"""#38 deskriptiv ankar-accuracy: väljer wick-par-detektorn samma A/B som facit?

Mäter — på daily BTC/USD-facit — om wick-par-väljaren träffar människans
``anchor_a``/``anchor_b`` minst lika bra som den befintliga pivot-kontrollen.
Två mått, båda återbrukade (ingen ny metrik):

- **Coverage** (``pivot_recall.evaluate_label_recall``, injicerad producer): ligger
  facit-high/low-baren i detektorns kandidat-universum?
- **Agreement** (``metrics.evaluate`` direkt): matchar detektorns valda A/B-par
  facit (price/time/fib-agreement)?

Kausalitet: ramen trunkeras till index ≤ B + k per facit (ingen framåtblick); både
kontroll och wick-par ser **samma** trunkerade ram. Deskriptivt — inget edge/PnL/
OOS-claim; små-N (N≈67) rapporteras varje gång.

Låst pre-reg: docs/research_wiki/reviews/btc-fib-daily-wick-pair-anchor-prereg-20260629.md

Kör:
    uv run --no-sync python -m fibengine.research.chamoun_wick_pair_accuracy \
        --config config/settings.expansion.yaml
"""

from __future__ import annotations

import argparse
import glob
import json
from datetime import UTC, datetime

import numpy as np

from fibengine.core.config import REPO_ROOT, Settings, load_settings
from fibengine.core.models import Swing
from fibengine.core.scoring import select_swing
from fibengine.data.loader import atr, load_candles
from fibengine.evaluation.bars import bar_of_timestamp
from fibengine.evaluation.metrics import evaluate
from fibengine.evaluation.pivot_recall import evaluate_label_recall
from fibengine.labeling.store import Point, SwingLabel
from fibengine.pivots.detect import detect_pivots
from fibengine.strategies.chamoun_daily_wick_pair import DEFAULT_WICK_FRAC, select_wick_pair

FACIT_GLOB = str(
    REPO_ROOT / "data" / "labels" / "human_fib" / "bitfinex" / "BTC-USD" / "1d" / "fib_*.json"
)
RESULTS = REPO_ROOT / "experiments" / "results" / "chamoun_wick_pair_accuracy.jsonl"


def _facit_to_label(payload: dict) -> SwingLabel:
    """anchor_a/anchor_b → SwingLabel(high, low) via pris (högre = high, lägre = low)."""
    a, b = payload["anchor_a"], payload["anchor_b"]
    top, bot = (a, b) if a["price"] >= b["price"] else (b, a)
    return SwingLabel(
        exchange=payload.get("exchange", "bitfinex"),
        symbol=payload.get("symbol", "BTC/USD"),
        timeframe=payload.get("timeframe", "1d"),
        high=Point(timestamp=top["time"], price=float(top["price"])),
        low=Point(timestamp=bot["time"], price=float(bot["price"])),
        source="human",
    )


def _atr_at(df, idx: int, period: int) -> float:
    series = atr(df, period)
    val = float(series.iloc[idx])
    if not np.isfinite(val) or val <= 0:
        val = float(np.nanmedian(series.to_numpy()))
    return val


def _agreement(settings: Settings, df, swing: Swing | None, label: SwingLabel) -> dict | None:
    if swing is None:
        return None
    atr_value = _atr_at(df, swing.end.index, settings.pivots.atr_period)
    return evaluate(df, swing, label, atr_value, settings.evaluation, settings)


def evaluate_facit(settings: Settings, payload: dict, k: int, wick_frac: float) -> dict:
    """Coverage + agreement för en facit-fil, kontroll vs wick-par på samma trunkerade ram."""
    label = _facit_to_label(payload)
    data_cfg = settings.data.model_copy(
        update={"exchange": label.exchange, "symbol": label.symbol, "timeframe": label.timeframe}
    )
    df = load_candles(data_cfg)

    # Kausal cut: index ≤ senaste ankarbar + k (B är endpoint = senaste i tid).
    hi_bar, hi_ok = bar_of_timestamp(df, label.high.timestamp)
    lo_bar, lo_ok = bar_of_timestamp(df, label.low.timestamp)
    b_bar = max(hi_bar, lo_bar)
    cut = min(len(df), b_bar + k + 1)

    def control_producer(frame):
        return detect_pivots(frame.iloc[:cut], settings.pivots)

    def wick_producer(frame):
        return select_wick_pair(frame.iloc[:cut], settings.pivots, wick_frac).candidates

    cov_control = evaluate_label_recall(settings, label, pivot_producer=control_producer)
    cov_wick = evaluate_label_recall(settings, label, pivot_producer=wick_producer)

    trunc = df.iloc[:cut]
    sel_control = select_swing(trunc, settings.pivots, settings.scoring)
    sel_wick = select_wick_pair(trunc, settings.pivots, wick_frac)

    return {
        "fib_id": payload.get("fib_id"),
        "in_window": bool(hi_ok and lo_ok),
        "n_bars_total": len(df),
        "cut": cut,
        "control": {
            "coverage": {k2: cov_control[k2] for k2 in ("high_hit", "low_hit", "both_hit")},
            "n_candidates": cov_control["n_pivots"],
            "agreement": _agreement(settings, df, sel_control, label),
        },
        "wick_pair": {
            "coverage": {k2: cov_wick[k2] for k2 in ("high_hit", "low_hit", "both_hit")},
            "n_candidates": cov_wick["n_pivots"],
            "agreement": _agreement(settings, df, sel_wick.swing, label),
            "selected": sel_wick.swing.to_dict() if sel_wick.swing else None,
            "audit": sel_wick.audit,
        },
    }


def _agg(rows: list[dict], arm: str) -> dict:
    usable = [r for r in rows if r["in_window"]]
    n = len(usable)
    if not n:
        return {"n": 0}
    both = sum(1 for r in usable if r[arm]["coverage"]["both_hit"]) / n
    agreements = [
        r[arm]["agreement"]["agreement"]
        for r in usable
        if r[arm]["agreement"] and r[arm]["agreement"].get("agreement") is not None
    ]
    n_pair = sum(1 for r in usable if r[arm]["agreement"] and r[arm]["agreement"].get("agreement"))
    return {
        "n": n,
        "both_hit_rate": round(both, 4),
        "n_pair_selected": n_pair,
        "mean_agreement": round(float(np.mean(agreements)), 4) if agreements else None,
        "median_agreement": round(float(np.median(agreements)), 4) if agreements else None,
    }


def run(config_path: str | None, k: int, wick_frac: float) -> dict:
    settings = load_settings(config_path)
    files = sorted(glob.glob(FACIT_GLOB))
    rows = [evaluate_facit(settings, json.loads(open(p).read()), k, wick_frac) for p in files]

    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    run_id = datetime.now(UTC).strftime("chamoun_wick_pair_%Y%m%dT%H%M%SZ")
    with RESULTS.open("a") as f:
        for r in rows:
            f.write(json.dumps({"run_id": run_id, "wick_frac": wick_frac, "k": k, **r}) + "\n")

    summary = {
        "run_id": run_id,
        "n_facit": len(files),
        "wick_frac": wick_frac,
        "k": k,
        "control": _agg(rows, "control"),
        "wick_pair": _agg(rows, "wick_pair"),
        "small_n_caveat": "Daily ar data-tunt (N~67); deskriptivt, inget edge/OOS-claim.",
    }
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=None, help="settings-yaml (default: config/settings.yaml)")
    ap.add_argument("--k", type=int, default=3, help="kausal bekräftelse-lag i barer (default 3)")
    ap.add_argument("--wick-frac", type=float, default=DEFAULT_WICK_FRAC, help="wick-tröskel")
    args = ap.parse_args()
    summary = run(args.config, args.k, args.wick_frac)
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

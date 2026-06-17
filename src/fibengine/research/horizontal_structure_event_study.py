"""B-1 — causal BTC horizontal-structure event study (research-only, Lean Fib Research).

Post-fib-null follow-up: does BTC price repel measurably more at **generic causal horizontal
levels** than at a matched **random-walk null**? Pre-registration (frozen rules, incl. the dated
§4/§8 amendments): `docs/research_wiki/reviews/btc-horizontal-structure-event-study-prereg-*.md`

**Behaviour only — no trading/edge claim, no Genesis touch, no 1H, no auto-fib, no label mutation,
no fib JSON read.** Every subject derives from candles alone. The primary control is the RW-null
(`synthetic_baseline`), the unseen quantity that legitimises this 3rd look; inference is
anytime-valid (`anytime_valid`: conditional 2×2 e-value + e-Holm), per prereg §8 (peeked window).

This module reuses the **frozen** event/outcome/split primitives from the closed behaviour study so
subjects and the RW-null are measured identically; it adds only level *generation* (prior-extreme,
RW-null) and the anytime-valid gate. ROUND (prereg §3 dynamic activity) lands in a later phase once
its §3/§4 cluster is pinned.

Run (ONLY after the prereg §12 execution gate is satisfied — separate explicit go):
    uv run python -m fibengine.research.horizontal_structure_event_study \\
        --timeframes 1M,1w,1d,4h --config config/settings.expansion.yaml
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from fibengine.core.config import REPO_ROOT, load_settings
from fibengine.data.loader import atr, load_candles
from fibengine.research.anytime_valid import (
    conditional_bernoulli_evalue,
    evalue_to_pvalue,
    holm_evalues,
)

# Deliberately reuse the FROZEN closed-study primitives (do not re-implement / do not mutate them).
from fibengine.research.fib_behaviour_event_study import (
    _TF_PARAMS,
    ALLOWED_TIMEFRAMES,
    EventStudyConfig,
    Level,
    _aggregate,  # noqa: F401  (re-exported for harness symmetry / tests)
    _collect_rows,
    _index_ns,
    detect_swing_levels,
    find_events,
    split_positions,
)
from fibengine.research.synthetic_baseline import random_walk_swing_levels

RESULTS_DIR = REPO_ROOT / "experiments" / "review" / "horizontal_structure_event_study"

# PRIOR-EXTREME mapping (prereg §4, frozen): the next-higher protocol TF supplies prior-period
# extremes. 1M is the ladder top → its own prior 12 completed monthly bars (the preceding year).
_HIGHER_TF = {"4h": "1d", "1d": "1w", "1w": "1M"}
_MONTHLY_PRIOR_BARS = 12


def _monthly_prior_levels(df_h: pd.DataFrame) -> list[Level]:
    """1M ladder top: rolling high/low over the prior 12 completed monthly bars (pure)."""
    highs, lows, idx = df_h["high"].to_numpy(), df_h["low"].to_numpy(), df_h.index
    levels: list[Level] = []
    for i in range(_MONTHLY_PRIOR_BARS, len(df_h)):
        known = pd.Timestamp(idx[i])  # prior 12 bars all completed by this bar's open
        levels.append(Level(known, float(highs[i - _MONTHLY_PRIOR_BARS : i].max())))
        levels.append(Level(known, float(lows[i - _MONTHLY_PRIOR_BARS : i].min())))
    return levels


def _higher_tf_prior_levels(df_h: pd.DataFrame, higher_tf: str) -> list[Level]:
    """Each completed higher-TF bar's high/low as a static level, known at its close (pure)."""
    dur = pd.Timedelta(seconds=_TF_PARAMS[higher_tf][2])
    levels: list[Level] = []
    for j in range(len(df_h)):
        close_t = pd.Timestamp(df_h.index[j]) + dur  # higher-TF bar is known at its close
        levels.append(Level(close_t, float(df_h["high"].iloc[j])))
        levels.append(Level(close_t, float(df_h["low"].iloc[j])))
    return levels


def prior_extreme_levels(timeframe: str, settings: Any) -> list[Level]:
    """Prior-period high/low as static causal levels, known at the prior period's close (§4)."""
    higher = "1M" if timeframe == "1M" else _HIGHER_TF[timeframe]
    df_h = load_candles(
        settings.data.model_copy(update={"timeframe": higher}), fetch_if_missing=False, strict=False
    )
    if timeframe == "1M":
        return _monthly_prior_levels(df_h)
    return _higher_tf_prior_levels(df_h, higher)


def rw_null_levels(
    subject_levels: list[Level],
    df: pd.DataFrame,
    cfg: EventStudyConfig,
    rng: np.random.Generator,
    timeframe: str,
) -> list[Level]:
    """RW-NULL matched to a subject (prereg §4 amendment): one seeded synthetic path per subject
    level, calibrated on real closes strictly before that level's ``known_after_ts``; take the
    path's MOST-RECENT swing, inherit the same ``known_after_ts``. Count is not forced (the
    conditional e-value handles n_s≠n_c); a path with no swing is skipped."""
    n_steps = _TF_PARAMS[timeframe][3]
    closes = df["close"].to_numpy()
    idx_ns = _index_ns(df)
    out: list[Level] = []
    for lv in subject_levels:
        hist = closes[idx_ns < lv.known_after_ts.value]
        if hist.size < 2:
            continue
        swings = random_walk_swing_levels(hist, n_steps, rng, pivot_k=cfg.pivot_k)
        if not swings:
            continue
        out.append(Level(lv.known_after_ts, swings[-1]))  # most-recent swing (unbiased temporally)
    return out


def _test_counts(rows: list[dict[str, Any]]) -> tuple[int, int]:
    """(rejects, n) over a window's outcome rows."""
    return int(sum(r["reject"] for r in rows)), len(rows)


def _subject_levels(timeframe: str, df: pd.DataFrame, cfg: EventStudyConfig, settings: Any) -> dict:
    """Generic horizontal-structure subjects for this slice (ROUND added once it is pinned)."""
    return {
        "swing": detect_swing_levels(df, cfg),
        "prior_extreme": prior_extreme_levels(timeframe, settings),
    }


def run_timeframe(timeframe: str, cfg: EventStudyConfig, settings: Any) -> dict[str, Any]:
    """Per-TF: each subject vs its matched RW-null, with test/train aggregates + the e-value."""
    if timeframe not in ALLOWED_TIMEFRAMES:
        raise ValueError(f"timeframe {timeframe!r} not allowed (1H is rejected fail-closed)")
    horizons, primary_h, _, _ = _TF_PARAMS[timeframe]
    max_h = max(horizons)
    df = load_candles(
        settings.data.model_copy(update={"timeframe": timeframe}),
        fetch_if_missing=False,
        strict=False,
    )
    if df.empty:
        raise ValueError(f"empty candle frame for {timeframe} — fail-closed")
    atr_s = atr(df, period=cfg.atr_period).to_numpy()
    rng = np.random.default_rng(cfg.seed)
    split_idx, n = split_positions(len(df), cfg.train_frac, max_h)

    out: dict[str, Any] = {"timeframe": timeframe, "n_bars": int(n), "subjects": {}}
    for name, levels in _subject_levels(timeframe, df, cfg, settings).items():
        null_levels = rw_null_levels(levels, df, cfg, rng, timeframe)
        subj = _collect_rows(
            df,
            atr_s,
            find_events(df, atr_s, levels, cfg, timeframe),
            primary_h,
            max_h,
            split_idx,
            cfg.react_eps,
        )
        null = _collect_rows(
            df,
            atr_s,
            find_events(df, atr_s, null_levels, cfg, timeframe),
            primary_h,
            max_h,
            split_idx,
            cfg.react_eps,
        )
        k_s, n_s = _test_counts(subj["_test_rows"])
        k_c, n_c = _test_counts(null["_test_rows"])
        out["subjects"][name] = {
            "n_levels": len(levels),
            "n_rw_null_levels": len(null_levels),
            "subject": {"train": subj["train"], "test": subj["test"]},
            "rw_null": {"train": null["train"], "test": null["test"]},
            "evalue": conditional_bernoulli_evalue(k_s, n_s, k_c, n_c),
            "test_counts": {"k_subject": k_s, "n_subject": n_s, "k_rw_null": k_c, "n_rw_null": n_c},
        }
    return out


def _gate(
    results: list[dict[str, Any]], cfg: EventStudyConfig, alpha: float = 0.05
) -> dict[str, Any]:
    """Pre-registered §9 robustness gate, with anytime-valid e-Holm across the subject×TF family."""
    evalues = {
        f"{name}-{r['timeframe']}": s["evalue"]
        for r in results
        for name, s in r["subjects"].items()
    }
    holm = holm_evalues(evalues, alpha)
    gate: dict[str, Any] = {}
    for r in results:
        for name, s in r["subjects"].items():
            key = f"{name}-{r['timeframe']}"
            st, sn = s["subject"]["test"], s["rw_null"]["test"]
            tr_s, tr_c = s["subject"]["train"]["reject_rate"], s["rw_null"]["train"]["reject_rate"]
            n_ok = st["n"] >= cfg.min_events and sn["n"] >= cfg.min_events
            beats_test = (
                st["reject_rate"] is not None
                and sn["reject_rate"] is not None
                and st["reject_rate"] > sn["reject_rate"]
            )
            same_sign_train = tr_s is not None and tr_c is not None and (tr_s - tr_c) > 0
            gate[key] = {
                "n_events_ge_min": n_ok,
                "beats_rw_null_test": beats_test,
                "same_sign_train": same_sign_train,
                "e_holm_significant": holm.get(key, False),
                "p_anytime_valid": evalue_to_pvalue(s["evalue"]),
                "robust": bool(n_ok and beats_test and same_sign_train and holm.get(key, False)),
            }
    return gate


def run_study(timeframes: list[str], config_path: str | None, cfg: EventStudyConfig) -> dict:
    settings = load_settings(config_path) if config_path else load_settings()
    results = [run_timeframe(tf, cfg, settings) for tf in timeframes]
    gate = _gate(results, cfg)
    return {
        "generated_by": "horizontal_structure_event_study",
        "seed": cfg.seed,
        "timeframes": timeframes,
        "results": results,
        "gate": gate,
        "any_robust": any(v["robust"] for v in gate.values()),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Causal BTC horizontal-structure event study (B-1)")
    ap.add_argument("--timeframes", default="1M,1w,1d,4h")
    ap.add_argument("--config", default="config/settings.expansion.yaml")
    ap.add_argument("--out", default=str(RESULTS_DIR))
    args = ap.parse_args(argv)
    tfs = [t.strip() for t in args.timeframes.split(",") if t.strip()]
    bad = [t for t in tfs if t not in ALLOWED_TIMEFRAMES]
    if bad:
        raise SystemExit(f"disallowed timeframe(s) {bad} (1H is rejected fail-closed)")
    report = run_study(tfs, args.config, EventStudyConfig())
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(report, indent=2, sort_keys=True), "utf-8")
    for key, g in report["gate"].items():
        print(f"[{key}] robust={g['robust']} p_av={g['p_anytime_valid']:.4g}")
    print(f"any_robust={report['any_robust']}  out={out_dir / 'summary.json'}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

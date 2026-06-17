"""MTF fib level projection — project locked HTF human fib onto LTF candles (research-only).

The human-drawn higher-timeframe (HTF) fib is the **locked map / source-of-truth**.
This runner reuses the *exact* human level prices and measures **lower-timeframe**
(LTF) candle behavior around those same prices, so a researcher can ask: when price
reaches an HTF human fib level, what does LTF candle behavior show around it?

Layers are kept strictly separate per row:

- ``human_fib``        — locked HTF map (``labeling.human_fib.load_annotation``; never mutated)
- ``projected_level``  — HTF fib level shown on LTF candles (``fib_level`` + ``fib_price``
                         + ``projected_from_timeframe``)
- ``relation``         — deterministic LTF geometry (``classify_candle`` on the LTF bar)
- ``fingerprint``      — measurable LTF behavior (``fib_level_fingerprints``)
- ``outcome``          — forward empirical result (``fib_candidate_outcomes``)

No auto-fib. No moved anchors. No relabeled human fib. Not a trading signal, buy/sell,
edge claim, ML, or optimized rule. ``auto_candidate`` stays a machine hypothesis on the
LTF interaction (needed only to infer outcome direction) and is never facit.

Run (first runnable slice — no network, 1W human fib -> 1D candles):
    uv run python -m fibengine.research.mtf_fib_level_projection \\
        --human-fib data/labels/human_fib/bitfinex/BTC-USD/1w/<fib_id>.json \\
        --lower-timeframes 1d \\
        --pre-bars 50 --post-bars 100 --horizons 5,10,20,50
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from fibengine.core.config import REPO_ROOT, Settings, load_settings
from fibengine.data.loader import atr, load_candles
from fibengine.labeling.human_fib import classify_candle, load_annotation
from fibengine.research.fib_candidate_outcomes import OutcomeConfig, analyze_events
from fibengine.research.fib_fingerprint_outcomes import (
    join_fingerprints_outcomes,
    summarize_joined,
)
from fibengine.research.fib_level_fingerprints import FingerprintConfig, extract_all
from fibengine.research.level_events import LevelEventConfig, _classify

MTF_RESULTS = REPO_ROOT / "experiments" / "results" / "mtf_fib_level_projection.jsonl"
MTF_RUNS = REPO_ROOT / "experiments" / "runs" / "mtf_fib_level_projection"


def _event_id(row: dict) -> str:
    """Match the shared key used by the fingerprint and outcome layers."""
    fid = row.get("fib_id", "fib")
    return f"{fid}|{row['fib_level']}|{row['event_bar']}|{row['auto_candidate']}"


def _scan_start_bar(df: pd.DataFrame, start_time: str) -> int | None:
    """First LTF bar strictly after the HTF leg end, or None if leg end is past cache."""
    ts = pd.to_datetime(start_time, utc=True)
    if ts > df.index[-1]:
        return None
    # searchsorted("right") => index just after any bar at/equal to ts (the leg-end bar);
    # if ts predates the cache this clamps to 0 (scan the whole loaded LTF window).
    return int(df.index.searchsorted(ts, side="right"))


def detect_ltf_level_interactions(
    df: pd.DataFrame,
    levels: list[dict],
    *,
    start_time: str,
    fib_id: str,
    symbol: str,
    timeframe: str,
    exchange: str,
    direction: str,
    projected_from_timeframe: str,
    level_cfg: LevelEventConfig | None = None,
    atr_period: int = 14,
    end_time: str | None = None,
) -> tuple[list[dict], str | None]:
    """Find LTF candle interactions with explicit HTF human level prices.

    Deterministic: for each human level price, scan LTF bars after the HTF leg end,
    debounce repeats, and emit one row per touch with ``approach_side``, ``relation``,
    ``touch_type`` and an ``auto_candidate`` (machine hypothesis, never facit). Rows are
    schema-compatible with :func:`extract_all` and :func:`analyze_events`.

    Returns ``(rows, skip_reason)``; ``skip_reason`` is set when no scan window exists.
    """
    cfg = level_cfg or LevelEventConfig()
    n = len(df)
    if n == 0:
        return [], "empty_candles"
    scan_start = _scan_start_bar(df, start_time)
    if scan_start is None:
        return [], "leg_end_after_cache"
    scan_start = max(scan_start, 1)  # need a previous bar to read approach side

    end_ts = pd.to_datetime(end_time, utc=True) if end_time else None
    end_bar = int(df.index.searchsorted(end_ts, side="right")) if end_ts is not None else n

    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()
    closes = df["close"].to_numpy()
    opens = df["open"].to_numpy()
    band = (cfg.touch_tolerance_atr * atr(df, atr_period)).to_numpy()
    timestamps = df.index

    rows: list[dict] = []
    for lvl in levels:
        ratio = float(lvl["ratio"])
        level_str = f"{ratio:g}"
        price = float(lvl["price"])
        gap_count = cfg.debounce_bars  # eligible for the first touch immediately

        for bar in range(scan_start, end_bar):
            touched = lows[bar] - band[bar] <= price <= highs[bar] + band[bar]
            if not touched:
                gap_count += 1
                continue
            if gap_count < cfg.debounce_bars:
                gap_count = 0
                continue
            gap_count = 0

            prev = bar - 1
            from_above = closes[prev] > price
            approach_side = "above" if from_above else "below"
            break_side = -1 if from_above else 1

            if closes[bar] >= price:
                touch_type = "wick_below" if lows[bar] < price - band[bar] else "close_above"
            else:
                touch_type = "wick_above" if highs[bar] > price + band[bar] else "close_below"

            last = min(bar + cfg.forward_window, n - 1)
            candidate, _evidence = _classify(closes, bar, last, price, band, break_side, cfg)
            relation = classify_candle(
                float(opens[bar]),
                float(highs[bar]),
                float(lows[bar]),
                float(closes[bar]),
                price,
            )
            row = {
                "fib_id": fib_id,
                "symbol": symbol,
                "timeframe": timeframe,
                "exchange": exchange,
                "swing_direction": direction,
                "fib_level": level_str,
                "fib_price": round(price, 6),
                "event_bar": int(bar),
                "event_time": timestamps[bar].isoformat(),
                "relation": relation,
                "auto_candidate": candidate,
                "approach_side": approach_side,
                "touch_type": touch_type,
                "projected_from_timeframe": projected_from_timeframe,
            }
            row["event_id"] = _event_id(row)
            rows.append(row)
    return rows, None


def _project_one(
    ann,
    ltf: str,
    *,
    settings: Settings,
    fingerprint_cfg: FingerprintConfig,
    outcome_cfg: OutcomeConfig,
    level_cfg: LevelEventConfig,
) -> dict[str, Any]:
    """Project one human fib annotation onto one LTF; returns interactions + joined rows."""
    out: dict[str, Any] = {
        "interactions": [],
        "joined": [],
        "unmatched": [],
        "skips": [],
        "fingerprint_skipped": 0,
        "outcome_skipped": 0,
    }
    data_cfg = settings.data.model_copy(
        update={"exchange": ann.exchange, "symbol": ann.symbol, "timeframe": ltf}
    )
    try:
        df = load_candles(data_cfg, fetch_if_missing=False)
    except FileNotFoundError as exc:
        out["skips"].append(
            {
                "fib_id": ann.fib_id,
                "symbol": ann.symbol,
                "projected_from_timeframe": ann.timeframe,
                "lower_timeframe": ltf,
                "reason": "missing_candle_cache",
                "detail": str(exc),
            }
        )
        return out

    levels = [{"ratio": lvl.ratio, "price": lvl.price} for lvl in ann.levels]
    rows, skip_reason = detect_ltf_level_interactions(
        df,
        levels,
        start_time=ann.anchor_b.time,
        fib_id=ann.fib_id,
        symbol=ann.symbol,
        timeframe=ltf,
        exchange=ann.exchange,
        direction=ann.direction,
        projected_from_timeframe=ann.timeframe,
        level_cfg=level_cfg,
        atr_period=fingerprint_cfg.atr_period,
    )
    if skip_reason is not None:
        out["skips"].append(
            {
                "fib_id": ann.fib_id,
                "symbol": ann.symbol,
                "projected_from_timeframe": ann.timeframe,
                "lower_timeframe": ltf,
                "reason": skip_reason,
                "detail": (
                    f"leg_end={ann.anchor_b.time} cache={df.index[0].date()}..{df.index[-1].date()}"
                ),
            }
        )
        return out

    out["interactions"] = rows
    df_cache = {(ann.exchange, ann.symbol, ltf): df}
    fingerprints, fp_skipped = extract_all(rows, df_cache, fingerprint_cfg)
    outcomes, oc_skipped = analyze_events(rows, df_cache, outcome_cfg)
    joined, unmatched = join_fingerprints_outcomes(fingerprints, outcomes)
    for jr in joined:
        jr["projected_from_timeframe"] = ann.timeframe
    out["joined"] = joined
    out["unmatched"] = unmatched
    out["fingerprint_skipped"] = len(fp_skipped)
    out["outcome_skipped"] = len(oc_skipped)
    return out


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def _write_summary_csv(path: Path, summary: list[dict]) -> None:
    if not summary:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)


def run_mtf_fib_level_projection(
    human_fib_paths: list[Path],
    lower_timeframes: list[str],
    *,
    settings: Settings | None = None,
    fingerprint_cfg: FingerprintConfig | None = None,
    outcome_cfg: OutcomeConfig | None = None,
    level_cfg: LevelEventConfig | None = None,
) -> dict[str, Any]:
    """Project locked HTF human fib levels onto LTF candles and write reproducible artifacts."""
    settings = settings or load_settings()
    fingerprint_cfg = fingerprint_cfg or FingerprintConfig()
    outcome_cfg = outcome_cfg or OutcomeConfig()
    level_cfg = level_cfg or LevelEventConfig()
    human_fib_paths = [Path(p) for p in human_fib_paths]
    lower_timeframes = list(lower_timeframes)
    if not human_fib_paths:
        raise ValueError("No human fib files provided")
    if not lower_timeframes:
        raise ValueError("No lower timeframes provided")

    run_id = datetime.now(UTC).strftime("mtf_proj_%Y%m%dT%H%M%SZ")
    run_date = datetime.now(UTC).strftime("%Y-%m-%d")
    run_dir = MTF_RUNS / run_date / run_id

    all_interactions: list[dict] = []
    all_joined: list[dict] = []
    all_unmatched: list[dict] = []
    skips: list[dict] = []
    fp_skipped = 0
    oc_skipped = 0
    projected_levels = 0
    htf_set: set[str] = set()

    for fib_path in human_fib_paths:
        ann = load_annotation(fib_path)
        htf_set.add(ann.timeframe)
        projected_levels += len(ann.levels) * len(lower_timeframes)
        for ltf in lower_timeframes:
            part = _project_one(
                ann,
                ltf,
                settings=settings,
                fingerprint_cfg=fingerprint_cfg,
                outcome_cfg=outcome_cfg,
                level_cfg=level_cfg,
            )
            all_interactions.extend(part["interactions"])
            all_joined.extend(part["joined"])
            all_unmatched.extend(part["unmatched"])
            skips.extend(part["skips"])
            fp_skipped += part["fingerprint_skipped"]
            oc_skipped += part["outcome_skipped"]

    for jr in all_joined:
        jr["run_id"] = run_id
    summary = summarize_joined(all_joined)

    config_doc = {
        "run_id": run_id,
        "lower_timeframes": lower_timeframes,
        "horizons": outcome_cfg.horizons,
        "pre_bars": fingerprint_cfg.pre_bars,
        "post_bars": fingerprint_cfg.post_bars,
        "atr_period": fingerprint_cfg.atr_period,
        "near_level_atr": fingerprint_cfg.near_level_atr,
        "touch_tolerance_atr": level_cfg.touch_tolerance_atr,
        "forward_window": level_cfg.forward_window,
        "debounce_bars": level_cfg.debounce_bars,
        "human_fib_files": [str(p) for p in human_fib_paths],
        "created_at": datetime.now(UTC).isoformat(),
    }
    run_summary = {
        **config_doc,
        "human_fibs": len(human_fib_paths),
        "projected_from_timeframes": sorted(htf_set),
        "projected_levels": projected_levels,
        "ltf_interactions": len(all_interactions),
        "joined_rows": len(all_joined),
        "joined_events": len({r["event_id"] for r in all_joined}),
        "unmatched": len(all_unmatched),
        "unmatched_reasons": dict(sorted(Counter(u["reason"] for u in all_unmatched).items())),
        "fingerprint_skipped": fp_skipped,
        "outcome_skipped": oc_skipped,
        "skipped": len(skips),
        "skipped_reasons": dict(sorted(Counter(s["reason"] for s in skips).items())),
        "ltf_timeframes_seen": sorted({r["timeframe"] for r in all_joined}),
    }

    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps(config_doc, indent=2), encoding="utf-8")
    _write_jsonl(run_dir / "interactions.jsonl", all_interactions)
    _write_jsonl(run_dir / "fingerprint_outcomes.jsonl", all_joined)
    _write_jsonl(run_dir / "unmatched.jsonl", all_unmatched)
    _write_jsonl(run_dir / "skipped.jsonl", skips)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_summary_csv(run_dir / "summary.csv", summary)
    (run_dir / "run_summary.json").write_text(json.dumps(run_summary, indent=2), encoding="utf-8")

    MTF_RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with MTF_RESULTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(run_summary, sort_keys=True) + "\n")

    return {**run_summary, "run_dir": str(run_dir)}


def _parse_horizons(raw: str) -> list[int]:
    parts = [int(x.strip()) for x in raw.split(",") if x.strip()]
    if not parts or any(p < 1 for p in parts):
        raise argparse.ArgumentTypeError("horizons must be comma-separated positive integers")
    return sorted(set(parts))


def _parse_timeframes(raw: str) -> list[str]:
    parts = [x.strip() for x in raw.split(",") if x.strip()]
    if not parts:
        raise argparse.ArgumentTypeError("lower-timeframes must be a comma-separated list")
    return parts


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Project locked HTF human fib levels onto LTF candles (research-only)."
    )
    p.add_argument(
        "--human-fib",
        action="append",
        default=[],
        dest="human_fib",
        type=Path,
        help="Base human fib JSON (<fib_id>.json, not *_events.json). Repeatable.",
    )
    p.add_argument(
        "--lower-timeframes",
        type=_parse_timeframes,
        default="1d",
        help="Comma-separated LTF list, e.g. 1d or 1d,4h. First slice: 1d only.",
    )
    p.add_argument("--pre-bars", type=int, default=50)
    p.add_argument("--post-bars", type=int, default=100)
    p.add_argument("--horizons", type=_parse_horizons, default="5,10,20,50")
    p.add_argument("--atr-period", type=int, default=14)
    p.add_argument(
        "--config",
        type=str,
        default="",
        help="Settings file (default: config/settings.yaml). Use to widen the LTF "
        "candle window without changing the global default.",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    paths = list(args.human_fib)
    if not paths:
        raise SystemExit("Provide --human-fib <path> (base human fib JSON, not *_events.json)")

    settings = load_settings(args.config or None)
    ltfs = args.lower_timeframes
    if isinstance(ltfs, str):  # default value not run through the type parser
        ltfs = _parse_timeframes(ltfs)
    horizons = args.horizons
    if isinstance(horizons, str):
        horizons = _parse_horizons(horizons)

    result = run_mtf_fib_level_projection(
        paths,
        ltfs,
        settings=settings,
        fingerprint_cfg=FingerprintConfig(
            pre_bars=args.pre_bars,
            post_bars=args.post_bars,
            atr_period=args.atr_period,
        ),
        outcome_cfg=OutcomeConfig(horizons=horizons),
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

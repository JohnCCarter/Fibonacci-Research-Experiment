"""Join fib level fingerprints (#23) with forward outcomes (#22) — research-only.

Combines the deterministic interaction fingerprint (pre/at/post) and the forward
outcome metrics for the *same* events, keyed on ``event_id``. Lets a researcher
ask, deterministically: which measurable fingerprints co-occur with which forward
outcomes, grouped by candidate / relation / level / timeframe / horizon.

Not trading logic. Not ML. No edge claims. No candidate-logic changes — this only
merges two existing research layers into one reproducible table.

Run:
    uv run python -m fibengine.research.fib_fingerprint_outcomes \\
        --events data/labels/human_fib/bitfinex/BTC-USD/1d/<fib_id>_events.json \\
        --horizons 5,10,20,50 --pre-bars 20 --post-bars 50
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from fibengine.core.config import REPO_ROOT, Settings, load_settings
from fibengine.data.loader import load_candles
from fibengine.research.fib_candidate_outcomes import (
    OutcomeConfig,
    analyze_events,
    discover_human_fib_event_files,
)
from fibengine.research.fib_level_fingerprints import (
    FingerprintConfig,
    extract_all,
)
from fibengine.research.human_review_level_events import (
    collect_human_fib_event_candidates,
)

JOIN_RESULTS = REPO_ROOT / "experiments" / "results" / "fib_fingerprint_outcomes.jsonl"
JOIN_RUNS = REPO_ROOT / "experiments" / "runs" / "fib_fingerprint_outcomes"

# Outcome-only metric fields carried into the joined row (identity keys are shared
# with the fingerprint and merged without duplication).
_OUTCOME_METRIC_KEYS = (
    "horizon",
    "forward_return",
    "mfe",
    "mae",
    "direction_inferred",
    "expected_direction",
    "close_on_approach_side",
    "close_on_break_side",
    "crossed_back",
    "stayed_on_break_side",
    "distance_from_level",
    "bars_available",
)

# Fingerprint numeric fields summarized alongside outcomes.
_FINGERPRINT_SUMMARY_KEYS = (
    "pre_bars_approaching_level",
    "pre_distance_atr_norm",
    "pre_approach_choppiness",
    "at_wick_through_level",
    "at_close_distance_atr_norm",
    "post_bars_on_break_side",
    "post_retest_count",
    "post_remained_near_level_rate",
)


def join_fingerprints_outcomes(
    fingerprints: list[dict],
    outcomes: list[dict],
) -> tuple[list[dict], list[dict]]:
    """Join on ``event_id``: one fingerprint × many outcome horizons.

    Returns ``(joined_rows, unmatched)``. Identity keys shared by both layers are
    kept once; outcome metric fields (incl. ``horizon``) are added per row.
    """
    fp_by_id = {fp["event_id"]: fp for fp in fingerprints}
    outcome_ids: set[str] = set()
    joined: list[dict] = []
    unmatched: list[dict] = []

    for oc in outcomes:
        eid = oc["event_id"]
        outcome_ids.add(eid)
        fp = fp_by_id.get(eid)
        if fp is None:
            unmatched.append({"event_id": eid, "reason": "outcome_without_fingerprint"})
            continue
        row = {k: v for k, v in fp.items() if k != "run_id"}
        for k in _OUTCOME_METRIC_KEYS:
            if k in oc:
                row[k] = oc[k]
        joined.append(row)

    for fp in fingerprints:
        if fp["event_id"] not in outcome_ids:
            unmatched.append({"event_id": fp["event_id"], "reason": "fingerprint_without_outcome"})

    return joined, unmatched


def _mean(values: list[float]) -> float | None:
    return round(statistics.mean(values), 6) if values else None


def _rate(flags: list[bool]) -> float | None:
    if not flags:
        return None
    return round(sum(1 for f in flags if f) / len(flags), 4)


def summarize_joined(joined: list[dict]) -> list[dict]:
    """Group joined rows by candidate/relation/level/timeframe/horizon.

    Reports outcome means/rates next to fingerprint means so a researcher can see
    which fingerprints co-occur with which forward outcomes per candidate.
    """
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for row in joined:
        key = (
            row.get("auto_candidate", ""),
            row.get("relation", ""),
            row.get("fib_level", ""),
            row.get("timeframe", ""),
            row.get("horizon"),
        )
        buckets[key].append(row)

    summary: list[dict] = []
    for key, rows in sorted(buckets.items(), key=lambda kv: tuple(str(x) for x in kv[0])):
        candidate, relation, level, tf, horizon = key
        returns = [r["forward_return"] for r in rows if r.get("forward_return") is not None]
        mfes = [r["mfe"] for r in rows if r.get("mfe") is not None]
        maes = [r["mae"] for r in rows if r.get("mae") is not None]
        approach_flags = [
            r["close_on_approach_side"] for r in rows if r.get("close_on_approach_side") is not None
        ]
        crossed_flags = [r["crossed_back"] for r in rows if r.get("crossed_back") is not None]
        entry: dict[str, Any] = {
            "auto_candidate": candidate,
            "relation": relation,
            "fib_level": level,
            "timeframe": tf,
            "horizon": horizon,
            "n_events": len(rows),
            "mean_forward_return": _mean(returns),
            "mean_mfe": _mean(mfes),
            "mean_mae": _mean(maes),
            "rate_close_on_approach_side": _rate(approach_flags),
            "rate_crossed_back": _rate(crossed_flags),
        }
        for fk in _FINGERPRINT_SUMMARY_KEYS:
            vals = [r[fk] for r in rows if r.get(fk) is not None]
            entry[f"mean_{fk}"] = _mean(vals)
        summary.append(entry)
    return summary


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


def run_fib_fingerprint_outcomes(
    event_paths: list[Path],
    *,
    settings: Settings | None = None,
    fingerprint_cfg: FingerprintConfig | None = None,
    outcome_cfg: OutcomeConfig | None = None,
    skip_out_of_range: bool = False,
) -> dict[str, Any]:
    """Extract fingerprints + outcomes for the same events and join them."""
    settings = settings or load_settings()
    fingerprint_cfg = fingerprint_cfg or FingerprintConfig()
    outcome_cfg = outcome_cfg or OutcomeConfig()
    event_paths = [Path(p) for p in event_paths]
    if not event_paths:
        raise ValueError("No event files provided")

    run_id = datetime.now(UTC).strftime("fp_outcomes_%Y%m%dT%H%M%SZ")
    run_date = datetime.now(UTC).strftime("%Y-%m-%d")
    run_dir = JOIN_RUNS / run_date / run_id

    rows, load_skips = collect_human_fib_event_candidates(
        event_paths, settings, skip_out_of_range=skip_out_of_range
    )
    df_cache: dict[tuple[str, str, str], pd.DataFrame] = {}
    for row in rows:
        key = (
            row.get("exchange", settings.data.exchange),
            row["symbol"],
            row["timeframe"],
        )
        if key not in df_cache:
            data_cfg = settings.data.model_copy(
                update={"exchange": key[0], "symbol": key[1], "timeframe": key[2]}
            )
            df_cache[key] = load_candles(data_cfg, fetch_if_missing=False)

    fingerprints, fp_skipped = extract_all(rows, df_cache, fingerprint_cfg)
    outcomes, oc_skipped = analyze_events(rows, df_cache, outcome_cfg)
    joined, unmatched = join_fingerprints_outcomes(fingerprints, outcomes)
    for row in joined:
        row["run_id"] = run_id
    summary = summarize_joined(joined)

    config_doc = {
        "run_id": run_id,
        "horizons": outcome_cfg.horizons,
        "pre_bars": fingerprint_cfg.pre_bars,
        "post_bars": fingerprint_cfg.post_bars,
        "atr_period": fingerprint_cfg.atr_period,
        "near_level_atr": fingerprint_cfg.near_level_atr,
        "event_files": [str(p) for p in event_paths],
        "created_at": datetime.now(UTC).isoformat(),
    }
    run_summary = {
        **config_doc,
        "events_input": len(rows),
        "fingerprints_extracted": len(fingerprints),
        "outcome_rows": len(outcomes),
        "joined_rows": len(joined),
        "joined_events": len({r["event_id"] for r in joined}),
        "unmatched": len(unmatched),
        "unmatched_reasons": dict(sorted(Counter(u["reason"] for u in unmatched).items())),
        "load_skipped": len(load_skips),
        "fingerprint_skipped": len(fp_skipped),
        "outcome_skipped": len(oc_skipped),
        "timeframes_seen": sorted({r["timeframe"] for r in joined}),
    }

    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps(config_doc, indent=2), encoding="utf-8")
    _write_jsonl(run_dir / "fingerprint_outcomes.jsonl", joined)
    _write_jsonl(run_dir / "unmatched.jsonl", unmatched)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_summary_csv(run_dir / "summary.csv", summary)
    (run_dir / "run_summary.json").write_text(json.dumps(run_summary, indent=2), encoding="utf-8")

    JOIN_RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with JOIN_RESULTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(run_summary, sort_keys=True) + "\n")

    return {**run_summary, "run_dir": str(run_dir)}


def _parse_horizons(raw: str) -> list[int]:
    parts = [int(x.strip()) for x in raw.split(",") if x.strip()]
    if not parts or any(p < 1 for p in parts):
        raise argparse.ArgumentTypeError("horizons must be comma-separated positive integers")
    return sorted(set(parts))


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Join fib level fingerprints (#23) with forward outcomes (#22), research-only."
    )
    p.add_argument("--events", action="append", default=[], dest="event_files", type=Path)
    p.add_argument("--all-human-fib-events", action="store_true")
    p.add_argument("--horizons", type=_parse_horizons, default="5,10,20,50")
    p.add_argument("--pre-bars", type=int, default=20)
    p.add_argument("--post-bars", type=int, default=50)
    p.add_argument("--atr-period", type=int, default=14)
    p.add_argument(
        "--config",
        type=str,
        default="",
        help="Settings file (default: config/settings.yaml). Use to widen the "
        "candle data window for data expansion without changing the global default.",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    if args.all_human_fib_events:
        paths = discover_human_fib_event_files()
    else:
        paths = list(args.event_files)
    if not paths:
        raise SystemExit("Provide --events <path> or --all-human-fib-events")

    settings = load_settings(args.config or None)
    result = run_fib_fingerprint_outcomes(
        paths,
        settings=settings,
        fingerprint_cfg=FingerprintConfig(
            pre_bars=args.pre_bars,
            post_bars=args.post_bars,
            atr_period=args.atr_period,
        ),
        outcome_cfg=OutcomeConfig(horizons=args.horizons),
        skip_out_of_range=args.all_human_fib_events,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

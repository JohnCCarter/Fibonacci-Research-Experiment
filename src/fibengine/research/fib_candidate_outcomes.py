"""Forward outcome analysis for machine-generated fib level candidates (research-only, #22).

Human fib JSON is locked source-of-truth. This module tests whether ``*_candidate``
labels from saved ``*_events.json`` files correlate with measurable forward price
behavior — not a trading strategy and not an edge claim.

Run:
    uv run python -m fibengine.research.fib_candidate_outcomes \\
        --events data/labels/human_fib/bitfinex/BTC-USD/1d/<fib_id>_events.json \\
        --horizons 5,10,20,50
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from fibengine.core.config import REPO_ROOT, Settings, load_settings
from fibengine.data.loader import load_candles
from fibengine.research.human_review_level_events import (
    collect_human_fib_event_candidates,
)

FIB_OUTCOMES_RESULTS = REPO_ROOT / "experiments" / "results" / "fib_candidate_outcomes.jsonl"
FIB_OUTCOMES_RUNS = REPO_ROOT / "experiments" / "runs" / "fib_candidate_outcomes"


class OutcomeConfig(BaseModel):
    """Research-only config for candidate outcome backtest (#22)."""

    horizons: list[int] = Field(default_factory=lambda: [5, 10, 20, 50])
    seed: int | None = None


@dataclass
class SkippedEvent:
    event_id: str
    reason: str
    fib_id: str = ""
    symbol: str = ""
    timeframe: str = ""


@dataclass
class OutcomeMetrics:
    horizon: int
    forward_return: float | None
    mfe: float | None
    mae: float | None
    direction_inferred: bool
    close_on_approach_side: bool | None
    close_on_break_side: bool | None
    crossed_back: bool | None
    stayed_on_break_side: bool | None
    distance_from_level: float | None
    bars_available: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "horizon": self.horizon,
            "forward_return": self.forward_return,
            "mfe": self.mfe,
            "mae": self.mae,
            "direction_inferred": self.direction_inferred,
            "close_on_approach_side": self.close_on_approach_side,
            "close_on_break_side": self.close_on_break_side,
            "crossed_back": self.crossed_back,
            "stayed_on_break_side": self.stayed_on_break_side,
            "distance_from_level": self.distance_from_level,
            "bars_available": self.bars_available,
        }


def expected_direction(candidate: str, approach_side: str | None) -> str | None:
    """Infer favorable price direction from candidate + approach side, or None if ambiguous."""
    if approach_side not in ("above", "below"):
        return None
    if candidate == "continuation_candidate":
        return "down" if approach_side == "above" else "up"
    if candidate in ("rejection_candidate", "failure_candidate"):
        return "up" if approach_side == "above" else "down"
    if candidate == "reaction_candidate":
        return None
    return None


def _on_approach_side(close: float, level: float, approach_side: str) -> bool:
    return close > level if approach_side == "above" else close < level


def _on_break_side(close: float, level: float, approach_side: str) -> bool:
    return not _on_approach_side(close, level, approach_side)


def compute_outcomes(
    df: pd.DataFrame,
    *,
    event_bar: int,
    fib_price: float,
    auto_candidate: str,
    approach_side: str | None,
    horizons: list[int],
) -> dict[int, OutcomeMetrics]:
    """Compute forward outcome metrics for one event at each horizon."""
    n = len(df)
    eb = int(event_bar)
    if eb < 0 or eb >= n:
        return {}
    event_close = float(df["close"].iloc[eb])
    exp_dir = expected_direction(auto_candidate, approach_side)
    direction_inferred = exp_dir is not None
    results: dict[int, OutcomeMetrics] = {}

    for horizon in horizons:
        end_bar = min(n - 1, eb + horizon)
        bars_available = end_bar - eb
        if bars_available <= 0:
            results[horizon] = OutcomeMetrics(
                horizon=horizon,
                forward_return=None,
                mfe=None,
                mae=None,
                direction_inferred=direction_inferred,
                close_on_approach_side=None,
                close_on_break_side=None,
                crossed_back=None,
                stayed_on_break_side=None,
                distance_from_level=None,
                bars_available=0,
            )
            continue

        forward_slice = df.iloc[eb + 1 : end_bar + 1]
        horizon_close = float(df["close"].iloc[end_bar])
        forward_return = (horizon_close - event_close) / event_close if event_close else None

        if not forward_slice.empty:
            max_high = float(forward_slice["high"].max())
            min_low = float(forward_slice["low"].min())
            if exp_dir == "up":
                mfe = (max_high - event_close) / event_close
                mae = (event_close - min_low) / event_close
            elif exp_dir == "down":
                mfe = (event_close - min_low) / event_close
                mae = (max_high - event_close) / event_close
            else:
                up_move = (max_high - event_close) / event_close
                down_move = (event_close - min_low) / event_close
                mfe = max(up_move, down_move)
                mae = max(up_move, down_move)
        else:
            mfe = mae = None

        close_on_approach = close_on_break = crossed_back = stayed_on_break = None
        if approach_side in ("above", "below"):
            close_on_approach = _on_approach_side(horizon_close, fib_price, approach_side)
            close_on_break = _on_break_side(horizon_close, fib_price, approach_side)
            start_on_break = _on_break_side(event_close, fib_price, approach_side)
            stayed_on_break = close_on_break if start_on_break else None
            sides = [
                _on_approach_side(float(c), fib_price, approach_side)
                for c in forward_slice["close"]
            ]
            if sides:
                crossed_back = any(sides) and any(not s for s in sides)

        distance_from_level = abs(horizon_close - fib_price)

        results[horizon] = OutcomeMetrics(
            horizon=horizon,
            forward_return=(round(forward_return, 6) if forward_return is not None else None),
            mfe=round(mfe, 6) if mfe is not None else None,
            mae=round(mae, 6) if mae is not None else None,
            direction_inferred=direction_inferred,
            close_on_approach_side=close_on_approach,
            close_on_break_side=close_on_break,
            crossed_back=crossed_back,
            stayed_on_break_side=stayed_on_break,
            distance_from_level=round(distance_from_level, 6),
            bars_available=bars_available,
        )
    return results


def _event_id(row: dict) -> str:
    fid = row.get("fib_id", "fib")
    return f"{fid}|{row['fib_level']}|{row['event_bar']}|{row['auto_candidate']}"


def analyze_events(
    rows: list[dict],
    df_cache: dict[tuple[str, str, str], pd.DataFrame],
    cfg: OutcomeConfig,
) -> tuple[list[dict], list[SkippedEvent]]:
    """Build per-event per-horizon outcome rows; skip when data is insufficient."""
    outcomes: list[dict] = []
    skipped: list[SkippedEvent] = []

    for row in rows:
        eid = _event_id(row)
        key = (row.get("exchange", ""), row["symbol"], row["timeframe"])
        df = df_cache.get(key)
        if df is None:
            skipped.append(
                SkippedEvent(
                    eid,
                    "missing_candles",
                    row.get("fib_id", ""),
                    row["symbol"],
                    row["timeframe"],
                )
            )
            continue

        eb = int(row["event_bar"])
        if eb < 0 or eb >= len(df):
            skipped.append(
                SkippedEvent(
                    eid,
                    "event_bar_out_of_range",
                    row.get("fib_id", ""),
                    row["symbol"],
                    row["timeframe"],
                )
            )
            continue
        if eb + 1 >= len(df):
            skipped.append(
                SkippedEvent(
                    eid,
                    "no_forward_bars",
                    row.get("fib_id", ""),
                    row["symbol"],
                    row["timeframe"],
                )
            )
            continue

        metrics = compute_outcomes(
            df,
            event_bar=eb,
            fib_price=float(row["fib_price"]),
            auto_candidate=row["auto_candidate"],
            approach_side=row.get("approach_side"),
            horizons=cfg.horizons,
        )
        if not metrics or all(m.bars_available == 0 for m in metrics.values()):
            skipped.append(
                SkippedEvent(
                    eid,
                    "insufficient_forward_bars",
                    row.get("fib_id", ""),
                    row["symbol"],
                    row["timeframe"],
                )
            )
            continue

        base = {
            "event_id": eid,
            "fib_id": row.get("fib_id", ""),
            "symbol": row["symbol"],
            "timeframe": row["timeframe"],
            "exchange": row.get("exchange", ""),
            "fib_level": row["fib_level"],
            "fib_price": row["fib_price"],
            "relation": row.get("relation", ""),
            "auto_candidate": row["auto_candidate"],
            "approach_side": row.get("approach_side", ""),
            "touch_type": row.get("touch_type", ""),
            "event_bar": eb,
            "event_time": row.get("event_time", ""),
            "expected_direction": expected_direction(
                row["auto_candidate"], row.get("approach_side")
            ),
        }
        for _horizon, m in metrics.items():
            outcomes.append({**base, **m.to_dict()})

    return outcomes, skipped


def _mean(values: list[float]) -> float | None:
    return round(statistics.mean(values), 6) if values else None


def _rate(flags: list[bool]) -> float | None:
    if not flags:
        return None
    return round(sum(1 for f in flags if f) / len(flags), 4)


def summarize_outcomes(outcomes: list[dict]) -> list[dict]:
    """Aggregate outcome rows by candidate, relation, level, symbol, timeframe, horizon."""
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for row in outcomes:
        key = (
            row["auto_candidate"],
            row.get("relation", ""),
            row["fib_level"],
            row["symbol"],
            row["timeframe"],
            row["horizon"],
        )
        buckets[key].append(row)

    summary: list[dict] = []
    for key, rows in sorted(buckets.items()):
        candidate, relation, level, symbol, tf, horizon = key
        returns = [r["forward_return"] for r in rows if r.get("forward_return") is not None]
        mfes = [r["mfe"] for r in rows if r.get("mfe") is not None]
        maes = [r["mae"] for r in rows if r.get("mae") is not None]
        approach_flags = [
            r["close_on_approach_side"] for r in rows if r.get("close_on_approach_side") is not None
        ]
        crossed_flags = [r["crossed_back"] for r in rows if r.get("crossed_back") is not None]
        summary.append(
            {
                "auto_candidate": candidate,
                "relation": relation,
                "fib_level": level,
                "symbol": symbol,
                "timeframe": tf,
                "horizon": horizon,
                "n_events": len(rows),
                "mean_forward_return": _mean(returns),
                "mean_mfe": _mean(mfes),
                "mean_mae": _mean(maes),
                "rate_close_on_approach_side": _rate(approach_flags),
                "rate_crossed_back": _rate(crossed_flags),
            }
        )
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


def discover_human_fib_event_files(root: Path | None = None) -> list[Path]:
    """Find all ``*_events.json`` under human_fib labels."""
    base = root or (REPO_ROOT / "data" / "labels" / "human_fib")
    return sorted(base.rglob("*_events.json"))


def run_fib_candidate_outcomes(
    event_paths: list[Path],
    *,
    settings: Settings | None = None,
    cfg: OutcomeConfig | None = None,
    skip_out_of_range: bool = False,
) -> dict[str, Any]:
    """Run outcome analysis and write reproducible artifacts under experiments/."""
    settings = settings or load_settings()
    cfg = cfg or OutcomeConfig()
    event_paths = [Path(p) for p in event_paths]
    if not event_paths:
        raise ValueError("No event files provided")

    run_id = datetime.now(UTC).strftime("outcomes_%Y%m%dT%H%M%SZ")
    run_date = datetime.now(UTC).strftime("%Y-%m-%d")
    run_dir = FIB_OUTCOMES_RUNS / run_date / run_id

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

    outcomes, skipped = analyze_events(rows, df_cache, cfg)
    for row in outcomes:
        row["run_id"] = run_id
    summary = summarize_outcomes(outcomes)

    config_doc = {
        "run_id": run_id,
        "horizons": cfg.horizons,
        "seed": cfg.seed,
        "event_files": [str(p) for p in event_paths],
        "created_at": datetime.now(UTC).isoformat(),
    }
    run_summary = {
        **config_doc,
        "events_input": len(rows),
        "events_tested": len({o["event_id"] for o in outcomes}),
        "outcome_rows": len(outcomes),
        "events_skipped": len(skipped),
        "load_skipped": len(load_skips),
        "skipped_reasons": dict(sorted(Counter(s.reason for s in skipped).items())),
        "load_skip_reasons": dict(sorted(Counter(s["reason"] for s in load_skips).items())),
    }

    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps(config_doc, indent=2), encoding="utf-8")
    _write_jsonl(run_dir / "event_outcomes.jsonl", outcomes)
    _write_jsonl(
        run_dir / "skipped_events.jsonl",
        [s.__dict__ for s in skipped] + load_skips,
    )
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_summary_csv(run_dir / "summary.csv", summary)
    (run_dir / "run_summary.json").write_text(json.dumps(run_summary, indent=2), encoding="utf-8")

    FIB_OUTCOMES_RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with FIB_OUTCOMES_RESULTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(run_summary, sort_keys=True) + "\n")

    return {**run_summary, "run_dir": str(run_dir)}


def _parse_horizons(raw: str) -> list[int]:
    parts = [int(x.strip()) for x in raw.split(",") if x.strip()]
    if not parts or any(p < 1 for p in parts):
        raise argparse.ArgumentTypeError("horizons must be comma-separated positive integers")
    return sorted(set(parts))


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Forward outcome analysis for fib level event candidates (research-only, #22)."
    )
    p.add_argument(
        "--events",
        action="append",
        default=[],
        dest="event_files",
        type=Path,
        help="Human-fib *_events.json file (repeatable).",
    )
    p.add_argument(
        "--all-human-fib-events",
        action="store_true",
        help="Scan data/labels/human_fib for all *_events.json files.",
    )
    p.add_argument("--horizons", type=_parse_horizons, default="5,10,20,50")
    p.add_argument("--seed", type=int, default=None)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    if args.all_human_fib_events:
        paths = discover_human_fib_event_files()
    else:
        paths = list(args.event_files)
    if not paths:
        raise SystemExit("Provide --events <path> or --all-human-fib-events")

    result = run_fib_candidate_outcomes(
        paths,
        cfg=OutcomeConfig(horizons=args.horizons, seed=args.seed),
        skip_out_of_range=args.all_human_fib_events,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

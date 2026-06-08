"""Deterministic level-interaction fingerprints for human-fib events (research-only, #23).

Extracts measurable pre/at/post behavior around each machine-detected fib level
event. Complements :mod:`fib_candidate_outcomes` (candidate → outcome) with a
lower-level feature layer (fingerprint → outcome). Not trading logic; not edge.

Run:
    uv run python -m fibengine.research.fib_level_fingerprints \\
        --events data/labels/human_fib/bitfinex/BTC-USD/1d/<fib_id>_events.json \\
        --pre-bars 20 --post-bars 50
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel, Field

from fibengine.core.config import REPO_ROOT, Settings, load_settings
from fibengine.data.loader import atr, load_candles
from fibengine.labeling.human_fib import classify_candle
from fibengine.research.fib_candidate_outcomes import discover_human_fib_event_files
from fibengine.research.human_review_level_events import (
    collect_human_fib_event_candidates,
)

FIB_FINGERPRINTS_RESULTS = REPO_ROOT / "experiments" / "results" / "fib_level_fingerprints.jsonl"
FIB_FINGERPRINTS_RUNS = REPO_ROOT / "experiments" / "runs" / "fib_level_fingerprints"


class FingerprintConfig(BaseModel):
    """Research-only config for level-interaction fingerprint extraction (#23)."""

    pre_bars: int = Field(default=20, ge=1)
    post_bars: int = Field(default=50, ge=1)
    atr_period: int = Field(default=14, ge=1)
    near_level_atr: float = Field(default=0.25, gt=0.0)


@dataclass
class SkippedFingerprint:
    event_id: str
    reason: str
    fib_id: str = ""
    symbol: str = ""
    timeframe: str = ""


def _round6(value: float | None) -> float | None:
    return round(value, 6) if value is not None and not math.isnan(value) else None


def _side_of(close: float, level: float) -> str:
    if close > level:
        return "above"
    if close < level:
        return "below"
    return "at"


def _break_side(approach_side: str) -> str:
    return "below" if approach_side == "above" else "above"


def _on_side(price: float, level: float, side: str) -> bool:
    if side == "above":
        return price > level
    if side == "below":
        return price < level
    return abs(price - level) < 1e-12


def _mean_body(df: pd.DataFrame, start: int, end: int) -> float:
    sl = df.iloc[max(0, start) : end + 1]
    if sl.empty:
        return 0.0
    return float((sl["close"] - sl["open"]).abs().mean())


def _direction_label(delta: float, ref: float, threshold: float = 0.001) -> str:
    if ref == 0:
        return "sideways"
    ratio = delta / ref
    if ratio > threshold:
        return "up"
    if ratio < -threshold:
        return "down"
    return "sideways"


def _event_id(row: dict) -> str:
    fid = row.get("fib_id", "fib")
    return f"{fid}|{row['fib_level']}|{row['event_bar']}|{row['auto_candidate']}"


def extract_pre_features(
    df: pd.DataFrame,
    atr_series: pd.Series,
    *,
    event_bar: int,
    level: float,
    approach_side: str,
    pre_bars: int,
) -> dict[str, Any]:
    """Approach behavior before the event bar."""
    eb = int(event_bar)
    start = max(0, eb - pre_bars)
    pre_slice = df.iloc[start:eb]
    out: dict[str, Any] = {
        "pre_bars_available": len(pre_slice),
        "pre_approach_side": (approach_side if approach_side in ("above", "below") else None),
    }
    if pre_slice.empty or approach_side not in ("above", "below"):
        return out

    first_close = float(pre_slice["close"].iloc[0])
    last_close = float(pre_slice["close"].iloc[-1])
    delta = last_close - first_close
    out["pre_approach_direction"] = _direction_label(delta, first_close)
    out["pre_distance_traveled"] = _round6(abs(last_close - first_close))
    span = max(1, len(pre_slice) - 1)
    out["pre_approach_slope"] = _round6(delta / span / last_close if last_close else None)

    bars_approaching = 0
    for i in range(eb - 1, start - 1, -1):
        if _on_side(float(df["close"].iloc[i]), level, approach_side):
            bars_approaching += 1
        else:
            break
    out["pre_bars_approaching_level"] = bars_approaching

    bodies = (pre_slice["close"] - pre_slice["open"]).abs()
    net_move = abs(float(pre_slice["close"].iloc[-1] - pre_slice["close"].iloc[0])) or 1e-12
    path = float(pre_slice["close"].diff().abs().sum()) or 0.0
    out["pre_approach_choppiness"] = _round6(path / net_move if net_move else None)

    atr_val = float(atr_series.iloc[eb]) if eb < len(atr_series) else None
    if atr_val and atr_val > 0:
        out["pre_distance_atr_norm"] = _round6(abs(last_close - first_close) / atr_val)
    else:
        out["pre_distance_atr_norm"] = None

    event_body = abs(float(df["close"].iloc[eb]) - float(df["open"].iloc[eb]))
    mean_body = float(bodies.mean()) if not bodies.empty else 0.0
    out["pre_body_expansion_ratio"] = _round6(event_body / mean_body if mean_body > 1e-12 else None)
    out["pre_impulse_like"] = (
        out["pre_approach_choppiness"] is not None
        and out["pre_approach_choppiness"] < 1.5
        and out["pre_approach_direction"] in ("up", "down")
    )
    return out


def extract_at_features(
    df: pd.DataFrame,
    atr_series: pd.Series,
    *,
    event_bar: int,
    level: float,
    row: dict,
) -> dict[str, Any]:
    """Contact behavior on the event bar."""
    eb = int(event_bar)
    o = float(df["open"].iloc[eb])
    h = float(df["high"].iloc[eb])
    low = float(df["low"].iloc[eb])
    c = float(df["close"].iloc[eb])
    relation = row.get("relation") or classify_candle(o, h, low, c, level)
    touch_type = row.get("touch_type", "")

    body = abs(c - o)
    recent_mean = _mean_body(df, max(0, eb - 10), eb - 1)
    wick_up = h - max(o, c)
    wick_down = min(o, c) - low

    penetration_up = max(0.0, h - level)
    penetration_down = max(0.0, level - low)
    wick_through = max(penetration_up, penetration_down)

    approach_side = row.get("approach_side", "")
    break_side = _break_side(approach_side) if approach_side in ("above", "below") else ""
    intrabar_cross_no_accept = relation == "cross" and (
        break_side and not _on_side(c, level, break_side)
    )

    atr_val = float(atr_series.iloc[eb]) if eb < len(atr_series) else None

    return {
        "at_relation": relation,
        "at_touch_type": touch_type,
        "at_wick_touch": touch_type.startswith("wick_") if touch_type else None,
        "at_body_touch": touch_type.startswith("close_") if touch_type else None,
        "at_close_above_level": c > level,
        "at_close_below_level": c < level,
        "at_open_above_level": o > level,
        "at_open_below_level": o < level,
        "at_body_size": _round6(body),
        "at_body_vs_recent_mean": _round6(body / recent_mean if recent_mean > 1e-12 else None),
        "at_wick_up": _round6(wick_up),
        "at_wick_down": _round6(wick_down),
        "at_wick_through_level": _round6(wick_through),
        "at_close_distance_from_level": _round6(abs(c - level)),
        "at_close_distance_atr_norm": _round6(abs(c - level) / atr_val if atr_val else None),
        "at_intrabar_cross_no_close_accept": intrabar_cross_no_accept,
    }


def extract_post_features(
    df: pd.DataFrame,
    atr_series: pd.Series,
    *,
    event_bar: int,
    level: float,
    approach_side: str,
    post_bars: int,
    near_level_atr: float,
) -> dict[str, Any]:
    """Behavior after the event bar within the post window."""
    eb = int(event_bar)
    end = min(len(df) - 1, eb + post_bars)
    post_slice = df.iloc[eb + 1 : end + 1]
    out: dict[str, Any] = {"post_bars_available": len(post_slice)}
    if post_slice.empty or approach_side not in ("above", "below"):
        return out

    break_side = _break_side(approach_side)
    closes = post_slice["close"].astype(float)
    on_break = [_on_side(c, level, break_side) for c in closes]
    on_approach = [_on_side(c, level, approach_side) for c in closes]
    out["post_bars_on_break_side"] = sum(on_break)
    out["post_bars_on_approach_side"] = sum(on_approach)

    first_return = None
    for i, bar in enumerate(post_slice.itertuples(), start=1):
        if float(bar.low) <= level <= float(bar.high):
            first_return = i
            break
    out["post_first_return_to_level_bars"] = first_return

    event_close = float(df["close"].iloc[eb])
    if break_side == "above":
        extensions = [float(x) - level for x in post_slice["high"]]
        adverse = [level - float(x) for x in post_slice["low"]]
    else:
        extensions = [level - float(x) for x in post_slice["low"]]
        adverse = [float(x) - level for x in post_slice["high"]]
    out["post_max_extension_away"] = _round6(max(extensions) if extensions else None)
    out["post_max_adverse_through_level"] = _round6(max(adverse) if adverse else None)

    retest_count = sum(
        1 for _, bar in post_slice.iterrows() if float(bar["low"]) <= level <= float(bar["high"])
    )
    out["post_retest_count"] = retest_count

    atr_val = float(atr_series.iloc[eb]) if eb < len(atr_series) else None
    if atr_val and atr_val > 0:
        post_range = float(post_slice["high"].max() - post_slice["low"].min())
        out["post_range_atr_norm"] = _round6(post_range / atr_val)
        band = near_level_atr * atr_val
        near = sum(1 for c in closes if abs(float(c) - level) <= band)
        out["post_remained_near_level_rate"] = _round6(near / len(closes))
    else:
        out["post_range_atr_norm"] = None
        out["post_remained_near_level_rate"] = None

    out["post_close_vs_event"] = _round6(
        (float(post_slice["close"].iloc[-1]) - event_close) / event_close if event_close else None
    )
    return out


def extract_fingerprint(
    df: pd.DataFrame,
    row: dict,
    cfg: FingerprintConfig,
) -> tuple[dict[str, Any] | None, str | None]:
    """Build one fingerprint row for an event, or return skip reason."""
    eb = int(row["event_bar"])
    if eb < 0 or eb >= len(df):
        return None, "event_bar_out_of_range"

    level = float(row["fib_price"])
    approach_side = row.get("approach_side", "")
    atr_series = atr(df, cfg.atr_period)

    pre = extract_pre_features(
        df,
        atr_series,
        event_bar=eb,
        level=level,
        approach_side=approach_side,
        pre_bars=cfg.pre_bars,
    )
    at = extract_at_features(df, atr_series, event_bar=eb, level=level, row=row)
    post = extract_post_features(
        df,
        atr_series,
        event_bar=eb,
        level=level,
        approach_side=approach_side,
        post_bars=cfg.post_bars,
        near_level_atr=cfg.near_level_atr,
    )

    fingerprint = {
        "event_id": _event_id(row),
        "fib_id": row.get("fib_id", ""),
        "symbol": row["symbol"],
        "timeframe": row["timeframe"],
        "exchange": row.get("exchange", ""),
        "swing_direction": row.get("swing_direction", ""),
        "fib_level": row["fib_level"],
        "fib_price": row["fib_price"],
        "event_bar": eb,
        "event_time": row.get("event_time", ""),
        "relation": row.get("relation", ""),
        "auto_candidate": row["auto_candidate"],
        "approach_side": approach_side,
        "touch_type": row.get("touch_type", ""),
        **pre,
        **at,
        **post,
    }
    return fingerprint, None


def extract_all(
    rows: list[dict],
    df_cache: dict[tuple[str, str, str], pd.DataFrame],
    cfg: FingerprintConfig,
) -> tuple[list[dict], list[SkippedFingerprint]]:
    fingerprints: list[dict] = []
    skipped: list[SkippedFingerprint] = []

    for row in rows:
        eid = _event_id(row)
        key = (row.get("exchange", ""), row["symbol"], row["timeframe"])
        df = df_cache.get(key)
        if df is None:
            skipped.append(
                SkippedFingerprint(
                    eid,
                    "missing_candles",
                    row.get("fib_id", ""),
                    row["symbol"],
                    row["timeframe"],
                )
            )
            continue
        fp, reason = extract_fingerprint(df, row, cfg)
        if fp is None:
            skipped.append(
                SkippedFingerprint(
                    eid,
                    reason or "unknown",
                    row.get("fib_id", ""),
                    row["symbol"],
                    row["timeframe"],
                )
            )
            continue
        fingerprints.append(fp)
    return fingerprints, skipped


def summarize_fingerprints(fingerprints: list[dict]) -> list[dict]:
    """Count events and mean key metrics grouped by candidate/relation/level/timeframe."""
    buckets: dict[tuple, list[dict]] = defaultdict(list)
    for fp in fingerprints:
        key = (
            fp.get("auto_candidate", ""),
            fp.get("relation", ""),
            fp.get("fib_level", ""),
            fp.get("timeframe", ""),
        )
        buckets[key].append(fp)

    numeric_keys = (
        "pre_bars_approaching_level",
        "pre_distance_atr_norm",
        "at_close_distance_atr_norm",
        "post_bars_on_break_side",
        "post_retest_count",
        "post_max_extension_away",
    )
    summary: list[dict] = []
    for key, rows in sorted(buckets.items()):
        candidate, relation, level, tf = key
        entry: dict[str, Any] = {
            "auto_candidate": candidate,
            "relation": relation,
            "fib_level": level,
            "timeframe": tf,
            "n_events": len(rows),
        }
        for nk in numeric_keys:
            vals = [r[nk] for r in rows if r.get(nk) is not None]
            entry[f"mean_{nk}"] = _round6(statistics.mean(vals)) if vals else None
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


def run_fib_level_fingerprints(
    event_paths: list[Path],
    *,
    settings: Settings | None = None,
    cfg: FingerprintConfig | None = None,
    skip_out_of_range: bool = False,
) -> dict[str, Any]:
    """Extract fingerprints and write reproducible artifacts under experiments/."""
    settings = settings or load_settings()
    cfg = cfg or FingerprintConfig()
    event_paths = [Path(p) for p in event_paths]
    if not event_paths:
        raise ValueError("No event files provided")

    run_id = datetime.now(UTC).strftime("fingerprints_%Y%m%dT%H%M%SZ")
    run_date = datetime.now(UTC).strftime("%Y-%m-%d")
    run_dir = FIB_FINGERPRINTS_RUNS / run_date / run_id

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

    fingerprints, skipped = extract_all(rows, df_cache, cfg)
    for fp in fingerprints:
        fp["run_id"] = run_id
    summary = summarize_fingerprints(fingerprints)

    config_doc = {
        "run_id": run_id,
        "pre_bars": cfg.pre_bars,
        "post_bars": cfg.post_bars,
        "atr_period": cfg.atr_period,
        "near_level_atr": cfg.near_level_atr,
        "event_files": [str(p) for p in event_paths],
        "created_at": datetime.now(UTC).isoformat(),
    }
    run_summary = {
        **config_doc,
        "events_input": len(rows),
        "fingerprints_extracted": len(fingerprints),
        "events_skipped": len(skipped),
        "load_skipped": len(load_skips),
        "skipped_reasons": dict(sorted(Counter(s.reason for s in skipped).items())),
        "load_skip_reasons": dict(sorted(Counter(s["reason"] for s in load_skips).items())),
        "timeframes_seen": sorted({fp["timeframe"] for fp in fingerprints}),
    }

    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "config.json").write_text(json.dumps(config_doc, indent=2), encoding="utf-8")
    _write_jsonl(run_dir / "fingerprints.jsonl", fingerprints)
    _write_jsonl(
        run_dir / "skipped_events.jsonl",
        [s.__dict__ for s in skipped] + load_skips,
    )
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_summary_csv(run_dir / "summary.csv", summary)
    (run_dir / "run_summary.json").write_text(json.dumps(run_summary, indent=2), encoding="utf-8")

    FIB_FINGERPRINTS_RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with FIB_FINGERPRINTS_RESULTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(run_summary, sort_keys=True) + "\n")

    return {**run_summary, "run_dir": str(run_dir)}


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Extract fib level interaction fingerprints (research-only, #23)."
    )
    p.add_argument("--events", action="append", default=[], dest="event_files", type=Path)
    p.add_argument("--all-human-fib-events", action="store_true")
    p.add_argument("--pre-bars", type=int, default=20)
    p.add_argument("--post-bars", type=int, default=50)
    p.add_argument("--atr-period", type=int, default=14)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    if args.all_human_fib_events:
        paths = discover_human_fib_event_files()
    else:
        paths = list(args.event_files)
    if not paths:
        raise SystemExit("Provide --events <path> or --all-human-fib-events")

    result = run_fib_level_fingerprints(
        paths,
        cfg=FingerprintConfig(
            pre_bars=args.pre_bars,
            post_bars=args.post_bars,
            atr_period=args.atr_period,
        ),
        skip_out_of_range=args.all_human_fib_events,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

"""Human-fib behavior candidates (emit-only, research).

Feed a **human-drawn fib** (ground-truth anchors from ``human_fib``) into the
existing :func:`fibengine.research.level_events.detect_level_events` and emit
``*_candidate`` events per fib level for later human review.

Layering:

- **Atoms** (per candle, in ``human_fib``): ``touch / cross / above / below``.
- **Candidates** (this module, across candles): ``rejection / continuation /
  failure / reaction`` — the *path* price takes after touching a level.

The human fib supplies the level prices; the candidate logic is reused verbatim
(no new formulas, no auto-fib, no tuning). **Candidates are never facts** — they
are inputs to human review (see ``docs/research/LEVEL_EVENTS.md``). This module is
additive and does not touch swing selection, evaluation, recall or promotion.

Run (needs cached candles; no network):
    uv run python -m fibengine.labeling.human_fib_events \\
        --fib data/labels/human_fib/bitfinex/BTC-USD/1d/<fib_id>.json
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from fibengine.core.config import load_settings
from fibengine.core.models import Pivot, Swing
from fibengine.data.loader import load_candles
from fibengine.labeling.human_fib import (
    HumanFibAnnotation,
    annotation_path,
    load_annotation,
)
from fibengine.research.level_events import (
    LevelEventConfig,
    LevelInteractionStream,
    detect_level_events,
)


def _bar_index(df: pd.DataFrame, time_str: str) -> int:
    ts = pd.to_datetime(time_str, utc=True)
    return int(df.index.get_indexer([ts], method="nearest")[0])


def swing_from_annotation(df: pd.DataFrame, ann: HumanFibAnnotation) -> Swing:
    """Build a Swing from human anchors so ``fib_levels(swing)`` == ann levels.

    ``anchor_a`` -> start (ratio 1.0), ``anchor_b`` -> end (ratio 0.0). The
    detector scans bars after ``end.index``, i.e. after the drawn leg. Assumes
    ``anchor_b`` is the temporal end of the leg (true for the labeling tool).
    """
    a_idx = _bar_index(df, ann.anchor_a.time)
    b_idx = _bar_index(df, ann.anchor_b.time)
    if a_idx > b_idx:
        raise ValueError(
            "Human fib anchors must be chronological: "
            f"anchor_a({ann.anchor_a.time}) is after anchor_b({ann.anchor_b.time}). "
            "Re-save the annotation from labeling.tool or swap anchors in the JSON."
        )
    start = Pivot(
        index=a_idx,
        timestamp=df.index[a_idx],
        price=float(ann.anchor_a.price),
        kind="high" if ann.direction == "down" else "low",
        prominence=0.0,
    )
    end = Pivot(
        index=b_idx,
        timestamp=df.index[b_idx],
        price=float(ann.anchor_b.price),
        kind="low" if ann.direction == "down" else "high",
        prominence=0.0,
    )
    return Swing(start=start, end=end, status="human")


def detect_candidates(
    df: pd.DataFrame,
    ann: HumanFibAnnotation,
    cfg: LevelEventConfig | None = None,
    atr_period: int = 14,
) -> list[LevelInteractionStream]:
    """Emit per-level ``*_candidate`` streams for a human fib (thin wrapper)."""
    cfg = cfg or LevelEventConfig()
    swing = swing_from_annotation(df, ann)
    ratios = [lvl.ratio for lvl in ann.levels]
    return detect_level_events(df, swing, cfg, ratios, atr_period)


def summarize(streams: list[LevelInteractionStream]) -> dict[str, dict[str, int]]:
    return {s.level: dict(Counter(e.auto_candidate for e in s.events)) for s in streams}


def events_path(ann: HumanFibAnnotation) -> Path:
    return annotation_path(ann).with_name(f"{ann.fib_id}_events.json")


def save_events(
    ann: HumanFibAnnotation,
    streams: list[LevelInteractionStream],
    cfg: LevelEventConfig | None = None,
    path: Path | None = None,
) -> Path:
    cfg = cfg or LevelEventConfig()
    path = path or events_path(ann)
    payload = {
        "fib_id": ann.fib_id,
        "symbol": ann.symbol,
        "timeframe": ann.timeframe,
        "exchange": ann.exchange,
        "direction": ann.direction,
        "anchor_a": asdict(ann.anchor_a),
        "anchor_b": asdict(ann.anchor_b),
        "source": "human_fib_events",
        "created_at": datetime.now(UTC).isoformat(),
        "config": cfg.model_dump(),
        "n_events": sum(len(s.events) for s in streams),
        "levels": [s.to_dict() for s in streams],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Emit *_candidate events from a human fib annotation "
            "(research; candidates never facts)."
        )
    )
    p.add_argument("--fib", type=Path, required=True, help="Path to a human fib annotation JSON.")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    ann = load_annotation(args.fib)
    settings = load_settings()
    data_cfg = settings.data.model_copy(
        update={"exchange": ann.exchange, "symbol": ann.symbol, "timeframe": ann.timeframe}
    )
    try:
        df = load_candles(data_cfg, fetch_if_missing=False)
    except FileNotFoundError as exc:
        raise SystemExit(f"No cached candles: {exc}") from exc

    cfg = LevelEventConfig()
    streams = detect_candidates(df, ann, cfg, settings.pivots.atr_period)
    path = save_events(ann, streams, cfg)
    n = sum(len(s.events) for s in streams)
    print(f"Saved {n} candidate events -> {path}")
    for level, counts in summarize(streams).items():
        print(f"  level {level}: {counts or '{}'}")


if __name__ == "__main__":
    main()

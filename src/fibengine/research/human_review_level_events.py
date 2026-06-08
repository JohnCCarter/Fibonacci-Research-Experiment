"""Bounded Human Review v1 for Fibonacci level event candidates (research-only).

Thin CLI + backward-compatible re-exports. Implementation split across
``human_review_constants``, ``human_review_rows``, ``human_review_charts``,
and ``human_review_pack``.

Run:
    uv run python -m fibengine.research.human_review_level_events --max-events 40 --seed 7
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fibengine.core.config import load_settings
from fibengine.core.scoring import select_swing
from fibengine.data.loader import load_candles
from fibengine.research.human_review_charts import (
    _draw_active_fib_badge,
    _draw_anchor_labels,
    _draw_event_label,
    _draw_fib_leg_overlay,
    _draw_fib_levels,
    _draw_fib_review_panel,
    _draw_view_mode_badge,
    _price_bounds_for_row,
    _resolve_row_bars,
    _warn_row_data_alignment,
    format_review_status_lines,
    render_chart,
    window_for_view,
    xlim_for_view,
)
from fibengine.research.human_review_constants import (
    CANDIDATE_TYPES,
    HUMAN_CONFIDENCE,
    HUMAN_LABELS,
    REVIEW_COLUMNS,
    REVIEW_ROOT,
    HumanReviewConfig,
    ReviewViewMode,
)
from fibengine.research.human_review_pack import (
    run_human_fib_review,
    run_human_review,
    write_index,
    write_review_sheets,
)
from fibengine.research.human_review_rows import (
    _row_for_event,
    _rows_from_human_fib_events_payload,
    collect_candidates,
    collect_human_fib_event_candidates,
    make_review_id,
    sample_candidates,
)
from fibengine.research.human_review_rows import (
    decode_levels as _decode_levels,
)
from fibengine.research.human_review_rows import (
    encode_levels as _encode_levels,
)
from fibengine.research.level_events import detect_level_events

__all__ = [
    "CANDIDATE_TYPES",
    "HUMAN_CONFIDENCE",
    "HUMAN_LABELS",
    "REVIEW_COLUMNS",
    "REVIEW_ROOT",
    "HumanReviewConfig",
    "ReviewViewMode",
    "_decode_levels",
    "_draw_active_fib_badge",
    "_draw_anchor_labels",
    "_draw_event_label",
    "_draw_fib_leg_overlay",
    "_draw_fib_levels",
    "_draw_fib_review_panel",
    "_draw_view_mode_badge",
    "_encode_levels",
    "_price_bounds_for_row",
    "_resolve_row_bars",
    "_row_for_event",
    "_rows_from_human_fib_events_payload",
    "_warn_row_data_alignment",
    "collect_candidates",
    "collect_human_fib_event_candidates",
    "detect_level_events",
    "format_review_status_lines",
    "load_candles",
    "make_review_id",
    "render_chart",
    "run_human_fib_review",
    "run_human_review",
    "sample_candidates",
    "select_swing",
    "window_for_view",
    "write_index",
    "write_review_sheets",
    "xlim_for_view",
]


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate a mobile-friendly human-review package for Fibonacci level "
        "event candidates (research-only)."
    )
    p.add_argument("--mode", choices=["single", "walk-forward"], default="walk-forward")
    p.add_argument(
        "--dedupe",
        action="store_true",
        help="Walk-forward: non-overlapping attribution (each bar counted under one leg).",
    )
    p.add_argument("--max-events", type=int, default=40, help="Max sampled events total.")
    p.add_argument("--max-per-candidate", type=int, default=None)
    p.add_argument("--max-per-level", type=int, default=None)
    p.add_argument(
        "--candidate-type",
        action="append",
        default=[],
        dest="candidate_types",
        help="Filter to these candidate types (repeatable).",
    )
    p.add_argument(
        "--level",
        action="append",
        default=[],
        dest="levels",
        help="Filter to these fib levels, e.g. 0.5 (repeatable).",
    )
    p.add_argument("--seed", type=int, default=None, help="Random seed for reproducible sampling.")
    p.add_argument(
        "--exchange",
        default=None,
        help="Override settings.data.exchange (default: config/settings.yaml).",
    )
    p.add_argument(
        "--symbol",
        default=None,
        help="Override settings.data.symbol, e.g. BTC/USD.",
    )
    p.add_argument(
        "--timeframe",
        default=None,
        help="Override settings.data.timeframe, e.g. 1d.",
    )
    p.add_argument(
        "--line",
        action="store_true",
        help="Use a close-line instead of candlesticks (lighter). Candlesticks are default.",
    )
    p.add_argument(
        "--context",
        type=int,
        default=None,
        help="Show ±N bars around the event (sets both --context-before and --context-after).",
    )
    p.add_argument("--context-before", type=int, default=25)
    p.add_argument("--context-after", type=int, default=25)
    p.add_argument(
        "--human-fib-events",
        action="append",
        type=Path,
        default=[],
        help="Review saved <fib_id>_events.json files from human_fib_events (repeatable).",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    before = args.context if args.context is not None else args.context_before
    after = args.context if args.context is not None else args.context_after
    settings = load_settings()
    if args.exchange:
        settings.data.exchange = args.exchange
    if args.symbol:
        settings.data.symbol = args.symbol
    if args.timeframe:
        settings.data.timeframe = args.timeframe
    cfg = HumanReviewConfig(
        max_events=args.max_events,
        max_per_candidate=args.max_per_candidate,
        max_per_level=args.max_per_level,
        candidate_types=args.candidate_types,
        levels=args.levels,
        seed=args.seed,
        context_before=before,
        context_after=after,
        candlestick=not args.line,
    )
    if args.human_fib_events:
        result = run_human_fib_review(args.human_fib_events, settings=settings, cfg=cfg)
    else:
        result = run_human_review(settings=settings, cfg=cfg, mode=args.mode, dedupe=args.dedupe)
    print(json.dumps(result, indent=2))

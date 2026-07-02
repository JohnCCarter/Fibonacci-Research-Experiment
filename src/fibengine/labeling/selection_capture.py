"""Pure conversion between the labeling GUI's leg picks and the contrastive selection-annotation
schema (Issue #42 capture surface). GUI-free so it is unit-testable; ``labeling/tool.py`` wires the
Matplotlib interaction on top of these helpers.

WHY: the screenshot-from-TradingView → transcribe → snap path is the capture bottleneck (repeated
price levels scramble chronology). Drawing directly on cached candles gives exact anchor
timestamps + prices with zero snap ambiguity, feeding the ``selection_annotation`` schema.

NO edge / PnL claim: this records which A/B leg the human accepts/rejects/marks-ambiguous and why.
"""

from __future__ import annotations

from pathlib import Path

from fibengine.research.selection_annotation import (
    Anchor,
    AnnotationWindow,
    Candidate,
    dump_window,
)


def direction_from_anchors(anchor_a: Anchor, anchor_b: Anchor) -> str:
    """Leg direction from anchor price ordering: high→low is ``down``, low→high is ``up``.

    Matches the ``Candidate`` structural check. Raises on equal prices (a degenerate leg).
    """
    if anchor_a.price == anchor_b.price:
        raise ValueError("degenerate leg: equal anchor prices")
    return "down" if anchor_a.price > anchor_b.price else "up"


def time_ordered(anchor_a: Anchor, anchor_b: Anchor) -> tuple[Anchor, Anchor]:
    """Order two anchors so the earlier-in-time one is first (the fib origin "1").

    A clean impulse starts at the origin and runs to the endpoint, so the earlier anchor is the
    origin. Ties (same timestamp) keep the higher-priced anchor first, which yields a ``down`` leg
    via :func:`direction_from_anchors`.
    """
    if anchor_a.time < anchor_b.time:
        return anchor_a, anchor_b
    if anchor_b.time < anchor_a.time:
        return anchor_b, anchor_a
    return (anchor_a, anchor_b) if anchor_a.price >= anchor_b.price else (anchor_b, anchor_a)


def next_candidate_id(existing: list[Candidate]) -> str:
    """Stable ``c1``/``c2``/... id one past the current max ``cN`` (gaps tolerated)."""
    nums = [int(c.id[1:]) for c in existing if c.id.startswith("c") and c.id[1:].isdigit()]
    return f"c{(max(nums) + 1) if nums else 1}"


def make_candidate(
    anchor_a: Anchor,
    anchor_b: Anchor,
    label: str,
    *,
    existing: list[Candidate] | None = None,
    reason: str = "",
    tags: tuple[str, ...] = (),
) -> Candidate:
    """Build one validated ``Candidate`` from two drawn anchors; direction is inferred."""
    return Candidate(
        id=next_candidate_id(existing or []),
        anchor_a=anchor_a,
        anchor_b=anchor_b,
        direction=direction_from_anchors(anchor_a, anchor_b),
        label=label,
        reason=reason,
        tags=tuple(tags),
    )


def build_window(
    *,
    symbol: str,
    timeframe: str,
    exchange: str,
    window_start: str,
    window_end: str,
    candidates: list[Candidate],
    regime_label: str = "",
    structure_label: str = "",
    created_by: str = "human",
) -> AnnotationWindow:
    """Assemble a validated ``AnnotationWindow`` (dataclass enforces invariants)."""
    return AnnotationWindow(
        symbol=symbol,
        timeframe=timeframe,
        exchange=exchange,
        window_start=window_start,
        window_end=window_end,
        regime_label=regime_label,
        structure_label=structure_label,
        created_by=created_by,
        candidates=tuple(candidates),
    )


def _compact_day(iso_ts: str) -> str:
    """First 10 chars of an ISO timestamp (``YYYY-MM-DD``) with dashes stripped → ``YYYYMMDD``."""
    return iso_ts[:10].replace("-", "")


def default_window_path(base_dir: str | Path, window: AnnotationWindow) -> Path:
    """``<base>/<exchange>/<SYMBOL-slug>/<tf>/window_<startday>.yaml`` (symbol ``/`` → ``-``)."""
    symbol_slug = window.symbol.replace("/", "-")
    fname = f"window_{_compact_day(window.window_start)}.yaml"
    return Path(base_dir) / window.exchange / symbol_slug / window.timeframe / fname


def save_window(window: AnnotationWindow, base_dir: str | Path) -> Path:
    """Write ``window`` under the default path, creating parent dirs. Returns the path written."""
    path = default_window_path(base_dir, window)
    path.parent.mkdir(parents=True, exist_ok=True)
    dump_window(window, path)
    return path

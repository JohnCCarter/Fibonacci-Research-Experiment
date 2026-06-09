"""Read-only higher-timeframe human fib overlays for the labeling tool.

When the chart timeframe is lower on the BTC top-down ladder, saved human fib
annotations from higher timeframes are drawn as non-interactive reference lines.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from fibengine.labeling.human_fib import (
    HUMAN_FIB_DIRNAME,
    HumanFibAnnotation,
    load_annotation,
)
from fibengine.labeling.store import get_labels_dir

# Top-down ladder (coarse → fine). Overlays use all saved fibs from TFs above chart_tf.
TOP_DOWN_LADDER: tuple[str, ...] = ("1M", "1w", "1d", "4h", "1h")

_TIMEFRAME_ALIASES: dict[str, str] = {
    "monthly": "1M",
    "month": "1M",
    "weekly": "1w",
    "week": "1w",
    "daily": "1d",
    "day": "1d",
}

HTF_OVERLAY_COLORS: dict[str, str] = {
    "1M": "#d4a843",
    "1w": "#a78bfa",
    "1d": "#60a5fa",
    "4h": "#34d399",
}


def normalize_timeframe(timeframe: str) -> str:
    return _TIMEFRAME_ALIASES.get(timeframe.lower(), timeframe)


def _ladder_index(timeframe: str) -> int | None:
    tf = normalize_timeframe(timeframe)
    try:
        return TOP_DOWN_LADDER.index(tf)
    except ValueError:
        return None


def htf_timeframes_for_chart(chart_timeframe: str) -> list[str]:
    """Return ladder timeframes strictly above ``chart_timeframe`` (coarse → fine)."""
    chart_i = _ladder_index(chart_timeframe)
    if chart_i is None or chart_i == 0:
        return []
    return list(TOP_DOWN_LADDER[:chart_i])


def human_fib_timeframe_dir(exchange: str, symbol: str, timeframe: str) -> Path:
    sym = symbol.replace("/", "-")
    tf = normalize_timeframe(timeframe)
    return get_labels_dir() / HUMAN_FIB_DIRNAME / exchange.lower() / sym / tf


def list_saved_annotations(
    exchange: str,
    symbol: str,
    timeframe: str,
) -> list[HumanFibAnnotation]:
    """Load base human fib JSON files for one symbol/timeframe (not *_events.json)."""
    root = human_fib_timeframe_dir(exchange, symbol, timeframe)
    if not root.is_dir():
        return []
    out: list[HumanFibAnnotation] = []
    for path in sorted(root.glob("*.json")):
        if path.name.endswith("_events.json"):
            continue
        out.append(load_annotation(path))
    return out


def load_htf_overlays(
    exchange: str,
    symbol: str,
    chart_timeframe: str,
) -> list[tuple[str, HumanFibAnnotation]]:
    """(source_tf, annotation) pairs for all saved HTF fibs visible on ``chart_timeframe``."""
    rows: list[tuple[str, HumanFibAnnotation]] = []
    for htf in htf_timeframes_for_chart(chart_timeframe):
        for ann in list_saved_annotations(exchange, symbol, htf):
            rows.append((htf, ann))
    return rows


def _label_level(ann: HumanFibAnnotation) -> tuple[float, float]:
    for lvl in ann.levels:
        if lvl.ratio == 0.5:
            return lvl.ratio, lvl.price
    if ann.levels:
        mid = ann.levels[len(ann.levels) // 2]
        return mid.ratio, mid.price
    return 0.0, 0.0


def draw_htf_overlays(
    ax,
    df: pd.DataFrame,
    overlays: list[tuple[str, HumanFibAnnotation]],
    *,
    show: bool,
) -> None:
    """Draw read-only HTF fib level lines (no picks, no drag targets)."""
    if not show or not overlays or df.empty:
        return
    label_x = len(df) - 1
    for htf, ann in overlays:
        color = HTF_OVERLAY_COLORS.get(htf, "#9aa3b2")
        for lvl in ann.levels:
            ax.axhline(
                lvl.price,
                color=color,
                ls=":",
                lw=0.85,
                alpha=0.42,
                zorder=2,
            )
        ratio, price = _label_level(ann)
        ax.text(
            label_x,
            price,
            f" {htf}·{ratio:g} (ro)",
            color=color,
            fontsize=7,
            alpha=0.75,
            zorder=2,
        )

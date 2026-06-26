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


def htf_anchor_markers(
    df: pd.DataFrame,
    overlays: list[tuple[str, HumanFibAnnotation]],
) -> list[tuple[int, float, str, str]]:
    """``(bar_index, price, label, color)`` for HTF anchor H/L points visible in ``df``.

    Each higher-timeframe fib contributes its two anchors tagged ``H`` (higher price)
    and ``L`` (lower price), placed at the **nearest bar to the anchor's own timestamp**
    so the parent swing's high/low are visible in *time* (not just price) on the child
    chart — the cue needed to nest a leg onto the same swing. Anchors whose timestamp
    falls outside the chart's visible span are skipped to keep the focus on that swing.
    Pure helper — no plotting.
    """
    if df.empty or not overlays:
        return []
    t0, t1 = df.index[0], df.index[-1]
    markers: list[tuple[int, float, str, str]] = []
    for htf, ann in overlays:
        color = HTF_OVERLAY_COLORS.get(htf, "#9aa3b2")
        high_first = ann.anchor_a.price >= ann.anchor_b.price
        hi = ann.anchor_a if high_first else ann.anchor_b
        lo = ann.anchor_b if high_first else ann.anchor_a
        for anchor, role in ((hi, "H"), (lo, "L")):
            ts = pd.to_datetime(anchor.time, utc=True)
            if ts < t0 or ts > t1:
                continue
            idx = int(df.index.get_indexer([ts], method="nearest")[0])
            markers.append((idx, float(anchor.price), f"{htf}·{role}", color))
    return markers


def overlays_in_view(
    overlays: list[tuple[str, HumanFibAnnotation]],
    view_start: pd.Timestamp,
    view_end: pd.Timestamp,
) -> list[tuple[str, HumanFibAnnotation]]:
    """Overlays whose A→B span overlaps the visible time range ``[view_start, view_end]``.

    Scopes the nesting-focus cycle to the parent swings actually on screen, so
    stepping does not have to walk every HTF fib in the corpus. Pure helper.
    """
    out: list[tuple[str, HumanFibAnnotation]] = []
    for htf, ann in overlays:
        ta = pd.to_datetime(ann.anchor_a.time, utc=True)
        tb = pd.to_datetime(ann.anchor_b.time, utc=True)
        lo, hi = (ta, tb) if ta <= tb else (tb, ta)
        if hi >= view_start and lo <= view_end:
            out.append((htf, ann))
    return out


def cycle_focus_id(current_id: str | None, candidate_ids: list[str]) -> str | None:
    """Advance the nesting focus through ``candidate_ids``: None → first → … → last → None.

    ``None`` means "no focus" (show all overlays). If the current id is not among the
    candidates (e.g. the view changed), start at the first candidate. Pure helper.
    """
    if not candidate_ids:
        return None
    if current_id is None or current_id not in candidate_ids:
        return candidate_ids[0]
    nxt = candidate_ids.index(current_id) + 1
    return candidate_ids[nxt] if nxt < len(candidate_ids) else None


def select_focused(
    overlays: list[tuple[str, HumanFibAnnotation]],
    focus_id: str | None,
) -> list[tuple[str, HumanFibAnnotation]]:
    """All overlays when ``focus_id`` is None, else only the parent fib with that id.

    Focusing one parent swing removes the clutter of every HTF anchor at once so a
    child leg can be nested onto a single swing. Pure helper.
    """
    if focus_id is None:
        return overlays
    return [(htf, ann) for htf, ann in overlays if ann.fib_id == focus_id]


def filter_to_session(
    overlays: list[tuple[str, HumanFibAnnotation]],
    session_ids: set[str],
    show_frozen: bool,
) -> list[tuple[str, HumanFibAnnotation]]:
    """Overlays drawn this session only, unless ``show_frozen`` keeps the whole corpus.

    The default nesting view shows just the fibs the user is drawing now (their session),
    so the frozen corpus does not clutter the child chart while building a nested set.
    Pure helper.
    """
    if show_frozen:
        return overlays
    return [(htf, ann) for htf, ann in overlays if ann.fib_id in session_ids]


def draw_htf_overlays(
    ax,
    df: pd.DataFrame,
    overlays: list[tuple[str, HumanFibAnnotation]],
    *,
    show: bool,
) -> None:
    """Draw read-only HTF fib level lines + parent anchor H/L markers (no drag targets)."""
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
    # Parent swing H/L anchors in time+price (hollow diamonds — distinct from the
    # filled ^/v picks), only for anchors inside the visible window.
    for idx, price, label, color in htf_anchor_markers(df, overlays):
        ax.scatter(
            [idx],
            [price],
            marker="D",
            s=44,
            facecolors="none",
            edgecolors=color,
            linewidths=1.1,
            alpha=0.9,
            zorder=3,
        )
        ax.text(
            idx,
            price,
            f" {label}",
            color=color,
            fontsize=7,
            alpha=0.95,
            zorder=3,
            va="bottom",
            ha="left",
        )

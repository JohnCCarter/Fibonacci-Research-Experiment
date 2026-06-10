"""Source-fib projection chart renderer (Issue #30 Phase 2 — visual review).

Renders existing projection-review data as PNG charts:

    experiments/review/source_fib_projection/<fib_id>/charts/
        overview/
            1w_projection.png
            1d_projection.png
            4h_projection.png
        zoom/
            1w_anchor.png
            1w_cluster_001.png
            4h_cluster_001.png
            ...

Overview charts render the full candle cache (good for 1W/1D context). Zoom
charts render windows around the source-fib anchor period and around each dense
event cluster — required for 4H, where the full cache is unreadable in one frame.

Reads review_sample.csv produced by source_fib_projection_review; does NOT
re-run detection. All projected levels stay visible and event-capable; there is
no active/golden-zone sampling bias — the optional ``relation_filter`` only
selects which event *markers* are shown, never which levels are drawn.

Usage::

    python -m fibengine.research.source_fib_projection_chart \\
        --source-fib data/labels/human_fib/bitfinex/BTC-USD/1M/<fib>.json \\
        --chart-timeframes 1w,1d,4h \\
        --relation-filter all \\
        --config config/settings.expansion.yaml
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import mplfinance as mpf  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from fibengine.core.config import Settings, load_settings  # noqa: E402
from fibengine.data.loader import load_candles  # noqa: E402
from fibengine.labeling.human_fib import load_annotation  # noqa: E402
from fibengine.research.source_fib_projection_review import PROJECTION_ROOT  # noqa: E402

_RELATION_COLORS: dict[str, str] = {
    "touch": "#2196F3",
    "cross": "#F44336",
    "above": "#4CAF50",
    "below": "#FF9800",
}
_RELATION_MARKERS: dict[str, str] = {
    "touch": "^",
    "cross": "X",
    "above": "D",
    "below": "v",
}
_BOUNDARY_COLOR = "#E65100"
_RETRACE_COLOR = "#FFC107"
_BOUNDARY_LW = 1.8
_RETRACE_LW = 1.0

# Relation filters (presentation only — never affects which levels are drawn).
_RELATION_FILTERS: dict[str, set[str] | None] = {
    "all": None,
    "touch": {"touch"},
    "cross": {"cross"},
    "above_below": {"above", "below"},
}

# Per-TF clustering: (gap_bars, pad_bars, max_window_bars).
#   gap_bars        — consecutive events farther apart than this start a new cluster
#   pad_bars        — context bars added on each side of a cluster window
#   max_window_bars — a window wider than this is split into segments (4H safety)
_CLUSTER_CONFIG: dict[str, tuple[int, int, int]] = {
    "1w": (6, 4, 80),
    "1d": (10, 6, 120),
    "4h": (12, 8, 150),
}
_CLUSTER_CONFIG_DEFAULT = (10, 6, 120)

# Per-TF anchor-zoom width (bars after anchor_b, clamped to cache length).
_ANCHOR_WINDOW_BARS: dict[str, int] = {"1w": 40, "1d": 60, "4h": 90}
_ANCHOR_WINDOW_DEFAULT = 60


@dataclass
class ChartSet:
    """Charts rendered for one chart timeframe."""

    timeframe: str
    overview: Path
    zoom: list[Path] = field(default_factory=list)


def render_projection_chart(
    source_fib_path: Path | str,
    chart_tf: str,
    settings: Settings | None = None,
    out_root: Path | None = None,
    review_dir: Path | None = None,
    relation_filter: str = "all",
) -> ChartSet:
    """Render overview + zoom charts for one chart timeframe.

    Parameters
    ----------
    source_fib_path:
        Path to a ``fib_*.json`` annotation file.
    chart_tf:
        Chart timeframe to render, e.g. ``"1d"``.
    settings:
        Loaded ``Settings``. Falls back to ``load_settings()`` if not provided.
    out_root:
        ``charts`` output directory. Overview PNGs go in ``<out_root>/overview``,
        zoom PNGs in ``<out_root>/zoom``. Defaults to
        ``PROJECTION_ROOT / fib_id / "charts"``.
    review_dir:
        Directory containing ``review_sample.csv``. Defaults to
        ``PROJECTION_ROOT / fib_id``. Override in tests or when review data lives
        outside the default location.
    relation_filter:
        One of ``all`` | ``touch`` | ``cross`` | ``above_below``. Selects which
        event markers are shown and which events drive clustering. All projected
        levels stay visible regardless.
    """
    if settings is None:
        settings = load_settings()
    if relation_filter not in _RELATION_FILTERS:
        raise ValueError(
            f"Unknown relation_filter {relation_filter!r}; "
            f"expected one of {sorted(_RELATION_FILTERS)}"
        )

    ann = load_annotation(source_fib_path)

    rdir = Path(review_dir) if review_dir else PROJECTION_ROOT / ann.fib_id
    review_csv = rdir / "review_sample.csv"
    if not review_csv.exists():
        raise FileNotFoundError(
            f"No review artifact at {review_csv}. Run source_fib_projection_review first."
        )

    df_events = pd.read_csv(review_csv)
    tf_events = df_events[df_events["chart_tf"] == chart_tf].copy()
    allowed = _RELATION_FILTERS[relation_filter]
    if allowed is not None and not tf_events.empty:
        tf_events = tf_events[tf_events["relation"].isin(allowed)].copy()

    data_cfg = settings.data.model_copy(
        update={"symbol": ann.symbol, "timeframe": chart_tf, "exchange": ann.exchange}
    )
    df = load_candles(data_cfg, fetch_if_missing=False)
    start_time = pd.to_datetime(ann.anchor_b.time, utc=True)
    df = df[df.index >= start_time]

    if df.empty:
        raise ValueError(f"No candles for {ann.symbol} {chart_tf} at or after {start_time}")

    charts_dir = Path(out_root) if out_root else rdir / "charts"
    overview_dir = charts_dir / "overview"
    zoom_dir = charts_dir / "zoom"
    overview_dir.mkdir(parents=True, exist_ok=True)
    zoom_dir.mkdir(parents=True, exist_ok=True)

    suffix = "" if relation_filter == "all" else f"  |  filter={relation_filter}"
    n = len(df)

    # --- Overview (full cache) --------------------------------------------
    overview_path = overview_dir / f"{chart_tf}_projection.png"
    _draw_chart(
        ann,
        df,
        tf_events,
        chart_tf,
        overview_path,
        title=(
            f"{ann.fib_id}  |  {chart_tf}  |  OVERVIEW  |  "
            f"{ann.timeframe} fib → {chart_tf} candles{suffix}"
        ),
        fig_w=max(24, min(n // 12, 60)),
    )

    zoom_paths: list[Path] = []

    # --- Anchor zoom (always rendered; positional, not event-driven) ------
    anchor_bars = _ANCHOR_WINDOW_BARS.get(chart_tf, _ANCHOR_WINDOW_DEFAULT)
    a_end = min(n - 1, anchor_bars)
    anchor_df = df.iloc[: a_end + 1]
    anchor_path = zoom_dir / f"{chart_tf}_anchor.png"
    _draw_chart(
        ann,
        anchor_df,
        tf_events,
        chart_tf,
        anchor_path,
        title=(
            f"{ann.fib_id}  |  {chart_tf}  |  ANCHOR ZOOM  |  "
            f"{anchor_df.index[0]:%Y-%m-%d}→{anchor_df.index[-1]:%Y-%m-%d}{suffix}"
        ),
        fig_w=_zoom_width(len(anchor_df)),
    )
    zoom_paths.append(anchor_path)

    # --- Event-cluster zooms ----------------------------------------------
    gap_bars, pad_bars, max_window_bars = _CLUSTER_CONFIG.get(chart_tf, _CLUSTER_CONFIG_DEFAULT)
    if not tf_events.empty:
        event_times = list(pd.to_datetime(tf_events["event_time"], utc=True, errors="coerce"))
    else:
        event_times = []
    windows = _cluster_windows(df, event_times, gap_bars, pad_bars, max_window_bars)
    for i, (a, b) in enumerate(windows, start=1):
        wdf = df.iloc[a : b + 1]
        cpath = zoom_dir / f"{chart_tf}_cluster_{i:03d}.png"
        _draw_chart(
            ann,
            wdf,
            tf_events,
            chart_tf,
            cpath,
            title=(
                f"{ann.fib_id}  |  {chart_tf}  |  CLUSTER {i:03d}  |  "
                f"{wdf.index[0]:%Y-%m-%d}→{wdf.index[-1]:%Y-%m-%d}{suffix}"
            ),
            fig_w=_zoom_width(len(wdf)),
        )
        zoom_paths.append(cpath)

    return ChartSet(timeframe=chart_tf, overview=overview_path, zoom=zoom_paths)


def _zoom_width(n_bars: int) -> int:
    """Figure width (inches) for a zoom window."""
    return max(16, min(n_bars // 6, 48))


def _nearest_pos(df: pd.DataFrame, t) -> int | None:
    """Integer position of the bar nearest ``t``, or None if out of range."""
    if t is None or pd.isna(t):
        return None
    if t < df.index[0] or t > df.index[-1]:
        return None
    secs = np.asarray((df.index - t).total_seconds(), dtype=float)
    return int(np.argmin(np.abs(secs)))


def _cluster_windows(
    df: pd.DataFrame,
    event_times: list,
    gap_bars: int,
    pad_bars: int,
    max_window_bars: int,
) -> list[tuple[int, int]]:
    """Group event times into padded bar windows.

    Consecutive events within ``gap_bars`` belong to the same cluster. Each
    cluster is padded by ``pad_bars`` on both sides and clamped to the cache.
    A padded window wider than ``max_window_bars`` is split into contiguous
    segments so dense 4H clusters stay reviewable.
    """
    positions = sorted({p for t in event_times if (p := _nearest_pos(df, t)) is not None})
    if not positions:
        return []

    clusters: list[tuple[int, int]] = []
    lo = prev = positions[0]
    for p in positions[1:]:
        if p - prev <= gap_bars:
            prev = p
        else:
            clusters.append((lo, prev))
            lo = prev = p
    clusters.append((lo, prev))

    n = len(df)
    windows: list[tuple[int, int]] = []
    for clo, chi in clusters:
        a = max(0, clo - pad_bars)
        b = min(n - 1, chi + pad_bars)
        if b - a <= max_window_bars:
            windows.append((a, b))
        else:
            start = a
            while start <= b:
                end = min(b, start + max_window_bars)
                windows.append((start, end))
                start = end + 1
    return windows


def _draw_chart(
    ann,
    df,
    tf_events,
    chart_tf,
    out_path,
    *,
    title: str | None = None,
    fig_w: int | None = None,
):
    """Render candles + fib level lines + event scatter markers to a PNG file.

    Only events whose time falls within ``df``'s range are marked and counted,
    so the same ``tf_events`` frame yields full counts for the overview and
    window-local counts for each zoom.
    """
    levels = ann.levels
    boundary = [lv for lv in levels if lv.ratio in (0.0, 1.0)]
    retrace = [lv for lv in levels if lv.ratio not in (0.0, 1.0)]

    # Restrict events to this window once.
    ev = tf_events.copy()
    if not ev.empty:
        ev["_t"] = pd.to_datetime(ev["event_time"], utc=True, errors="coerce")
        lo, hi = df.index[0], df.index[-1]
        ev = ev[(ev["_t"] >= lo) & (ev["_t"] <= hi)]

    # One scatter series per relation type.
    addplots = []
    for relation, color in _RELATION_COLORS.items():
        rel_rows = ev[ev["relation"] == relation] if not ev.empty else ev
        if rel_rows.empty:
            continue
        marker_series = pd.Series(np.nan, index=df.index, dtype=float)
        for _, erow in rel_rows.iterrows():
            event_time = erow["_t"]
            nearest_pos = _nearest_pos(df, event_time)
            if nearest_pos is None:
                continue
            nearest = df.index[nearest_pos]
            # Place marker 0.5% above the bar high so it doesn't overlap the wick.
            marker_series.loc[nearest] = float(df.loc[nearest, "high"]) * 1.005
        if marker_series.notna().any():
            addplots.append(
                mpf.make_addplot(
                    marker_series,
                    type="scatter",
                    markersize=35,
                    marker=_RELATION_MARKERS[relation],
                    color=color,
                )
            )

    n = len(df)
    if fig_w is None:
        fig_w = max(24, min(n // 12, 60))
    if title is None:
        title = f"{ann.fib_id}  |  {chart_tf}  |  {ann.timeframe} fib → {chart_tf} candles"

    mc = mpf.make_marketcolors(up="#26a69a", down="#ef5350", inherit=True)
    style = mpf.make_mpf_style(
        marketcolors=mc,
        gridstyle=":",
        gridcolor="#cccccc",
        facecolor="#f5f5f5",
        figcolor="#ffffff",
        y_on_right=True,
    )

    plot_kwargs: dict = dict(
        type="candle",
        style=style,
        title=title,
        figsize=(fig_w, 9),
        returnfig=True,
        warn_too_much_data=100_000,
    )
    if addplots:
        plot_kwargs["addplot"] = addplots

    fig, axes = mpf.plot(df, **plot_kwargs)
    ax = axes[0]

    # Fib level lines — added post-plot for reliable per-line styling.
    for lv in boundary:
        ax.axhline(lv.price, color=_BOUNDARY_COLOR, lw=_BOUNDARY_LW, ls="--", alpha=0.9, zorder=2)
    for lv in retrace:
        ax.axhline(lv.price, color=_RETRACE_COLOR, lw=_RETRACE_LW, ls="--", alpha=0.75, zorder=2)

    # Ratio labels on right edge.
    x_right = len(df) - 1
    for lv in sorted(levels, key=lambda x: x.ratio):
        is_boundary = lv.ratio in (0.0, 1.0)
        color = _BOUNDARY_COLOR if is_boundary else _RETRACE_COLOR
        ax.text(
            x_right,
            lv.price,
            f"  {lv.ratio}",
            color=color,
            va="center",
            fontsize=7,
            fontweight="bold" if is_boundary else "normal",
        )

    # Legend — per-relation counts reflect events within this window.
    legend_handles: list[mpatches.Patch] = [
        mpatches.Patch(color=_BOUNDARY_COLOR, label=f"boundary [{ann.timeframe}]"),
        mpatches.Patch(color=_RETRACE_COLOR, label=f"retracement [{ann.timeframe}]"),
    ]
    for rel, color in _RELATION_COLORS.items():
        count = int((ev["relation"] == rel).sum()) if not ev.empty else 0
        if count:
            legend_handles.append(mpatches.Patch(color=color, label=f"{rel} ({count})"))
    ax.legend(handles=legend_handles, loc="upper left", fontsize=7, framealpha=0.85)

    fig.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close(fig)


def render_all_charts(
    source_fib_path: Path | str,
    chart_timeframes: list[str],
    settings: Settings | None = None,
    out_root: Path | None = None,
    review_dir: Path | None = None,
    relation_filter: str = "all",
) -> dict[str, ChartSet]:
    """Render overview + zoom charts for all requested timeframes."""
    results: dict[str, ChartSet] = {}
    for tf in chart_timeframes:
        results[tf] = render_projection_chart(
            source_fib_path,
            tf,
            settings=settings,
            out_root=out_root,
            review_dir=review_dir,
            relation_filter=relation_filter,
        )
    return results


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Render source-fib projection review charts as PNG files."
    )
    p.add_argument("--source-fib", required=True, help="Path to fib_*.json annotation")
    p.add_argument(
        "--chart-timeframes",
        default="1w,1d,4h",
        help="Comma-separated chart timeframes (default: 1w,1d,4h)",
    )
    p.add_argument(
        "--relation-filter",
        default="all",
        choices=sorted(_RELATION_FILTERS),
        help="Restrict event markers (default: all). all|touch|cross|above_below",
    )
    p.add_argument("--config", default=None, help="Path to settings YAML")
    p.add_argument("--out-dir", default=None, help="Override charts output directory")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    settings = load_settings(args.config)
    tfs = [t.strip() for t in args.chart_timeframes.split(",") if t.strip()]
    results = render_all_charts(
        source_fib_path=args.source_fib,
        chart_timeframes=tfs,
        settings=settings,
        out_root=Path(args.out_dir) if args.out_dir else None,
        relation_filter=args.relation_filter,
    )
    for tf, cs in results.items():
        print(f"  {tf}: overview={cs.overview}  zoom={len(cs.zoom)} window(s)")
        for zp in cs.zoom:
            print(f"      {zp.name}")

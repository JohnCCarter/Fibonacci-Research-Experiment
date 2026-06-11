"""Source-fib projection chart renderer (Issue #30 Phase 2 — visual review).

Renders existing projection-review data as PNG charts:

    experiments/review/source_fib_projection/<fib_id>/charts/
        human_fib/
            1d_human_fib.png        # clean: candles + fib leg + levels, no markers
        events/
            1d_events.png           # same view, event markers overlaid
        zoom/
            1d_anchor.png
            1d_cluster_001.png
            ...

The human_fib and events views span anchor_a−pad → review_end so the human-drawn
source move is visible, the diagonal anchor-A→anchor-B leg is drawn, and the
y-axis is log to match the TradingView log fib (the fib *math* is unchanged —
level prices come straight from the annotation). The reviewer recognizes the fib
in human_fib first, then reviews markers in events. Zoom charts render windows
around the anchor period and each dense event cluster — required for 4H, where
the full window is unreadable in one frame.

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
import shutil
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.patches as mpatches  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
import mplfinance as mpf  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from fibengine.core.config import Settings, load_settings  # noqa: E402
from fibengine.data.loader import load_candles  # noqa: E402
from fibengine.labeling.human_fib import load_annotation  # noqa: E402
from fibengine.research.source_fib_projection_review import (  # noqa: E402
    PROJECTION_ROOT,
    load_review_windows,
)

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

# Per-TF clustering: (gap_bars, pad_bars, max_window_bars, min_events).
#   gap_bars        — consecutive events farther apart than this start a new cluster
#   pad_bars        — context bars added on each side of a cluster window
#   max_window_bars — a window wider than this is split into segments (4H safety)
#   min_events      — only *dense* clusters (>= this many events) get a zoom window;
#                     isolated singletons stay visible on the overview chart
# Gap thresholds are ~14 days across TFs (events here span ~5 years with long quiet
# stretches, so a tighter gap over-fragments 4H into dozens of single-event windows).
_CLUSTER_CONFIG: dict[str, tuple[int, int, int, int]] = {
    "1w": (3, 4, 80, 2),  # gap ~21d (3 weekly bars)
    "1d": (14, 6, 120, 2),  # gap 14d
    "4h": (84, 8, 150, 2),  # gap 14d (84 four-hour bars)
}
_CLUSTER_CONFIG_DEFAULT = (14, 6, 120, 2)

# Per-TF anchor-zoom width (bars after anchor_b, clamped to cache length).
_ANCHOR_WINDOW_BARS: dict[str, int] = {"1w": 40, "1d": 60, "4h": 90}
_ANCHOR_WINDOW_DEFAULT = 60

# Per-TF context pad (bars rendered before anchor_a) so the source move sits
# inside the human-fib view rather than starting at the left edge.
_CONTEXT_PAD_BARS: dict[str, int] = {"1w": 8, "1d": 30, "4h": 120}
_CONTEXT_PAD_DEFAULT = 20

# Fib-leg / anchor styling.
_LEG_COLOR = "#5E35B1"
_ANCHOR_DOT_COLOR = "#212121"


@dataclass
class ChartSet:
    """Charts rendered for one chart timeframe.

    ``human_fib`` is the clean view (recognize the drawn fib); ``events`` is the
    same view with event markers; ``zoom`` holds anchor/cluster detail windows.
    """

    timeframe: str
    human_fib: Path
    events: Path
    zoom: list[Path] = field(default_factory=list)


def render_projection_chart(
    source_fib_path: Path | str,
    chart_tf: str,
    settings: Settings | None = None,
    out_root: Path | None = None,
    review_dir: Path | None = None,
    relation_filter: str = "all",
    full_history: bool = False,
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

    windows = {} if full_history else load_review_windows(source_fib_path)
    win = windows.get(ann.fib_id, {})
    review_end_time: str | None = win.get("review_end_time")

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

    # Clip events to review window so markers stay consistent with chart scope.
    if review_end_time and not tf_events.empty:
        end_ts = pd.to_datetime(review_end_time, utc=True)
        ev_times = pd.to_datetime(tf_events["event_time"], utc=True, errors="coerce")
        tf_events = tf_events[ev_times <= end_ts].copy()

    data_cfg = settings.data.model_copy(
        update={"symbol": ann.symbol, "timeframe": chart_tf, "exchange": ann.exchange}
    )
    df_full = load_candles(data_cfg, fetch_if_missing=False)

    anchor_a_time = pd.to_datetime(ann.anchor_a.time, utc=True)
    anchor_b_time = pd.to_datetime(ann.anchor_b.time, utc=True)
    end_ts = pd.to_datetime(review_end_time, utc=True) if review_end_time else None

    # Context view spans anchor_a (minus a pad) → review_end so the human-drawn
    # source move is visible. This only adds candle *context*; event markers come
    # from the already-gated review_sample.csv, so detection/windows are untouched.
    pad = _CONTEXT_PAD_BARS.get(chart_tf, _CONTEXT_PAD_DEFAULT)
    pos_a_full = _nearest_pos(df_full, anchor_a_time)
    lo = max(0, (pos_a_full if pos_a_full is not None else 0) - pad)
    if end_ts is not None:
        hi = int(df_full.index.searchsorted(end_ts, side="right"))
    else:
        hi = len(df_full)
    df_ctx = df_full.iloc[lo:hi]
    if df_ctx.empty:
        raise ValueError(f"No candles for {ann.symbol} {chart_tf} around anchor_a {anchor_a_time}")

    # Events view (zoom basis): anchor_b → review_end, as before.
    df_evt = df_full[df_full.index >= anchor_b_time]
    if end_ts is not None:
        df_evt = df_evt[df_evt.index <= end_ts]

    charts_dir = Path(out_root) if out_root else rdir / "charts"
    human_fib_dir = charts_dir / "human_fib"
    events_dir = charts_dir / "events"
    zoom_dir = charts_dir / "zoom"
    human_fib_dir.mkdir(parents=True, exist_ok=True)
    events_dir.mkdir(parents=True, exist_ok=True)
    zoom_dir.mkdir(parents=True, exist_ok=True)

    # Drop stale PNGs for this TF so a re-run with fewer windows leaves no orphans.
    for old in human_fib_dir.glob(f"{chart_tf}_human_fib.png"):
        old.unlink()
    for old in events_dir.glob(f"{chart_tf}_events.png"):
        old.unlink()
    for old in zoom_dir.glob(f"{chart_tf}_anchor.png"):
        old.unlink()
    for old in zoom_dir.glob(f"{chart_tf}_cluster_*.png"):
        old.unlink()

    suffix = "" if relation_filter == "all" else f"  |  filter={relation_filter}"
    # The context view spans anchor_a−pad → review_end; label it "view=" (not
    # "window=") so it isn't mistaken for the review window the human confirms.
    if review_end_time:
        win_label = f"  |  view={df_ctx.index[0]:%Y-%m-%d}→{end_ts:%Y-%m-%d}"
    else:
        win_label = "  |  full-history"

    # Anchor positions inside the context df (drive the diagonal leg + dots).
    fib_leg = (
        _nearest_pos(df_ctx, anchor_a_time),
        float(ann.anchor_a.price),
        _nearest_pos(df_ctx, anchor_b_time),
        float(ann.anchor_b.price),
    )
    n_ctx = len(df_ctx)

    # --- Human-fib view (clean — recognize the drawn fib first) -----------
    human_fib_path = human_fib_dir / f"{chart_tf}_human_fib.png"
    _draw_chart(
        ann,
        df_ctx,
        tf_events,
        chart_tf,
        human_fib_path,
        title=(
            f"{ann.fib_id}  |  {chart_tf}  |  HUMAN FIB  |  "
            f"{ann.timeframe} fib (log) → {chart_tf} candles{win_label}"
        ),
        fig_w=max(24, min(n_ctx // 12, 60)),
        show_events=False,
        fib_leg=fib_leg,
    )

    # --- Event overlay view (same picture, markers added) -----------------
    events_path = events_dir / f"{chart_tf}_events.png"
    _draw_chart(
        ann,
        df_ctx,
        tf_events,
        chart_tf,
        events_path,
        title=(
            f"{ann.fib_id}  |  {chart_tf}  |  EVENTS  |  "
            f"{ann.timeframe} fib (log) → {chart_tf} candles{win_label}{suffix}"
        ),
        fig_w=max(24, min(n_ctx // 12, 60)),
        show_events=True,
        fib_leg=fib_leg,
    )

    # Zoom charts operate on the events window (anchor_b → review_end).
    df = df_evt
    n = len(df)
    if df.empty:
        return ChartSet(timeframe=chart_tf, human_fib=human_fib_path, events=events_path, zoom=[])

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
    gap_bars, pad_bars, max_window_bars, min_events = _CLUSTER_CONFIG.get(
        chart_tf, _CLUSTER_CONFIG_DEFAULT
    )
    if not tf_events.empty:
        event_times = list(pd.to_datetime(tf_events["event_time"], utc=True, errors="coerce"))
    else:
        event_times = []
    windows = _cluster_windows(
        df, event_times, gap_bars, pad_bars, max_window_bars, min_events=min_events
    )
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

    return ChartSet(
        timeframe=chart_tf, human_fib=human_fib_path, events=events_path, zoom=zoom_paths
    )


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
    min_events: int = 1,
) -> list[tuple[int, int]]:
    """Group event times into padded bar windows.

    Consecutive events within ``gap_bars`` belong to the same cluster. Only
    clusters holding at least ``min_events`` events yield windows — isolated
    singletons are left to the overview chart. Each kept cluster is padded by
    ``pad_bars`` on both sides and clamped to the cache; a padded window wider
    than ``max_window_bars`` is split into contiguous segments so dense 4H
    clusters stay reviewable.
    """
    positions = sorted(p for t in event_times if (p := _nearest_pos(df, t)) is not None)
    if not positions:
        return []

    clusters: list[tuple[int, int, int]] = []  # (lo, hi, event_count)
    lo = prev = positions[0]
    count = 1
    for p in positions[1:]:
        if p - prev <= gap_bars:
            prev = p
            count += 1
        else:
            clusters.append((lo, prev, count))
            lo = prev = p
            count = 1
    clusters.append((lo, prev, count))

    n = len(df)
    windows: list[tuple[int, int]] = []
    for clo, chi, cnt in clusters:
        if cnt < min_events:
            continue
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


def _annotate_anchor(ax, x: int, price: float, text: str, *, below: bool) -> None:
    """Label an anchor dot with a boxed time/price tag, offset clear of the dot."""
    dy = -16 if below else 12
    ax.annotate(
        text,
        xy=(x, price),
        xytext=(6, dy),
        textcoords="offset points",
        fontsize=8,
        fontweight="bold",
        color=_ANCHOR_DOT_COLOR,
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=_ANCHOR_DOT_COLOR, alpha=0.85),
        zorder=5,
    )


def _draw_chart(
    ann,
    df,
    tf_events,
    chart_tf,
    out_path,
    *,
    title: str | None = None,
    fig_w: int | None = None,
    show_events: bool = True,
    fib_leg: tuple[int | None, float, int | None, float] | None = None,
    log_scale: bool = True,
):
    """Render candles + fib level segments (+ optional event markers) to a PNG.

    ``show_events=False`` produces the clean human-fib view (no markers) so the
    reviewer can recognize the drawn fib first. ``fib_leg`` is
    ``(pos_a, price_a, pos_b, price_b)`` in df bar positions; when both positions
    are in range the diagonal anchor-A→anchor-B leg and labelled anchor dots are
    drawn. ``log_scale`` renders the y-axis in log to match the TradingView log
    fib (the fib *math* is unchanged — prices come straight from the annotation).

    Only events whose time falls within ``df``'s range are marked and counted,
    so the same ``tf_events`` frame yields full counts for the context view and
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

    # One scatter series per relation type (suppressed in the clean human-fib view).
    addplots = []
    if show_events:
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

    # Log y-axis to match the TradingView log fib (math unchanged — see docstring).
    if log_scale:
        ax.set_yscale("log")
        ax.yaxis.set_major_formatter(mticker.ScalarFormatter())
        ax.yaxis.set_minor_formatter(mticker.ScalarFormatter())
        ax.tick_params(axis="y", which="minor", labelsize=6)

    x_right = len(df) - 1
    # Level lines are bounded segments (TradingView "extend right" from the fib),
    # not full-width axhlines. They start at anchor_a when it is in view, else at
    # the left edge.
    pos_a = fib_leg[0] if fib_leg else None
    seg_x0 = pos_a if pos_a is not None else 0
    for lv in boundary:
        ax.plot(
            [seg_x0, x_right],
            [lv.price, lv.price],
            color=_BOUNDARY_COLOR,
            lw=_BOUNDARY_LW,
            ls="--",
            alpha=0.9,
            zorder=2,
        )
    for lv in retrace:
        ax.plot(
            [seg_x0, x_right],
            [lv.price, lv.price],
            color=_RETRACE_COLOR,
            lw=_RETRACE_LW,
            ls="--",
            alpha=0.75,
            zorder=2,
        )

    # Ratio + price labels on right edge.
    for lv in sorted(levels, key=lambda x: x.ratio):
        is_boundary = lv.ratio in (0.0, 1.0)
        color = _BOUNDARY_COLOR if is_boundary else _RETRACE_COLOR
        ax.text(
            x_right,
            lv.price,
            f"  {lv.ratio}  ${lv.price:,.0f}",
            color=color,
            va="center",
            fontsize=7,
            fontweight="bold" if is_boundary else "normal",
        )

    # Diagonal fib leg + labelled anchor dots (when both anchors are in view).
    if fib_leg is not None:
        pos_a, price_a, pos_b, price_b = fib_leg
        if pos_a is not None and pos_b is not None:
            ax.plot(
                [pos_a, pos_b],
                [price_a, price_b],
                color=_LEG_COLOR,
                lw=2.0,
                ls="-",
                alpha=0.9,
                zorder=3,
            )
            ax.scatter(
                [pos_a, pos_b],
                [price_a, price_b],
                color=_ANCHOR_DOT_COLOR,
                s=40,
                zorder=4,
            )
            a_date = pd.to_datetime(ann.anchor_a.time, utc=True).strftime("%Y-%m-%d")
            b_date = pd.to_datetime(ann.anchor_b.time, utc=True).strftime("%Y-%m-%d")
            _annotate_anchor(ax, pos_a, price_a, f"A  {a_date}  ${price_a:,.0f}", below=True)
            _annotate_anchor(ax, pos_b, price_b, f"B  {b_date}  ${price_b:,.0f}", below=False)

    # Legend. Relation counts only on the events view — the clean human-fib view
    # must not leak event info (recognize the fib first, review markers after).
    legend_handles: list[mpatches.Patch] = [
        mpatches.Patch(color=_BOUNDARY_COLOR, label=f"boundary [{ann.timeframe}]"),
        mpatches.Patch(color=_RETRACE_COLOR, label=f"retracement [{ann.timeframe}]"),
    ]
    if show_events:
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
    full_history: bool = False,
) -> dict[str, ChartSet]:
    """Render overview + zoom charts for all requested timeframes.

    Clears the charts directory before writing so stale TF artifacts from a
    previous run never appear in the output package.
    """
    ann = load_annotation(source_fib_path)
    rdir = Path(review_dir) if review_dir else PROJECTION_ROOT / ann.fib_id
    charts_dir = Path(out_root) if out_root else rdir / "charts"
    if charts_dir.exists():
        shutil.rmtree(charts_dir)

    results: dict[str, ChartSet] = {}
    for tf in chart_timeframes:
        results[tf] = render_projection_chart(
            source_fib_path,
            tf,
            settings=settings,
            out_root=out_root,
            review_dir=review_dir,
            relation_filter=relation_filter,
            full_history=full_history,
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
    p.add_argument(
        "--full-history",
        action="store_true",
        help="Ignore review_windows.yaml and render the full candle cache (debug only)",
    )
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
        full_history=getattr(args, "full_history", False),
    )
    for tf, cs in results.items():
        print(f"  {tf}: human_fib={cs.human_fib}")
        print(f"      events={cs.events}  zoom={len(cs.zoom)} window(s)")
        for zp in cs.zoom:
            print(f"      {zp.name}")

"""Chart rendering for human Fibonacci level-event review."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

from fibengine.research.human_review_candles import draw_review_candles
from fibengine.research.human_review_constants import HumanReviewConfig, ReviewViewMode
from fibengine.research.human_review_rows import (
    _bar_index,
    decode_levels,
)

_decode_levels = decode_levels


def _chart_x(bar_idx: int, x_shift: int) -> int:
    return int(bar_idx) - x_shift


def _anchor_chart_label(label: str) -> str:
    if "@" in label:
        head, price = label.split("@", 1)
        return f"{head.strip()} @ {price.strip()}"
    return label.strip()


def _mark_swing_point(
    ax,
    df,
    bar_idx,
    lo,
    hi,
    *,
    marker,
    color,
    label,
    price=None,
    dark_theme: bool = False,
    x_shift: int = 0,
) -> None:
    if not (lo <= bar_idx <= hi):
        return
    x = _chart_x(bar_idx, x_shift)
    y = float(price) if price is not None else float(df["close"].iloc[bar_idx])
    ax.scatter(
        [x],
        [y],
        color=color,
        marker=marker,
        s=170,
        edgecolors="black",
        linewidths=0.7,
        zorder=7,
    )
    y_off = 22 if marker == "^" else -24
    x_off = -28 if bar_idx >= (lo + hi) // 2 else 22
    ax.annotate(
        _anchor_chart_label(label),
        xy=(x, y),
        xytext=(x_off, y_off),
        textcoords="offset points",
        fontsize=8.5,
        color=color,
        fontweight="bold",
        ha="center",
        va="bottom" if marker == "^" else "top",
        bbox={
            "boxstyle": "round,pad=0.3",
            "fc": "#1a1d26" if dark_theme else "white",
            "ec": color,
            "alpha": 0.94,
        },
        zorder=9,
    )


def _price_label(value: float) -> str:
    return f"{float(value):,.2f}"


def _anchor_points(row: dict) -> list[dict]:
    a = {
        "bar": int(row.get("anchor_a_bar", row["swing_start_bar"])),
        "time": row.get("anchor_a_time", row["swing_start_time"]),
        "price": float(row.get("anchor_a_price", row.get("fib_price"))),
    }
    b = {
        "bar": int(row.get("anchor_b_bar", row["swing_end_bar"])),
        "time": row.get("anchor_b_time", row["swing_end_time"]),
        "price": float(row.get("anchor_b_price", row.get("fib_price"))),
    }
    if row.get("swing_direction") == "down":
        h_anchor, l_anchor = a, b
    else:
        h_anchor, l_anchor = b, a
    tf = row["timeframe"]
    return [
        {
            **h_anchor,
            "label": f"H anchor {tf} @ {_price_label(h_anchor['price'])}",
            "marker": "^",
        },
        {
            **l_anchor,
            "label": f"L anchor {tf} @ {_price_label(l_anchor['price'])}",
            "marker": "v",
        },
    ]


def _draw_anchor_labels(
    ax,
    df: pd.DataFrame,
    row: dict,
    lo: int,
    hi: int,
    *,
    color: str,
    dark_theme: bool = False,
    x_shift: int = 0,
) -> None:
    for anchor in _anchor_points(row):
        _mark_swing_point(
            ax,
            df,
            anchor["bar"],
            lo,
            hi,
            marker=anchor["marker"],
            color=color,
            label=anchor["label"],
            price=anchor["price"],
            dark_theme=dark_theme,
            x_shift=x_shift,
        )


def _fib_leg_spec(row: dict) -> tuple[dict, dict, str, str]:
    anchors = _anchor_points(row)
    h, low_anchor = anchors[0], anchors[1]
    direction = str(row.get("swing_direction") or "down")
    if direction == "down":
        return h, low_anchor, "H → L fib leg", direction
    return low_anchor, h, "L → H fib leg", direction


def _leg_price_at_bar(x0: float, y0: float, x1: float, y1: float, bar: float) -> float:
    if x1 == x0:
        return y0
    return y0 + (y1 - y0) * (bar - x0) / (x1 - x0)


def _offscreen_hint(anchor: dict, lo: int, hi: int) -> str | None:
    bar = int(anchor["bar"])
    role = " ".join(anchor["label"].split()[:2])
    if bar < lo:
        return f"◀ {role} off-screen"
    if bar > hi:
        return f"{role} off-screen ▶"
    return None


def _draw_fib_leg_overlay(
    ax,
    row: dict,
    lo: int,
    hi: int,
    *,
    dark_theme: bool = False,
    x_shift: int = 0,
) -> None:
    start, end, leg_label, direction = _fib_leg_spec(row)
    color = "#b388ff" if dark_theme else "#7e57c2"
    fc = "#1a1d26" if dark_theme else "white"
    x0, y0 = _chart_x(int(start["bar"]), x_shift), float(start["price"])
    x1, y1 = _chart_x(int(end["bar"]), x_shift), float(end["price"])
    lo_x, hi_x = _chart_x(lo, x_shift), _chart_x(hi, x_shift)
    offscreen = [h for h in (_offscreen_hint(start, lo, hi), _offscreen_hint(end, lo, hi)) if h]

    if x0 == x1:
        ax.vlines(
            x0,
            min(y0, y1),
            max(y0, y1),
            colors=color,
            linewidth=2.4,
            alpha=0.88,
            zorder=3,
        )
        span = max(y0, y1) - min(y0, y1) or 1.0
        mid = (y0 + y1) / 2
        if direction == "down":
            ax.annotate(
                "",
                xy=(x0, min(y0, y1) + 0.12 * span),
                xytext=(x0, max(y0, y1) - 0.12 * span),
                arrowprops={"arrowstyle": "->", "color": color, "lw": 2.2},
                zorder=4,
            )
        else:
            ax.annotate(
                "",
                xy=(x0, max(y0, y1) - 0.12 * span),
                xytext=(x0, min(y0, y1) + 0.12 * span),
                arrowprops={"arrowstyle": "->", "color": color, "lw": 2.2},
                zorder=4,
            )
        label_x, label_y = x0, mid
    else:
        sx, sy, ex, ey = x0, y0, x1, y1
        if sx < lo_x:
            sx, sy = float(lo_x), _leg_price_at_bar(x0, y0, x1, y1, lo_x)
        elif sx > hi_x:
            sx, sy = float(hi_x), _leg_price_at_bar(x0, y0, x1, y1, hi_x)
        if ex < lo_x:
            ex, ey = float(lo_x), _leg_price_at_bar(x0, y0, x1, y1, lo_x)
        elif ex > hi_x:
            ex, ey = float(hi_x), _leg_price_at_bar(x0, y0, x1, y1, hi_x)
        if (sx, sy) != (ex, ey):
            ax.annotate(
                "",
                xy=(ex, ey),
                xytext=(sx, sy),
                arrowprops={
                    "arrowstyle": "->",
                    "color": color,
                    "lw": 2.4,
                    "alpha": 0.9,
                    "shrinkA": 0,
                    "shrinkB": 0,
                },
                zorder=3,
            )
        label_x = (sx + ex) / 2
        label_y = (sy + ey) / 2

    leg_visible = lo_x <= x0 <= hi_x or lo_x <= x1 <= hi_x or x0 < lo_x < x1 or x0 < hi_x < x1
    if leg_visible:
        ax.text(
            label_x,
            label_y,
            f"{leg_label}\ndirection: {direction}",
            fontsize=8,
            color=color,
            fontweight="bold",
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.3", "fc": fc, "ec": color, "alpha": 0.9},
            zorder=4,
        )

    for i, hint in enumerate(offscreen):
        ax.text(
            0.02,
            0.12 - i * 0.05,
            hint,
            transform=ax.transAxes,
            fontsize=7.5,
            color=color,
            fontstyle="italic",
            bbox={"boxstyle": "round,pad=0.2", "fc": fc, "ec": color, "alpha": 0.85},
            zorder=4,
            clip_on=False,
        )


def _active_fib_style(*, dark_theme: bool) -> tuple[str, float, float, int]:
    if dark_theme:
        return "#5eb3ff", 2.6, 1.0, 5
    return "#1a73e8", 2.4, 1.0, 5


def _inactive_fib_style(*, dark_theme: bool) -> tuple[str, float, float, int]:
    if dark_theme:
        return "#3d4654", 0.5, 0.18, 1
    return "#b0b8c4", 0.55, 0.22, 1


def _draw_fib_levels(ax, row: dict, *, dark_theme: bool = False) -> None:
    active = str(row["fib_level"])
    active_color, active_lw, active_alpha, active_z = _active_fib_style(dark_theme=dark_theme)
    inactive_color, inactive_lw, inactive_alpha, inactive_z = _inactive_fib_style(
        dark_theme=dark_theme
    )
    for lvl in _decode_levels(row):
        ratio = str(lvl["ratio"])
        price = float(lvl["price"])
        is_active = ratio == active
        ax.axhline(
            price,
            color=active_color if is_active else inactive_color,
            ls="-" if is_active else "--",
            lw=active_lw if is_active else inactive_lw,
            alpha=active_alpha if is_active else inactive_alpha,
            zorder=active_z if is_active else inactive_z,
        )


def _event_date(row: dict) -> str:
    return str(row.get("event_time", ""))[:10]


def _view_mode_label(mode: ReviewViewMode) -> str:
    return "fib-context" if mode == "fib_context" else "event-zoom"


def _bars_for_view(row: dict) -> list[int]:
    bars: list[int] = []
    for key in (
        "anchor_a_bar",
        "anchor_b_bar",
        "event_bar",
        "swing_start_bar",
        "swing_end_bar",
    ):
        val = row.get(key)
        if val not in (None, ""):
            bars.append(int(val))
    return bars or [int(row["event_bar"])]


def window_for_view(
    row: dict,
    df: pd.DataFrame,
    cfg: HumanReviewConfig,
    mode: ReviewViewMode,
) -> tuple[int, int]:
    n = len(df) - 1
    eb = int(row["event_bar"])
    if mode == "event_zoom":
        return max(0, eb - cfg.context_before), min(n, eb + cfg.context_after)
    bars = _bars_for_view(row)
    pad = cfg.fib_context_pad_bars
    return max(0, min(bars) - pad), min(n, max(bars) + pad)


def xlim_for_view(
    row: dict,
    df: pd.DataFrame,
    cfg: HumanReviewConfig,
    mode: ReviewViewMode,
) -> tuple[float, float]:
    if mode == "event_zoom":
        eb = int(row["event_bar"])
        pad = max(cfg.context_before, cfg.context_after, 30)
        return float(eb - pad), float(eb + pad)
    lo, hi = window_for_view(row, df, cfg, mode)
    return float(lo) - 0.5, float(hi) + 0.5


def format_review_status_lines(
    row: dict,
    *,
    index: int | None = None,
    total: int | None = None,
    labeled: int | None = None,
    view_mode: ReviewViewMode | None = None,
) -> str:
    relation = row.get("relation") or row.get("touch_type") or "event"
    hl = (row.get("human_label") or "").strip() or "unset"
    hc = (row.get("human_confidence") or "").strip() or "unset"
    fib_id = row.get("fib_id") or row.get("fib_source", "fib")
    head = (
        f"[{index}/{total}] {row['symbol']} {row['timeframe'].upper()}"
        if index
        else (f"{row['symbol']} {row['timeframe'].upper()}")
    )
    lines = [
        head,
        f"Fib: {fib_id}",
        f"Event: {_event_date(row)} | {row['fib_level']} {relation} → {row['auto_candidate']}",
    ]
    if view_mode is not None:
        lines.append(f"View: {_view_mode_label(view_mode)} (g=toggle)")
    if index is not None and total is not None and labeled is not None:
        lines.append(f"Human: {hl} | confidence: {hc} | labeled {labeled}/{total}")
    else:
        lines.append(f"Human: {hl} | confidence: {hc}")
    return "\n".join(lines)


def _resolve_row_bars(df: pd.DataFrame, row: dict) -> dict:
    out = dict(row)
    for time_key, bar_key in (
        ("event_time", "event_bar"),
        ("anchor_a_time", "anchor_a_bar"),
        ("anchor_b_time", "anchor_b_bar"),
        ("swing_start_time", "swing_start_bar"),
        ("swing_end_time", "swing_end_bar"),
    ):
        raw = out.get(time_key)
        if not raw:
            continue
        out[bar_key] = _bar_index(df, str(raw))
    return out


def _price_bounds_for_row(df: pd.DataFrame, row: dict, lo: int, hi: int) -> tuple[float, float]:
    sl = max(0, lo - 5)
    sh = min(len(df), hi + 6)
    ymin = float(df["low"].iloc[sl:sh].min())
    ymax = float(df["high"].iloc[sl:sh].max())
    for lvl in _decode_levels(row):
        price = float(lvl["price"])
        ymin = min(ymin, price)
        ymax = max(ymax, price)
    for key in ("anchor_a_price", "anchor_b_price", "fib_price"):
        val = row.get(key)
        if val not in (None, ""):
            ymin = min(ymin, float(val))
            ymax = max(ymax, float(val))
    return ymin, ymax


def _warn_row_data_alignment(df: pd.DataFrame, row: dict, *, stored_event_bar: int | None) -> None:
    eb = int(row["event_bar"])
    if not 0 <= eb < len(df):
        print(f"WARNING: event_bar {eb} outside candle cache (len={len(df)}).")
        return
    bar = df.iloc[eb]
    fib_price = float(row["fib_price"])
    lo, hi = float(bar["low"]), float(bar["high"])
    if fib_price < lo * 0.5 or fib_price > hi * 2.0:
        print(
            "WARNING: fib price "
            f"{fib_price:g} far from event candle range {lo:g}–{hi:g} on {bar.name.date()}. "
            "Candle cache may not cover the human-fib era — fetch longer 1d history and "
            "regenerate the review pack."
        )
    if stored_event_bar is not None and stored_event_bar != eb:
        print(
            f"NOTE: event_bar re-resolved {stored_event_bar} -> {eb} "
            f"({row.get('event_time', '')[:10]})."
        )


def _draw_fib_review_panel(ax, row: dict, *, dark_theme: bool = False) -> None:
    anchors = _anchor_points(row)
    h, low_anchor = anchors[0], anchors[1]
    _, _, leg_label, direction = _fib_leg_spec(row)
    active = str(row["fib_level"])
    relation = row.get("relation") or row.get("touch_type") or "event"
    candidate = row.get("auto_candidate", "")
    tf = row["timeframe"]
    sep = "─" * 20
    blank = ""
    lines = [
        "REVIEW PANEL",
        sep,
        "FIB LEG",
        f"  {leg_label}",
        f"  direction: {direction}",
        blank,
        "H ANCHOR",
        f"  {tf} @ {_price_label(h['price'])}",
        blank,
        "FIB LEVELS",
    ]
    for lvl in _decode_levels(row):
        ratio = str(lvl["ratio"])
        price = float(lvl["price"])
        tag = "  ◀ ACTIVE" if ratio == active else ""
        lines.append(f"  {ratio}{tag}")
        lines.append(f"    {_price_label(price)}")
    lines.extend(
        [
            blank,
            "L ANCHOR",
            f"  {tf} @ {_price_label(low_anchor['price'])}",
            sep,
            "EVENT",
            f"  ACTIVE: {active} @ {_price_label(float(row['fib_price']))}",
            f"  relation: {relation}",
            f"  candidate: {candidate}",
            f"  {active} {relation} → {candidate}",
        ]
    )
    fg = "#d6d9e0" if dark_theme else "#1a1d26"
    bg = "#1a1d26" if dark_theme else "#f8f9fb"
    ec = "#5eb3ff" if dark_theme else "#1a73e8"
    ax.text(
        1.03,
        0.98,
        "\n".join(lines),
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8.5,
        color=fg,
        family="monospace",
        linespacing=1.55,
        bbox={
            "boxstyle": "round,pad=0.6",
            "fc": bg,
            "ec": ec,
            "alpha": 0.96,
            "lw": 1.2,
        },
        zorder=20,
        clip_on=False,
    )


def _draw_view_mode_badge(ax, mode: ReviewViewMode, *, dark_theme: bool = False) -> None:
    label = _view_mode_label(mode)
    fg = "#9aa3b2" if dark_theme else "#5f6368"
    bg = "#1a1d26" if dark_theme else "#f1f3f4"
    ax.text(
        0.02,
        0.02,
        f"VIEW: {label}",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=8.5,
        color=fg,
        bbox={"boxstyle": "round,pad=0.25", "fc": bg, "ec": fg, "alpha": 0.9},
        zorder=20,
    )


def _draw_active_fib_badge(ax, row: dict, *, dark_theme: bool = False) -> None:
    active = str(row["fib_level"])
    price = float(row["fib_price"])
    fg = "#5eb3ff" if dark_theme else "#1a73e8"
    bg = "#1a1d26" if dark_theme else "white"
    ax.text(
        0.02,
        0.98,
        f"ACTIVE: {active} @ {_price_label(price)}",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=10,
        fontweight="bold",
        color=fg,
        bbox={"boxstyle": "round,pad=0.35", "fc": bg, "ec": fg, "alpha": 0.94},
        zorder=20,
    )


def _draw_event_label(ax, row: dict, *, dark_theme: bool = False, x_shift: int = 0) -> None:
    eb = _chart_x(int(row["event_bar"]), x_shift)
    price = float(row["fib_price"])
    relation = row.get("relation") or row.get("touch_type") or "event"
    label = f"{row['fib_level']} {relation} → {row['auto_candidate']}"
    accent = "#ff9f43" if dark_theme else "#e65100"
    fc = "#1a1d26" if dark_theme else "white"
    ax.annotate(
        label,
        xy=(eb, price),
        xytext=(36, 42),
        textcoords="offset points",
        fontsize=9.5,
        color=accent,
        fontweight="bold",
        ha="left",
        bbox={
            "boxstyle": "round,pad=0.35",
            "fc": fc,
            "ec": accent,
            "alpha": 0.94,
            "lw": 1.2,
        },
        arrowprops={
            "arrowstyle": "->",
            "color": accent,
            "lw": 1.4,
            "connectionstyle": "arc3,rad=0.15",
            "shrinkA": 2,
            "shrinkB": 4,
        },
        zorder=12,
    )


def render_chart(df: pd.DataFrame, row: dict, out_path: Path, cfg: HumanReviewConfig) -> Path:
    eb = int(row["event_bar"])
    view_mode = cfg.default_view_mode
    lo, hi = window_for_view(row, df, cfg, view_mode)
    sub = df.iloc[lo : hi + 1]
    x_shift = lo

    fig, ax = plt.subplots(figsize=(9, 5.5))
    fig.subplots_adjust(right=0.72)
    draw_review_candles(ax, sub, candlestick=cfg.candlestick, dark_theme=False)

    _draw_fib_leg_overlay(ax, row, lo, hi, dark_theme=False, x_shift=x_shift)
    _draw_fib_levels(ax, row, dark_theme=False)
    _draw_active_fib_badge(ax, row, dark_theme=False)
    _draw_view_mode_badge(ax, view_mode, dark_theme=False)

    eb_x = _chart_x(eb, x_shift)
    ax.axvspan(eb_x - 0.5, eb_x + 0.5, color="#ff9f43", alpha=0.16, zorder=1)
    ax.axvline(eb_x, color="#e65100", lw=1.5, alpha=0.9, zorder=4)
    ax.vlines(eb_x, df["low"].iloc[eb], df["high"].iloc[eb], color="#e65100", lw=1.6, zorder=5)
    ax.scatter(
        [eb_x],
        [df["close"].iloc[eb]],
        color="#ff9f43",
        marker="*",
        s=260,
        edgecolors="black",
        linewidths=0.7,
        zorder=8,
    )
    _draw_event_label(ax, row, dark_theme=False, x_shift=x_shift)
    _draw_anchor_labels(ax, df, row, lo, hi, color="#7e57c2", x_shift=x_shift)
    _draw_fib_review_panel(ax, row, dark_theme=False)

    ymin, ymax = _price_bounds_for_row(df, row, lo, hi)
    margin = (ymax - ymin) * 0.08 or 1.0
    ax.set_ylim(ymin - margin, ymax + margin)

    ax.set_title(
        format_review_status_lines(row, view_mode=view_mode),
        fontsize=9,
        loc="left",
        pad=8,
    )
    ax.set_xlabel("bar index")
    ax.set_xlim(-0.5, len(sub) - 0.5)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return out_path

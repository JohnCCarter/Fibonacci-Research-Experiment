"""Interactive chart review for Fibonacci level-event candidates (Hypothesis A).

Loads a ``human_review_level_events`` package and lets you pan/zoom real
candlesticks (shared mplfinance layer with PNG review) while labeling each
sample with keyboard shortcuts.

Run:
    uv run python -m fibengine.research.level_event_review_tool \\
        --run-dir experiments/review/fib_level_events/review_20260601T152524Z
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

from fibengine.core.config import DataConfig, load_settings
from fibengine.data.loader import load_candles
from fibengine.labeling.hover import HoverReadout
from fibengine.research.human_review_candles import draw_review_candles
from fibengine.research.human_review_level_events import (
    HumanReviewConfig,
    ReviewViewMode,
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
    window_for_view,
    write_review_sheets,
    xlim_for_view,
)

# human_review_level_events forces the headless "Agg" backend for PNG export.
# Importing it here leaks that backend, so an interactive window can't open
# ("FigureCanvasAgg is non-interactive"). Switch back to a GUI backend.
_INTERACTIVE_BACKENDS = ("TkAgg", "QtAgg", "Qt5Agg", "MacOSX")


def _ensure_interactive_backend() -> str | None:
    if matplotlib.get_backend().lower() != "agg":
        return matplotlib.get_backend()
    for backend in _INTERACTIVE_BACKENDS:
        try:
            plt.switch_backend(backend)
            return backend
        except Exception:
            continue
    return None


LABEL_KEYS = {
    "1": "agree",
    "2": "wrong_type",
    "3": "missed_context",
    "4": "noise",
    "5": "unclear",
}
CONF_KEYS = {"h": "high", "m": "medium", "l": "low"}


def _load_rows(run_dir: Path) -> list[dict]:
    jsonl = run_dir / "review_sample.jsonl"
    if not jsonl.exists():
        raise FileNotFoundError(f"Missing {jsonl}")
    return [
        json.loads(line) for line in jsonl.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def _data_cfg(row: dict) -> DataConfig:
    settings = load_settings()
    return settings.data.model_copy(
        update={
            "exchange": row.get("exchange") or settings.data.exchange,
            "symbol": row["symbol"],
            "timeframe": row["timeframe"],
        }
    )


def _overlay_event(
    ax,
    df: pd.DataFrame,
    row: dict,
    cfg: HumanReviewConfig,
    view_mode: ReviewViewMode,
) -> tuple[int, int]:
    lo, hi = window_for_view(row, df, cfg, view_mode)
    _draw_fib_leg_overlay(ax, row, lo, hi, dark_theme=True)
    _draw_fib_levels(ax, row, dark_theme=True)
    _draw_active_fib_badge(ax, row, dark_theme=True)
    _draw_view_mode_badge(ax, view_mode, dark_theme=True)
    eb = int(row["event_bar"])
    ax.axvspan(eb - 0.5, eb + 0.5, color="#ff9f43", alpha=0.22, zorder=1)
    ax.axvline(eb, color="#ff9f43", lw=1.6, zorder=5)
    ax.scatter(
        [eb],
        [df["close"].iloc[eb]],
        color="#ff9f43",
        marker="*",
        s=300,
        edgecolors="black",
        linewidths=0.6,
        zorder=8,
    )
    _draw_event_label(ax, row, dark_theme=True)
    _draw_anchor_labels(ax, df, row, lo, hi, color="#b388ff", dark_theme=True)
    _draw_fib_review_panel(ax, row, dark_theme=True)
    return lo, hi


def _check_candle_coverage(df: pd.DataFrame, rows: list[dict]) -> None:
    """Fail fast when review timestamps predate the loaded candle cache."""
    need: list[str] = []
    for key in ("event_time", "anchor_a_time", "anchor_b_time"):
        need.extend(str(r[key]) for r in rows if r.get(key))
    if not need:
        return
    earliest = min(pd.to_datetime(t, utc=True) for t in need)
    if earliest < df.index[0]:
        raise ValueError(
            f"Review needs candles from {earliest.date()}, but cache starts "
            f"{df.index[0].date()} ({len(df)} bars). "
            "Run: python -m fibengine.data.fetch --symbols ETH/USD --timeframes 1d --refresh "
            "then regenerate the review pack."
        )


def run_review_tool(run_dir: Path, cfg: HumanReviewConfig | None = None) -> None:
    cfg = cfg or HumanReviewConfig()
    rows = _load_rows(run_dir.resolve())
    if not rows:
        raise ValueError("No events in review_sample.jsonl")

    backend = _ensure_interactive_backend()
    if backend is None:
        raise RuntimeError(
            "No interactive matplotlib backend available (tried "
            f"{', '.join(_INTERACTIVE_BACKENDS)}). On Windows install tkinter-enabled "
            "Python, or review via REVIEW_INDEX.md + review_sample.csv instead."
        )

    df_cache: dict[tuple[str, str, str], pd.DataFrame] = {}
    idx = 0
    view_mode: ReviewViewMode = cfg.default_view_mode
    view_limits: tuple[tuple[float, float], tuple[float, float]] | None = None

    def market_key(row: dict) -> tuple[str, str, str]:
        return (row.get("exchange", ""), row["symbol"], row["timeframe"])

    def get_df(row: dict) -> pd.DataFrame:
        key = market_key(row)
        if key not in df_cache:
            df_cache[key] = load_candles(_data_cfg(row))
        return df_cache[key]

    fig, ax = plt.subplots(figsize=(16, 8))
    fig.subplots_adjust(right=0.72, top=0.88)
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#0f1117")
    hover = HoverReadout()

    def labeled_count() -> int:
        return sum(1 for r in rows if (r.get("human_label") or "").strip())

    def update_title(row: dict | None = None) -> None:
        row = row if row is not None else rows[idx]
        fig.suptitle(
            format_review_status_lines(
                row,
                index=idx + 1,
                total=len(rows),
                labeled=labeled_count(),
                view_mode=view_mode,
            ),
            color="#d6d9e0",
            fontsize=10,
            ha="left",
            x=0.06,
            y=0.98,
            family="monospace",
        )

    def redraw(*, reset_view: bool = False) -> None:
        nonlocal view_limits
        if reset_view:
            view_limits = None
        elif ax.has_data():
            view_limits = (ax.get_xlim(), ax.get_ylim())

        raw_row = rows[idx]
        df = get_df(raw_row)
        stored_event_bar = int(raw_row.get("event_bar", -1))
        row = _resolve_row_bars(df, raw_row)
        if view_limits is None:
            _warn_row_data_alignment(df, row, stored_event_bar=stored_event_bar)
        ax.clear()
        ax.set_facecolor("#0f1117")
        draw_review_candles(ax, df, candlestick=cfg.candlestick, dark_theme=True)
        lo, hi = _overlay_event(ax, df, row, cfg, view_mode)
        ax.set_xlabel("bar index", color="#9aa3b2")
        ax.tick_params(colors="#9aa3b2")
        for spine in ax.spines.values():
            spine.set_color("#3a4150")
        update_title(row)
        if view_limits is None:
            ax.set_xlim(*xlim_for_view(row, df, cfg, view_mode))
            ymin, ymax = _price_bounds_for_row(df, row, lo, hi)
            margin = (ymax - ymin) * 0.08 or 1.0
            ax.set_ylim(ymin - margin, ymax + margin)
        else:
            ax.set_xlim(view_limits[0])
            ax.set_ylim(view_limits[1])
        hover.reattach(ax, fig)
        fig.canvas.draw_idle()

    def save() -> None:
        csv_path, jsonl_path = write_review_sheets(rows, run_dir.resolve())
        print(f"Saved {len(rows)} rows -> {csv_path.name}, {jsonl_path.name}")

    def on_key(event) -> None:
        nonlocal idx, view_mode
        key = (event.key or "").lower()
        row = rows[idx]
        if key in LABEL_KEYS:
            row["human_label"] = LABEL_KEYS[key]
            print(f"  human_label = {row['human_label']}")
            redraw()
        elif key in CONF_KEYS:
            row["human_confidence"] = CONF_KEYS[key]
            print(f"  human_confidence = {row['human_confidence']}")
            redraw()
        elif key in {"right", "n", "pagedown"}:
            idx = min(len(rows) - 1, idx + 1)
            redraw(reset_view=True)
        elif key in {"left", "p", "pageup"}:
            idx = max(0, idx - 1)
            redraw(reset_view=True)
        elif key == "s":
            save()
        elif key == "g":
            view_mode = "event_zoom" if view_mode == "fib_context" else "fib_context"
            print(f"  view = {view_mode.replace('_', '-')}")
            redraw(reset_view=True)
        elif key == "z":
            redraw(reset_view=True)
        elif key == "q":
            save()
            plt.close(fig)
        elif key == "?":
            _print_help()

    def on_motion(event) -> None:
        if event.inaxes != ax:
            hover.hide()
            return
        hover.update(event, get_df(rows[idx]))

    probe_df = get_df(rows[0])
    _check_candle_coverage(probe_df, rows)

    _print_help()
    print(f"Loaded {len(rows)} events from {run_dir}")
    c0, c1 = probe_df.index[0].date(), probe_df.index[-1].date()
    print(f"Candles: {c0} .. {c1} ({len(probe_df)} bars)")

    fig.canvas.mpl_connect("key_press_event", on_key)
    fig.canvas.mpl_connect("motion_notify_event", on_motion)
    redraw(reset_view=True)
    plt.show()


def _print_help() -> None:
    print(
        "Keys: 1=agree 2=wrong_type 3=missed_context 4=noise 5=unclear | "
        "h/m/l=confidence | n/-> next p/<- prev | g=toggle fib-context/event-zoom | "
        "s=save z=reset view q=quit save+exit | pan/zoom with mouse (matplotlib toolbar)"
    )


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Interactive level-event review on real candlesticks.")
    p.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="human_review package dir (contains review_sample.jsonl)",
    )
    p.add_argument("--context-before", type=int, default=40)
    p.add_argument("--context-after", type=int, default=40)
    p.add_argument(
        "--fib-context-pad",
        type=int,
        default=15,
        help="extra bars around H/L anchors in fib-context view (#21)",
    )
    p.add_argument(
        "--default-view",
        choices=("fib_context", "event_zoom"),
        default="fib_context",
        help="starting view mode: full H/L range or tight event window (#21)",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run_review_tool(
        args.run_dir,
        HumanReviewConfig(
            context_before=args.context_before,
            context_after=args.context_after,
            fib_context_pad_bars=args.fib_context_pad,
            default_view_mode=args.default_view,
        ),
    )

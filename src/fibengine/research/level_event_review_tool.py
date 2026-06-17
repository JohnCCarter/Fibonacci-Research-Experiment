"""Interactive chart review for Fibonacci level-event candidates (Hypothesis A).

Loads a ``human_review_level_events`` package and lets you pan/zoom real
candlesticks (shared mplfinance layer with PNG review) while labeling each
sample with keyboard shortcuts.

MTF top-down flow (BTC Monthly-first):
    Each event starts at the 1M context view.  Drill down with d/u/e to move
    through the TF hierarchy before reaching the event's own timeframe.
    Higher-TF fib levels are shown as faint overlays on the event chart.

Anchor correction (Shift+H / Shift+L):
    In event-review mode, press Shift+H then click a candle to record a HIGH
    anchor correction.  Shift+L sets a LOW anchor correction.  Corrections are
    saved to <run-dir>/review_anchor_overrides.jsonl — the original fib file is
    never modified.

Multi-level sequence context:
    When multiple events in the review pack share the same fib_id (same fib
    leg, different levels), sibling events are shown as subtle diamond markers
    on the chart and a SEQUENCE summary panel appears in the lower-right corner.
    This lets the reviewer see the full fib ladder behavior — not just one
    isolated level.  No candidate logic or human fib is changed.

Run:
    uv run python -m fibengine.research.level_event_review_tool \\
        --run-dir experiments/review/fib_level_events/review_20260601T152524Z \\
        --config config/variants/settings.deep-4h.yaml
"""

from __future__ import annotations

import argparse
import datetime
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
    _price_bounds_for_row,
    _resolve_row_bars,
    _warn_row_data_alignment,
    format_review_status_lines,
    write_review_sheets,
    xlim_for_view,
)
from fibengine.research.level_event_review_tool_views import (
    TF_HIERARCHY,
    _build_fib_siblings,
    _check_candle_coverage,
    _context_xlim,
    _draw_anchor_corrections,
    _draw_context_view,
    _draw_edit_mode_badge,
    _draw_htf_overlays,
    _draw_sequence_panel,
    _draw_sibling_markers,
    _load_anchor_overrides,
    _load_human_fibs_by_tf,
    _overlay_event,
    _override_key,
    _save_anchor_overrides,
    _tf_path_str,
    _tf_rank,
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


def _data_cfg(row: dict, settings=None) -> DataConfig:
    settings = settings or load_settings()
    return settings.data.model_copy(
        update={
            "exchange": row.get("exchange") or settings.data.exchange,
            "symbol": row["symbol"],
            "timeframe": row["timeframe"],
        }
    )


# ---------------------------------------------------------------------------
# Main review tool
# ---------------------------------------------------------------------------


def run_review_tool(run_dir: Path, cfg: HumanReviewConfig | None = None, settings=None) -> None:
    cfg = cfg or HumanReviewConfig()
    settings = settings or load_settings()
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

    all_human_fibs = _load_human_fibs_by_tf()
    anchor_overrides: dict[str, dict] = _load_anchor_overrides(run_dir.resolve())
    anchor_edit_mode: str | None = None  # "H" or "L" while waiting for a click
    fib_siblings: dict[str, list[dict]] = _build_fib_siblings(rows)

    df_cache: dict[tuple[str, str, str], pd.DataFrame] = {}
    idx = 0
    ctx_tf_idx: int = 0  # index into TF_HIERARCHY; 0 = 1M (highest available)
    view_mode: ReviewViewMode = cfg.default_view_mode
    view_limits: tuple[tuple[float, float], tuple[float, float]] | None = None

    def market_key(row: dict) -> tuple[str, str, str]:
        return (row.get("exchange", ""), row["symbol"], row["timeframe"])

    def get_df(row: dict) -> pd.DataFrame:
        key = market_key(row)
        if key not in df_cache:
            df_cache[key] = load_candles(_data_cfg(row, settings))
        return df_cache[key]

    def _current_ctx_tf() -> str:
        event_tf = rows[idx]["timeframe"]
        ci = min(ctx_tf_idx, _tf_rank(event_tf))
        return TF_HIERARCHY[ci]

    fig, ax = plt.subplots(figsize=(16, 8))
    fig.subplots_adjust(right=0.72, top=0.86)
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#0f1117")
    hover = HoverReadout()

    def labeled_count() -> int:
        return sum(1 for r in rows if (r.get("human_label") or "").strip())

    def update_title(row: dict | None = None, ctx_tf: str | None = None) -> None:
        row = row if row is not None else rows[idx]
        ctx_tf = ctx_tf or _current_ctx_tf()
        path = _tf_path_str(row["timeframe"], ctx_tf)
        status = format_review_status_lines(
            row,
            index=idx + 1,
            total=len(rows),
            labeled=labeled_count(),
            view_mode=view_mode,
        )
        fig.suptitle(
            f"TF: {path}\n{status}",
            color="#d6d9e0",
            fontsize=9,
            ha="left",
            x=0.06,
            y=0.99,
            family="monospace",
        )

    def redraw(*, reset_view: bool = False) -> None:
        nonlocal view_limits
        if reset_view:
            view_limits = None
        elif ax.has_data():
            view_limits = (ax.get_xlim(), ax.get_ylim())

        raw_row = rows[idx]
        ctx_tf = _current_ctx_tf()
        event_tf = raw_row["timeframe"]

        # Load candles for the current context TF
        ctx_row = dict(raw_row, timeframe=ctx_tf)
        df = get_df(ctx_row)

        ax.clear()
        ax.set_facecolor("#0f1117")
        # Log price axis so log-scale fib levels render evenly spaced (TradingView-style).
        ax.set_yscale("log" if settings.fib.scale_mode == "log" else "linear")
        draw_review_candles(ax, df, candlestick=cfg.candlestick, dark_theme=True)
        ax.set_xlabel("bar index", color="#9aa3b2")
        ax.tick_params(colors="#9aa3b2")
        for spine in ax.spines.values():
            spine.set_color("#3a4150")

        if ctx_tf.lower() == event_tf.lower():
            # ----- EVENT-REVIEW MODE (full existing behavior) -----
            stored_event_bar = int(raw_row.get("event_bar", -1))
            row = _resolve_row_bars(df, raw_row)
            if view_limits is None:
                _warn_row_data_alignment(df, row, stored_event_bar=stored_event_bar)
            lo, hi = _overlay_event(ax, df, row, cfg, view_mode)
            _draw_htf_overlays(ax, raw_row["event_time"], all_human_fibs, ctx_tf)
            override = anchor_overrides.get(_override_key(raw_row), {})
            if override:
                _draw_anchor_corrections(ax, df, override)
            if anchor_edit_mode:
                _draw_edit_mode_badge(ax, anchor_edit_mode)
            # Multi-level sequence: show sibling events on the same fib leg
            siblings = fib_siblings.get(raw_row.get("fib_id", ""), [])
            if len(siblings) > 1:
                _draw_sibling_markers(ax, df, raw_row, siblings)
                _draw_sequence_panel(ax, raw_row, siblings)
            update_title(row, ctx_tf=ctx_tf)
            if view_limits is None:
                ax.set_xlim(*xlim_for_view(row, df, cfg, view_mode))
                ymin, ymax = _price_bounds_for_row(df, row, lo, hi)
                margin = (ymax - ymin) * 0.08 or 1.0
                ax.set_ylim(ymin - margin, ymax + margin)
        else:
            # ----- CONTEXT VIEW MODE -----
            tf_fibs = all_human_fibs.get(ctx_tf, [])
            _draw_context_view(ax, df, tf_fibs, raw_row["event_time"], ctx_tf)
            update_title(raw_row, ctx_tf=ctx_tf)
            if view_limits is None:
                lo_x, hi_x = _context_xlim(df, tf_fibs, raw_row["event_time"])
                ax.set_xlim(lo_x - 0.5, hi_x + 0.5)
                lo_i = int(max(0, lo_x))
                hi_i = int(min(len(df) - 1, hi_x))
                sub = df.iloc[lo_i : hi_i + 1]
                if not sub.empty:
                    ymin = float(sub["low"].min())
                    ymax = float(sub["high"].max())
                    margin = (ymax - ymin) * 0.10 or 1.0
                    ax.set_ylim(ymin - margin, ymax + margin)

        if view_limits is not None:
            ax.set_xlim(view_limits[0])
            ax.set_ylim(view_limits[1])

        hover.reattach(ax, fig)
        fig.canvas.draw_idle()

    def save() -> None:
        csv_path, jsonl_path = write_review_sheets(rows, run_dir.resolve())
        print(f"Saved {len(rows)} rows -> {csv_path.name}, {jsonl_path.name}")
        _save_anchor_overrides(anchor_overrides, run_dir.resolve())

    def on_key(event) -> None:
        nonlocal idx, view_mode, ctx_tf_idx, anchor_edit_mode
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
            ctx_tf_idx = 0  # reset to 1M (top) on new event
            redraw(reset_view=True)
        elif key in {"left", "p", "pageup"}:
            idx = max(0, idx - 1)
            ctx_tf_idx = 0  # reset to 1M (top) on new event
            redraw(reset_view=True)
        elif key == "d":  # drill down one TF
            event_i = _tf_rank(rows[idx]["timeframe"])
            ctx_tf_idx = min(ctx_tf_idx + 1, event_i)
            print(f"  ctx_tf = {_current_ctx_tf()}")
            redraw(reset_view=True)
        elif key == "u":  # drill up one TF
            ctx_tf_idx = max(0, ctx_tf_idx - 1)
            print(f"  ctx_tf = {_current_ctx_tf()}")
            redraw(reset_view=True)
        elif key == "e":  # jump directly to event TF
            ctx_tf_idx = _tf_rank(rows[idx]["timeframe"])
            print(f"  ctx_tf = {_current_ctx_tf()} (event TF)")
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
        elif key == "escape":
            if anchor_edit_mode:
                anchor_edit_mode = None
                print("  anchor edit cancelled")
                redraw()
        elif event.key == "H":  # Shift+H — enter high-anchor edit (only at event TF)
            if _current_ctx_tf().lower() == rows[idx]["timeframe"].lower():
                anchor_edit_mode = "H"
                print("  anchor edit: click to place HIGH anchor (Esc=cancel)")
                redraw()
        elif event.key == "L":  # Shift+L — enter low-anchor edit (only at event TF)
            if _current_ctx_tf().lower() == rows[idx]["timeframe"].lower():
                anchor_edit_mode = "L"
                print("  anchor edit: click to place LOW anchor (Esc=cancel)")
                redraw()
        elif key == "?":
            _print_help()

    def on_click(event) -> None:
        nonlocal anchor_edit_mode
        if anchor_edit_mode is None or event.inaxes != ax:
            return
        if _current_ctx_tf().lower() != rows[idx]["timeframe"].lower():
            return  # corrections only in event-review mode
        if event.xdata is None:
            return
        row = rows[idx]
        df = get_df(dict(row, timeframe=row["timeframe"]))
        bar_i = max(0, min(len(df) - 1, int(round(float(event.xdata)))))
        ts = df.index[bar_i]
        if anchor_edit_mode == "H":
            price = float(df["high"].iloc[bar_i])
            field, label = "high_anchor", "HIGH"
        else:
            price = float(df["low"].iloc[bar_i])
            field, label = "low_anchor", "LOW"
        key = _override_key(row)
        if key not in anchor_overrides:
            anchor_overrides[key] = {
                "fib_id": row.get("fib_id", ""),
                "event_time": row.get("event_time", ""),
                "based_on_fib_id": row.get("fib_id", ""),
                "source": "review_tool_correction",
                "corrected_by": "human",
                "corrected_at": datetime.datetime.now(tz=datetime.UTC).isoformat(),
            }
        anchor_overrides[key][field] = {"time": ts.isoformat(), "price": price}
        anchor_overrides[key]["corrected_at"] = datetime.datetime.now(tz=datetime.UTC).isoformat()
        print(f"  {label} anchor -> {ts.date()} @ {price:.2f}")
        anchor_edit_mode = None
        redraw()

    def on_motion(event) -> None:
        if event.inaxes != ax:
            hover.hide()
            return
        ctx_tf = _current_ctx_tf()
        ctx_row = dict(rows[idx], timeframe=ctx_tf)
        hover.update(event, get_df(ctx_row))

    probe_df = get_df(rows[0])
    _check_candle_coverage(probe_df, rows)

    _print_help()
    print(f"Loaded {len(rows)} events from {run_dir}")
    c0, c1 = probe_df.index[0].date(), probe_df.index[-1].date()
    print(f"Candles: {c0} .. {c1} ({len(probe_df)} bars)")
    loaded_tfs = sorted(all_human_fibs.keys(), key=_tf_rank)
    fib_summary = ", ".join(f"{tf}({len(all_human_fibs[tf])})" for tf in loaded_tfs)
    print(f"Human fibs loaded: {fib_summary}")

    fig.canvas.mpl_connect("key_press_event", on_key)
    fig.canvas.mpl_connect("motion_notify_event", on_motion)
    fig.canvas.mpl_connect("button_press_event", on_click)
    redraw(reset_view=True)
    plt.show()


def _print_help() -> None:
    print(
        "Keys: 1=agree 2=wrong_type 3=missed_context 4=noise 5=unclear | "
        "h/m/l=confidence | n/-> next  p/<- prev | "
        "d=drill-down  u=drill-up  e=jump-to-event-TF | "
        "g=toggle fib-context/event-zoom | "
        "Shift+H=set-high-anchor  Shift+L=set-low-anchor  Esc=cancel-edit | "
        "s=save  z=reset-view  q=quit+save | pan/zoom: mouse/toolbar\n"
        "Sequence panel (lower-right): shows other fib-level interactions on same fib leg "
        "(diamond markers + SEQUENCE summary; green=held, red=broke, blue=continuation)"
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
    p.add_argument(
        "--config",
        type=str,
        default="",
        help="Settings file (e.g. config/settings.expansion.yaml).",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    from fibengine.core.config import load_settings as _ls

    run_review_tool(
        args.run_dir,
        HumanReviewConfig(
            context_before=args.context_before,
            context_after=args.context_after,
            fib_context_pad_bars=args.fib_context_pad,
            default_view_mode=args.default_view,
        ),
        settings=_ls(args.config or None),
    )

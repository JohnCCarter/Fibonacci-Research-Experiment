"""Interactive chart review for Fibonacci level-event candidates (Hypothesis A).

Loads a ``human_review_level_events`` package and lets you pan/zoom real
candlesticks (same style as :mod:`fibengine.labeling.tool`) while labeling each
sample with keyboard shortcuts.

Run:
    uv run python -m fibengine.research.level_event_review_tool \\
        --run-dir experiments/review/fib_level_events/review_20260601T152524Z
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle

from fibengine.core.config import DataConfig, load_settings
from fibengine.data.loader import load_candles
from fibengine.labeling.hover import HoverReadout
from fibengine.research.human_review_level_events import (
    HumanReviewConfig,
    _mark_swing_point,
    write_review_sheets,
)

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


def _draw_labeling_candles(ax, df: pd.DataFrame) -> None:
    """Candlesticks aligned with labeling.tool styling."""
    up_color, down_color, wick_color = "#26a69a", "#ef5350", "#c7cedb"
    width = 0.62
    for i, (_, bar) in enumerate(df.iterrows()):
        o, h, low, c = bar["open"], bar["high"], bar["low"], bar["close"]
        color = up_color if c >= o else down_color
        ax.vlines(i, low, h, color=wick_color, linewidth=0.8, alpha=0.9, zorder=2)
        body_lo, body_hi = min(o, c), max(o, c)
        if body_hi - body_lo <= 1e-12:
            ax.hlines(c, i - width / 2, i + width / 2, color=color, linewidth=1.2, zorder=3)
        else:
            ax.add_patch(
                Rectangle(
                    (i - width / 2, body_lo),
                    width,
                    body_hi - body_lo,
                    facecolor=color,
                    edgecolor=color,
                    linewidth=0.8,
                    zorder=3,
                )
            )


def _overlay_event(ax, df: pd.DataFrame, row: dict, cfg: HumanReviewConfig) -> tuple[int, int]:
    eb = int(row["event_bar"])
    lo = max(0, eb - cfg.context_before)
    hi = min(len(df) - 1, eb + cfg.context_after)
    fib_price = float(row["fib_price"])
    ax.axhline(
        fib_price,
        color="#5b9cf5",
        ls="--",
        lw=1.2,
        zorder=4,
        label=f"fib {row['fib_level']}",
    )
    ax.axvspan(eb - 0.5, eb + 0.5, color="#ff9f43", alpha=0.2, zorder=1)
    ax.axvline(eb, color="#ff9f43", lw=1.4, zorder=5)
    ax.scatter(
        [eb],
        [df["close"].iloc[eb]],
        color="#ff9f43",
        marker="*",
        s=280,
        edgecolors="black",
        linewidths=0.6,
        zorder=8,
    )
    _mark_swing_point(
        ax,
        df,
        int(row["swing_start_bar"]),
        lo,
        hi,
        marker="^",
        color="#b388ff",
        label="swing start",
    )
    _mark_swing_point(
        ax, df, int(row["swing_end_bar"]), lo, hi, marker="v", color="#b388ff", label="swing end"
    )
    return lo, hi


def run_review_tool(run_dir: Path, cfg: HumanReviewConfig | None = None) -> None:
    cfg = cfg or HumanReviewConfig()
    rows = _load_rows(run_dir.resolve())
    if not rows:
        raise ValueError("No events in review_sample.jsonl")

    df_cache: dict[tuple[str, str, str], pd.DataFrame] = {}
    idx = 0
    view_limits: tuple[tuple[float, float], tuple[float, float]] | None = None

    def market_key(row: dict) -> tuple[str, str, str]:
        return (row.get("exchange", ""), row["symbol"], row["timeframe"])

    def get_df(row: dict) -> pd.DataFrame:
        key = market_key(row)
        if key not in df_cache:
            df_cache[key] = load_candles(_data_cfg(row))
        return df_cache[key]

    fig, ax = plt.subplots(figsize=(15, 8))
    fig.patch.set_facecolor("#0f1117")
    ax.set_facecolor("#0f1117")
    hover = HoverReadout()

    def labeled_count() -> int:
        return sum(1 for r in rows if (r.get("human_label") or "").strip())

    def update_title() -> None:
        row = rows[idx]
        hl = row.get("human_label") or "—"
        hc = row.get("human_confidence") or "—"
        ax.set_title(
            f"[{idx + 1}/{len(rows)}] {row['symbol']} {row['timeframe']} | "
            f"fib {row['fib_level']} | auto={row['auto_candidate']}\n"
            f"event {row['event_time']} | human_label={hl} | confidence={hc} | "
            f"labeled {labeled_count()}/{len(rows)}",
            color="#d6d9e0",
            fontsize=10,
        )

    def redraw(*, reset_view: bool = False) -> None:
        nonlocal view_limits
        if reset_view:
            view_limits = None
        elif ax.has_data():
            view_limits = (ax.get_xlim(), ax.get_ylim())

        row = rows[idx]
        df = get_df(row)
        ax.clear()
        ax.set_facecolor("#0f1117")
        _draw_labeling_candles(ax, df)
        lo, hi = _overlay_event(ax, df, row, cfg)
        ax.set_xlabel("bar index", color="#9aa3b2")
        ax.tick_params(colors="#9aa3b2")
        for spine in ax.spines.values():
            spine.set_color("#3a4150")
        update_title()
        ax.legend(loc="upper left", fontsize=8, facecolor="#1a1d26", labelcolor="#d6d9e0")
        if view_limits is None:
            eb = int(row["event_bar"])
            pad = max(cfg.context_before, cfg.context_after, 30)
            ax.set_xlim(eb - pad, eb + pad)
            ymin = float(df["low"].iloc[max(0, lo - 5) : min(len(df), hi + 6)].min())
            ymax = float(df["high"].iloc[max(0, lo - 5) : min(len(df), hi + 6)].max())
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
        nonlocal idx
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

    _print_help()
    print(f"Loaded {len(rows)} events from {run_dir}")

    fig.canvas.mpl_connect("key_press_event", on_key)
    fig.canvas.mpl_connect("motion_notify_event", on_motion)
    redraw(reset_view=True)
    plt.show()


def _print_help() -> None:
    print(
        "Keys: 1=agree 2=wrong_type 3=missed_context 4=noise 5=unclear | "
        "h/m/l=confidence | n/→ next p/← prev | s=save z=zoom event q=quit save+exit | "
        "pan/zoom with mouse (matplotlib toolbar)"
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
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run_review_tool(
        args.run_dir,
        HumanReviewConfig(context_before=args.context_before, context_after=args.context_after),
    )

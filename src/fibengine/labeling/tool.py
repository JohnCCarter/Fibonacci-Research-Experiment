"""Interactive click tool for labeling swing high/low.

Run:
    uv run python -m fibengine.labeling.tool

Controls:
- Click sets the active point. It snaps to the nearest bar high/low.
- h: next click sets high
- l: next click sets low
- u/backspace: undo latest high/low edit
- r: clear current picks
- d: delete saved label for the active symbol/timeframe
- s: save or overwrite label
- q: quit
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from fibengine.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.labeling.store import (
    Point,
    SwingLabel,
    delete_label,
    find_label,
    save_label,
)


def _nearest_bar(df: pd.DataFrame, x: float) -> int:
    return int(min(max(round(x), 0), len(df) - 1))


def _nearest_timestamp_bar(df: pd.DataFrame, timestamp: str) -> int:
    target = pd.to_datetime(timestamp, utc=True)
    return int(df.index.get_indexer([target], method="nearest")[0])


def run_label_tool():
    settings = load_settings()
    df = load_candles(settings.data)

    picks: dict[str, tuple[int, float]] = {}
    history: list[str] = []
    active_kind = "high"

    existing = find_label(
        settings.data.exchange, settings.data.symbol, settings.data.timeframe
    )
    if existing is not None:
        picks["high"] = (
            _nearest_timestamp_bar(df, existing.high.timestamp),
            existing.high.price,
        )
        picks["low"] = (
            _nearest_timestamp_bar(df, existing.low.timestamp),
            existing.low.price,
        )
        print("Loaded existing label. Click high/low again and press 's' to overwrite.")

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(range(len(df)), df["close"].to_numpy(), color="black", lw=0.8)
    base_title = f"{settings.data.symbol} {settings.data.timeframe}"

    def update_title():
        ax.set_title(
            f"{base_title} | active={active_kind.upper()} | "
            "h/l choose, u undo, r reset, s save, d delete"
        )

    def redraw():
        for scat in list(ax.collections):
            scat.remove()
        for text in list(ax.texts):
            text.remove()
        for kind, (idx, price) in picks.items():
            color = "red" if kind == "high" else "green"
            marker = "^" if kind == "high" else "v"
            ax.scatter([idx], [price], color=color, marker=marker, s=90, zorder=5)
            ax.text(idx, price, f" {kind}", color=color, fontsize=9)
        update_title()
        fig.canvas.draw_idle()

    def on_click(event):
        nonlocal active_kind
        if event.inaxes != ax or event.xdata is None:
            return

        idx = _nearest_bar(df, event.xdata)
        if active_kind == "high":
            price = float(df["high"].iloc[idx])
            picks["high"] = (idx, price)
            history.append("high")
            print(f"HIGH @ bar {idx}, price {price}")
            active_kind = "low"
        else:
            price = float(df["low"].iloc[idx])
            picks["low"] = (idx, price)
            history.append("low")
            print(f"LOW  @ bar {idx}, price {price}")
            active_kind = "high"
        redraw()

    def on_key(event):
        nonlocal active_kind
        if event.key == "r":
            picks.clear()
            history.clear()
            print("Reset current picks.")
            redraw()
        elif event.key == "h":
            active_kind = "high"
            print("Next click sets HIGH.")
            redraw()
        elif event.key == "l":
            active_kind = "low"
            print("Next click sets LOW.")
            redraw()
        elif event.key in {"u", "backspace"}:
            if history:
                removed = history.pop()
                picks.pop(removed, None)
                active_kind = removed
                print(f"Undid {removed.upper()}.")
            redraw()
        elif event.key == "d":
            label = SwingLabel(
                exchange=settings.data.exchange,
                symbol=settings.data.symbol,
                timeframe=settings.data.timeframe,
                high=Point("", 0.0),
                low=Point("", 0.0),
            )
            deleted = delete_label(label)
            print("Deleted saved label." if deleted else "No saved label to delete.")
        elif event.key == "s":
            if "high" not in picks or "low" not in picks:
                print("Choose both high and low before saving.")
                return
            hi_idx, hi_price = picks["high"]
            lo_idx, lo_price = picks["low"]
            label = SwingLabel(
                exchange=settings.data.exchange,
                symbol=settings.data.symbol,
                timeframe=settings.data.timeframe,
                high=Point(df.index[hi_idx].isoformat(), hi_price),
                low=Point(df.index[lo_idx].isoformat(), lo_price),
            )
            path = save_label(label)
            print(f"Saved/overwrote label -> {path}")
        elif event.key == "q":
            plt.close(fig)

    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.canvas.mpl_connect("key_press_event", on_key)
    redraw()
    plt.show()


if __name__ == "__main__":
    run_label_tool()

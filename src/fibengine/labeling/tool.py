"""Interaktivt klick-verktyg för att labela swing high/low.

Kör: uv run python -m fibengine.labeling.tool
Klicka först nära din swing HIGH, sedan nära din swing LOW. Klicken snäpps till
närmaste bars high/low. Tryck 's' för att spara, 'r' för att börja om, 'q' avslut.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd

from fibengine.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.labeling.store import Point, SwingLabel, save_label


def _nearest_bar(df: pd.DataFrame, x: float) -> int:
    return int(min(max(round(x), 0), len(df) - 1))


def run_label_tool():
    settings = load_settings()
    df = load_candles(settings.data)

    picks: list[tuple[str, int, float]] = []  # (kind, bar_index, price)

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(range(len(df)), df["close"].to_numpy(), color="black", lw=0.8)
    ax.set_title(f"{settings.data.symbol} {settings.data.timeframe} — klicka HIGH sedan LOW")

    def redraw():
        for scat in list(ax.collections):
            scat.remove()
        for kind, idx, price in picks:
            color = "red" if kind == "high" else "green"
            ax.scatter([idx], [price], color=color, s=80, zorder=5)
        fig.canvas.draw_idle()

    def on_click(event):
        if event.inaxes != ax or event.xdata is None:
            return
        idx = _nearest_bar(df, event.xdata)
        if len(picks) == 0:
            price = float(df["high"].iloc[idx])
            picks.append(("high", idx, price))
            print(f"HIGH @ bar {idx}, pris {price}")
        elif len(picks) == 1:
            price = float(df["low"].iloc[idx])
            picks.append(("low", idx, price))
            print(f"LOW  @ bar {idx}, pris {price}")
        else:
            print("Båda redan valda — tryck 'r' för att börja om.")
        redraw()

    def on_key(event):
        if event.key == "r":
            picks.clear()
            print("Återställt.")
            redraw()
        elif event.key == "s":
            if len(picks) < 2:
                print("Välj både high och low innan du sparar.")
                return
            _, hi_idx, hi_price = picks[0]
            _, lo_idx, lo_price = picks[1]
            label = SwingLabel(
                exchange=settings.data.exchange,
                symbol=settings.data.symbol,
                timeframe=settings.data.timeframe,
                high=Point(df.index[hi_idx].isoformat(), hi_price),
                low=Point(df.index[lo_idx].isoformat(), lo_price),
            )
            path = save_label(label)
            print(f"Sparade facit -> {path}")
        elif event.key == "q":
            plt.close(fig)

    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.canvas.mpl_connect("key_press_event", on_key)
    plt.show()


if __name__ == "__main__":
    run_label_tool()

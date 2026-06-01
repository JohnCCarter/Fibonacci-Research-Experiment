"""Read-only chart hover: crosshair price (A) and bar OHLC (B)."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib.transforms import blended_transform_factory


def _nearest_bar_index(bar_count: int, x: float) -> int:
    return int(min(max(round(x), 0), bar_count - 1))


def format_price(price: float) -> str:
    if price >= 10_000:
        return f"{price:,.2f}"
    if price >= 1:
        text = f"{price:.4f}".rstrip("0").rstrip(".")
        return text or "0"
    text = f"{price:.8f}".rstrip("0").rstrip(".")
    return text or "0"


def _ohlc_line(df: pd.DataFrame, idx: int) -> str:
    row = df.iloc[idx]
    ts = df.index[idx]
    ts_text = ts.strftime("%Y-%m-%d %H:%M") if hasattr(ts, "strftime") else str(ts)
    return (
        f"bar {idx}  {ts_text}  "
        f"O {format_price(float(row['open']))}  "
        f"H {format_price(float(row['high']))}  "
        f"L {format_price(float(row['low']))}  "
        f"C {format_price(float(row['close']))}"
    )


@dataclass
class HoverReadout:
    """Crosshair + OHLC overlay; reattach after ``ax.clear()`` in redraw."""

    hline: Line2D | None = None
    vline: Line2D | None = None
    y_label: Text | None = None
    ohlc_label: Text | None = None
    _ax: Axes | None = field(default=None, repr=False)
    _fig: Figure | None = field(default=None, repr=False)

    def reattach(self, ax: Axes, fig: Figure) -> None:
        self._ax = ax
        self._fig = fig
        self.hline = ax.axhline(
            0,
            color="#8a93a8",
            ls="--",
            lw=0.75,
            alpha=0.85,
            visible=False,
            zorder=10,
        )
        self.vline = ax.axvline(
            0,
            color="#8a93a8",
            ls="--",
            lw=0.75,
            alpha=0.85,
            visible=False,
            zorder=10,
        )
        y_trans = blended_transform_factory(ax.transAxes, ax.transData)
        self.y_label = ax.text(
            1.01,
            0,
            "",
            transform=y_trans,
            color="#e8ebf2",
            fontsize=9,
            va="center",
            ha="left",
            visible=False,
            zorder=11,
            clip_on=False,
        )
        self.ohlc_label = fig.text(
            0.01,
            0.99,
            "",
            transform=fig.transFigure,
            color="#b8bfd0",
            fontsize=9,
            va="top",
            ha="left",
            visible=False,
        )

    def hide(self) -> None:
        for artist in (self.hline, self.vline, self.y_label, self.ohlc_label):
            if artist is not None:
                artist.set_visible(False)
        if self._fig is not None:
            self._fig.canvas.draw_idle()

    def update(self, event, df: pd.DataFrame) -> None:
        if self._ax is None or self._fig is None:
            return
        ax = self._ax
        if event.inaxes != ax or event.xdata is None or event.ydata is None or len(df) == 0:
            self.hide()
            return
        if any(
            artist is None for artist in (self.hline, self.vline, self.y_label, self.ohlc_label)
        ):
            self.reattach(ax, self._fig)

        idx = _nearest_bar_index(len(df), float(event.xdata))
        y = float(event.ydata)
        price_text = format_price(y)

        self.hline.set_ydata([y, y])
        self.hline.set_visible(True)
        self.vline.set_xdata([idx, idx])
        self.vline.set_visible(True)

        self.y_label.set_position((1.01, y))
        self.y_label.set_text(f"  {price_text}")
        self.y_label.set_visible(True)

        self.ohlc_label.set_text(_ohlc_line(df, idx))
        self.ohlc_label.set_visible(True)

        self._fig.canvas.draw_idle()

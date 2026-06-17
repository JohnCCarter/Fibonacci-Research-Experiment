"""Plotta candles + predikterad swing/fib mot manuellt facit."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless-säkert
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from fibengine.core.fib import fib_levels  # noqa: E402
from fibengine.core.models import Swing  # noqa: E402
from fibengine.labeling.store import SwingLabel  # noqa: E402
from fibengine.research.human_review_candles import draw_review_candles  # noqa: E402


def _nearest_bar(df: pd.DataFrame, ts: str) -> int:
    target = pd.to_datetime(ts, utc=True)
    return int(np.argmin(np.abs((df.index - target).total_seconds())))


def plot_prediction(
    df: pd.DataFrame,
    swing: Swing,
    levels: list[float],
    out_path: Path,
    label: SwingLabel | None = None,
    title: str = "",
    *,
    candlestick: bool = False,
    dark_theme: bool = False,
) -> Path:
    fig, ax = plt.subplots(figsize=(14, 7))
    # Shared rendering primitive (same palette/path as the review charts). Default
    # ``candlestick=False`` keeps the close-line behaviour and only needs a ``close``
    # column; ``candlestick=True`` requires full OHLCV (see human_review_candles).
    draw_review_candles(ax, df, candlestick=candlestick, dark_theme=dark_theme)

    # Predikterad leg + fib-nivåer. Provisorisk = streckad, bekräftad = heldragen.
    leg_style = "--" if swing.status == "provisional" else "-"
    ax.plot(
        [swing.start.index, swing.end.index],
        [swing.start.price, swing.end.price],
        color="tab:blue",
        lw=2,
        ls=leg_style,
        marker="o",
        label=f"predikterad leg [{swing.status}]",
    )
    for lvl, price in fib_levels(swing, levels).items():
        ax.axhline(price, color="tab:blue", ls="--", lw=0.6, alpha=0.6)
        ax.text(len(df) - 1, price, f" {lvl}", color="tab:blue", va="center", fontsize=8)

    # Manuellt facit.
    if label is not None:
        man_high_bar = _nearest_bar(df, label.high.timestamp)
        man_low_bar = _nearest_bar(df, label.low.timestamp)
        ax.scatter(
            [man_high_bar], [label.high.price], color="red", s=90, zorder=6, label="facit high"
        )
        ax.scatter(
            [man_low_bar], [label.low.price], color="green", s=90, zorder=6, label="facit low"
        )

    base_title = title or "Predikterad swing/fib vs facit"
    ax.set_title(f"{base_title} [{swing.status}]")
    ax.legend(loc="best", fontsize=8)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return out_path

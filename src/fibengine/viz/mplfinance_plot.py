"""Candlestick-plotting via mplfinance."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import pandas as pd

from fibengine.core.fib import fib_levels
from fibengine.core.models import Swing
from fibengine.labeling.store import SwingLabel


def _nearest_bar(df: pd.DataFrame, ts: str) -> int:
    target = pd.to_datetime(ts, utc=True)
    return int(np.argmin(np.abs((df.index - target).total_seconds())))


def plot_prediction_mplfinance(
    df: pd.DataFrame,
    swing: Swing,
    levels: list[float],
    out_path: Path,
    label: SwingLabel | None = None,
    title: str = "",
) -> Path:
    volume = "volume" in df.columns and bool(df["volume"].notna().any())
    fig, axes = mpf.plot(
        df,
        type="candle",
        style="yahoo",
        volume=volume,
        returnfig=True,
        figscale=1.15,
        title=(title or "Predikterad swing/fib vs facit") + f" [{swing.status}]",
        ylabel="price",
    )
    ax = axes[0]
    leg_style = "--" if swing.status == "provisional" else "-"
    ax.plot(
        [df.index[swing.start.index], df.index[swing.end.index]],
        [swing.start.price, swing.end.price],
        color="tab:blue",
        lw=2,
        ls=leg_style,
        marker="o",
        label=f"predikterad leg [{swing.status}]",
    )
    for lvl, price in fib_levels(swing, levels).items():
        ax.axhline(price, color="tab:blue", ls="--", lw=0.6, alpha=0.6)
        ax.annotate(
            f" {lvl}",
            xy=(df.index[-1], price),
            xytext=(4, 0),
            textcoords="offset points",
            color="tab:blue",
            va="center",
            fontsize=8,
        )

    if label is not None:
        ax.scatter(
            [df.index[_nearest_bar(df, label.high.timestamp)]],
            [label.high.price],
            color="red",
            s=90,
            zorder=6,
            label="facit high",
        )
        ax.scatter(
            [df.index[_nearest_bar(df, label.low.timestamp)]],
            [label.low.price],
            color="green",
            s=90,
            zorder=6,
            label="facit low",
        )

    ax.legend(loc="best", fontsize=8)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return out_path

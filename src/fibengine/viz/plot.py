"""Plotta candles + predikterad swing/fib mot manuellt facit."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from fibengine.core.models import Swing
from fibengine.labeling.store import SwingLabel


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
) -> Path:
    from fibengine.viz.mplfinance_plot import plot_prediction_mplfinance

    return plot_prediction_mplfinance(df, swing, levels, out_path, label=label, title=title)

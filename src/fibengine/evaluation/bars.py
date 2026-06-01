"""Bar index lookup for evaluation (shared by metrics, pivot_recall, MTF layer)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def _median_interval_seconds(df: pd.DataFrame) -> float:
    if len(df.index) < 2:
        return float("inf")
    deltas = np.diff(df.index.view("int64")) / 1e9
    return float(np.median(deltas))


def bar_of_timestamp(df: pd.DataFrame, ts: str) -> tuple[int, bool]:
    """Nearest bar index and whether the timestamp lies in the loaded window."""
    target = pd.to_datetime(ts, utc=True)
    if len(df.index) == 0:
        return 0, False
    dist = np.abs((df.index - target).total_seconds())
    idx = int(np.argmin(dist))
    half_interval = _median_interval_seconds(df) / 2.0
    in_range = df.index.min() <= target <= df.index.max()
    in_window = bool(in_range and dist[idx] <= half_interval)
    return idx, in_window

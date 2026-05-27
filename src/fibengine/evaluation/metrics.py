"""Mät hur nära en predikterad swing ligger det manuella facit."""

from __future__ import annotations

import numpy as np
import pandas as pd

from fibengine.config import EvaluationConfig
from fibengine.fib import fib_from_prices
from fibengine.labeling.store import SwingLabel
from fibengine.models import Swing


def _bar_of_timestamp(df: pd.DataFrame, ts: str) -> int:
    target = pd.to_datetime(ts, utc=True)
    return int(np.argmin(np.abs((df.index - target).total_seconds())))


def _predicted_high_low(swing: Swing) -> tuple[float, float]:
    if swing.start.kind == "high":
        return swing.start.price, swing.end.price
    return swing.end.price, swing.start.price


def _predicted_high_low_bars(swing: Swing) -> tuple[int, int]:
    if swing.start.kind == "high":
        return swing.start.index, swing.end.index
    return swing.end.index, swing.start.index


def evaluate(
    df: pd.DataFrame,
    swing: Swing,
    label: SwingLabel,
    atr_value: float,
    cfg: EvaluationConfig,
) -> dict:
    """Returnera fel-mått + hit-flaggor för en prediktion mot facit."""
    pred_high, pred_low = _predicted_high_low(swing)
    pred_high_bar, pred_low_bar = _predicted_high_low_bars(swing)

    man_high_bar = _bar_of_timestamp(df, label.high.timestamp)
    man_low_bar = _bar_of_timestamp(df, label.low.timestamp)

    high_price_err = abs(pred_high - label.high.price) / atr_value
    low_price_err = abs(pred_low - label.low.price) / atr_value
    high_time_err = abs(pred_high_bar - man_high_bar)
    low_time_err = abs(pred_low_bar - man_low_bar)

    # Fib-nivå-överensstämmelse på nyckelnivåerna.
    key_levels = [0.382, 0.5, 0.618]
    pred_fib = fib_from_prices(pred_low, pred_high, key_levels)
    man_fib = fib_from_prices(label.low.price, label.high.price, key_levels)
    man_range = abs(label.high.price - label.low.price) or float("nan")
    fib_errs = {
        lvl: abs(pred_fib[lvl] - man_fib[lvl]) / man_range for lvl in key_levels
    }
    mean_fib_err = float(np.mean(list(fib_errs.values())))

    price_hit = (
        high_price_err <= cfg.price_tol_atr and low_price_err <= cfg.price_tol_atr
    )
    time_hit = high_time_err <= cfg.time_tol_bars and low_time_err <= cfg.time_tol_bars
    fib_hit = mean_fib_err <= cfg.fib_level_tol

    return {
        "high_price_err_atr": round(high_price_err, 4),
        "low_price_err_atr": round(low_price_err, 4),
        "high_time_err_bars": high_time_err,
        "low_time_err_bars": low_time_err,
        "mean_fib_err_frac": round(mean_fib_err, 4),
        "price_hit": price_hit,
        "time_hit": time_hit,
        "fib_hit": fib_hit,
        "overall_hit": bool(price_hit and time_hit and fib_hit),
    }

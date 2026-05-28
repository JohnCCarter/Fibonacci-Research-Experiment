"""Mät hur väl en predikterad swing *håller med* dina exempel.

Exemplen är referens, inte domare: vi rapporterar en kontinuerlig `agreement`
∈ [0, 1] för sanity — vi optimerar aldrig vikter mot den. Tolerans-värdena i
EvaluationConfig är mjuka skalor i exponentiell avklingning, inte pass/fail.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from fibengine.core.config import EvaluationConfig
from fibengine.core.fib import fib_from_prices
from fibengine.core.models import Swing
from fibengine.labeling.store import SwingLabel


def _median_interval_seconds(df: pd.DataFrame) -> float:
    if len(df.index) < 2:
        return float("inf")
    deltas = np.diff(df.index.view("int64")) / 1e9  # ns -> s
    return float(np.median(deltas))


def _bar_of_timestamp(df: pd.DataFrame, ts: str) -> tuple[int, bool]:
    """Närmaste bar + om tidsstämpeln faktiskt ligger i fönstret.

    `argmin` snäpper alltid till en kant-bar; utan fönsterkoll skulle en label
    utanför det laddade datat tyst jämföras mot fel bar (skräpmått). Vi flaggar
    därför out-of-window: target utanför [min, max] eller > ½ candle-intervall
    från närmaste bar (in-window-labels ligger på exakta candle-tider → ~0).
    """
    target = pd.to_datetime(ts, utc=True)
    dist = np.abs((df.index - target).total_seconds())
    idx = int(np.argmin(dist))
    half_interval = _median_interval_seconds(df) / 2.0
    in_range = df.index.min() <= target <= df.index.max()
    in_window = bool(in_range and dist[idx] <= half_interval)
    return idx, in_window


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
    """Returnera beskrivande fel-mått + en kontinuerlig agreement-signal."""
    pred_high, pred_low = _predicted_high_low(swing)
    pred_high_bar, pred_low_bar = _predicted_high_low_bars(swing)

    man_high_bar, high_in_window = _bar_of_timestamp(df, label.high.timestamp)
    man_low_bar, low_in_window = _bar_of_timestamp(df, label.low.timestamp)
    out_of_window = not (high_in_window and low_in_window)

    high_price_err = abs(pred_high - label.high.price) / atr_value
    low_price_err = abs(pred_low - label.low.price) / atr_value
    high_time_err = abs(pred_high_bar - man_high_bar)
    low_time_err = abs(pred_low_bar - man_low_bar)

    # Fib-nivå-överensstämmelse på nyckelnivåerna.
    key_levels = [0.382, 0.5, 0.618]
    pred_fib = fib_from_prices(pred_low, pred_high, key_levels)
    man_fib = fib_from_prices(label.low.price, label.high.price, key_levels)
    man_range = abs(label.high.price - label.low.price)
    if man_range <= 1e-12:
        fib_errs = {lvl: 0.0 for lvl in key_levels}
    else:
        fib_errs = {lvl: abs(pred_fib[lvl] - man_fib[lvl]) / man_range for lvl in key_levels}
    mean_fib_err = float(np.mean(list(fib_errs.values())))

    # Mjuk agreement: exponentiell avklingning per komponent, medelvärde i [0, 1].
    mean_price_err = (high_price_err + low_price_err) / 2.0
    mean_time_err = (high_time_err + low_time_err) / 2.0
    price_agree = np.exp(-mean_price_err / cfg.price_tol_atr)
    time_agree = np.exp(-mean_time_err / cfg.time_tol_bars)
    fib_agree = np.exp(-mean_fib_err / cfg.fib_level_tol)
    agreement = float(np.mean([price_agree, time_agree, fib_agree]))

    return {
        "high_price_err_atr": round(high_price_err, 4),
        "low_price_err_atr": round(low_price_err, 4),
        "high_time_err_bars": high_time_err,
        "low_time_err_bars": low_time_err,
        "mean_fib_err_frac": round(mean_fib_err, 4),
        "price_agree": round(float(price_agree), 4),
        "time_agree": round(float(time_agree), 4),
        "fib_agree": round(float(fib_agree), 4),
        "agreement": round(agreement, 4),
        "out_of_window": out_of_window,
    }

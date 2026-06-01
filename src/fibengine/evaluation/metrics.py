"""Mät hur väl en predikterad swing *håller med* dina exempel.

Exemplen är referens, inte domare: vi rapporterar en kontinuerlig `agreement`
∈ [0, 1] för sanity — vi optimerar aldrig vikter mot den. Tolerans-värdena i
EvaluationConfig är mjuka skalor i exponentiell avklingning, inte pass/fail.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from fibengine.core.config import EvaluationConfig, Settings, load_settings
from fibengine.core.fib import fib_from_prices, fib_levels
from fibengine.core.models import Swing
from fibengine.data.loader import load_candles
from fibengine.evaluation.bars import bar_of_timestamp
from fibengine.labeling.mtf_disambiguation import disambiguate_label_endpoints
from fibengine.labeling.store import SwingLabel


def _predicted_high_low(swing: Swing) -> tuple[float, float]:
    if swing.start.kind == "high":
        return swing.start.price, swing.end.price
    return swing.end.price, swing.start.price


def _predicted_high_low_timestamps(swing: Swing) -> tuple[str, str]:
    if swing.start.kind == "high":
        return swing.start.timestamp.isoformat(), swing.end.timestamp.isoformat()
    return swing.end.timestamp.isoformat(), swing.start.timestamp.isoformat()


def evaluate(
    df: pd.DataFrame,
    swing: Swing,
    label: SwingLabel,
    atr_value: float,
    cfg: EvaluationConfig,
    settings: Settings | None = None,
) -> dict:
    """Returnera beskrivande fel-mått + en kontinuerlig agreement-signal."""
    settings = settings or load_settings()
    endpoints = disambiguate_label_endpoints(label, df, settings)

    if endpoints.skip_evaluation:
        return {
            "high_price_err_atr": None,
            "low_price_err_atr": None,
            "high_time_err_bars": None,
            "low_time_err_bars": None,
            "mean_fib_err_frac": None,
            "price_agree": None,
            "time_agree": None,
            "fib_agree": None,
            "agreement": None,
            "out_of_window": False,
            "mtf_status": endpoints.mtf_status,
            "mtf_skip_reason": endpoints.skip_reason,
            "skipped_mtf": True,
            "same_htf_candle": endpoints.same_htf_candle,
        }

    pred_high, pred_low = _predicted_high_low(swing)
    pred_high_ts, pred_low_ts = _predicted_high_low_timestamps(swing)

    time_df = df
    if endpoints.time_df_timeframe != label.timeframe:
        time_df = load_candles(
            settings.data.model_copy(
                update={
                    "exchange": label.exchange,
                    "symbol": label.symbol,
                    "timeframe": endpoints.time_df_timeframe,
                }
            )
        )

    man_high_bar, high_in_window = bar_of_timestamp(time_df, endpoints.high_timestamp)
    man_low_bar, low_in_window = bar_of_timestamp(time_df, endpoints.low_timestamp)
    pred_high_bar, _ = bar_of_timestamp(time_df, pred_high_ts)
    pred_low_bar, _ = bar_of_timestamp(time_df, pred_low_ts)
    out_of_window = not (high_in_window and low_in_window)

    high_price_err = abs(pred_high - endpoints.high_price) / atr_value
    low_price_err = abs(pred_low - endpoints.low_price) / atr_value
    high_time_err = abs(pred_high_bar - man_high_bar)
    low_time_err = abs(pred_low_bar - man_low_bar)

    # Fib-nivå-överensstämmelse på nyckelnivåerna (temporal leg, not sorted low/high).
    key_levels = [0.382, 0.5, 0.618]
    pred_fib = fib_levels(swing, key_levels)
    man_fib = fib_from_prices(endpoints.fib_start_price, endpoints.fib_end_price, key_levels)
    man_range = abs(endpoints.high_price - endpoints.low_price)
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
        "mtf_status": endpoints.mtf_status,
        "mtf_order": endpoints.order,
        "mtf_resolution_kind": endpoints.resolution_kind,
        "same_htf_candle": endpoints.same_htf_candle,
        "skipped_mtf": False,
    }

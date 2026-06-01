"""Knyt ihop prediktion + facit för ett eller flera labelade chart."""

from __future__ import annotations

import numpy as np

from fibengine.core.config import Settings
from fibengine.core.scoring import select_swing
from fibengine.data.loader import atr, load_candles
from fibengine.evaluation.metrics import evaluate
from fibengine.labeling.store import SwingLabel


def compare_label(settings: Settings, label: SwingLabel) -> dict:
    """Kör pipelinen för en labels symbol/timeframe och jämför mot facit."""
    data_cfg = settings.data.model_copy(
        update={
            "exchange": label.exchange,
            "symbol": label.symbol,
            "timeframe": label.timeframe,
        }
    )
    df = load_candles(data_cfg)
    swing = select_swing(df, settings.pivots, settings.scoring)
    if swing is None:
        return {"label": _label_id(label), "error": "ingen swing detekterad"}

    atr_series = atr(df, settings.pivots.atr_period)
    atr_value = float(atr_series.iloc[swing.end.index])
    if not np.isfinite(atr_value) or atr_value <= 0:
        atr_value = float(np.nanmedian(atr_series.to_numpy()))

    result = evaluate(df, swing, label, atr_value, settings.evaluation, settings)
    return {
        "label": _label_id(label),
        "predicted_swing": swing.to_dict(),
        "metrics": result,
    }


def _label_id(label: SwingLabel) -> str:
    return f"{label.exchange}_{label.symbol.replace('/', '-')}_{label.timeframe}"

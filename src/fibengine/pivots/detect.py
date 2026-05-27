"""Detektera kandidat-pivots: lokala extrema filtrerade på ATR-skalad prominens."""

from __future__ import annotations

import pandas as pd

from fibengine.config import PivotConfig
from fibengine.data.loader import atr
from fibengine.models import Pivot


def detect_pivots(df: pd.DataFrame, cfg: PivotConfig) -> list[Pivot]:
    """Hitta lokala max/min över ett fönster och behåll de tillräckligt prominenta.

    Prominens mäts som avståndet från pivotpriset till den motsatta extrempunkten
    i lookback-fönstret, normaliserat mot ATR vid pivoten. Så tröskeln anpassar
    sig till volatilitet istället för ett fast prisavstånd.
    """
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()
    atr_series = atr(df, cfg.atr_period).to_numpy()
    n = len(df)
    lb = cfg.lookback
    pivots: list[Pivot] = []

    for i in range(n):
        lo = max(0, i - lb)
        hi = min(n, i + lb + 1)
        window_high = highs[lo:hi].max()
        window_low = lows[lo:hi].min()
        local_atr = atr_series[i] if atr_series[i] > 0 else float("nan")
        if local_atr != local_atr:  # NaN under uppvärmningsperioden
            continue

        if highs[i] == window_high:
            prominence = (highs[i] - window_low) / local_atr
            if prominence >= cfg.min_prominence_atr:
                pivots.append(
                    Pivot(i, df.index[i], float(highs[i]), "high", float(prominence))
                )
        if lows[i] == window_low:
            prominence = (window_high - lows[i]) / local_atr
            if prominence >= cfg.min_prominence_atr:
                pivots.append(
                    Pivot(i, df.index[i], float(lows[i]), "low", float(prominence))
                )

    return _dedupe_alternating(pivots)


def _dedupe_alternating(pivots: list[Pivot]) -> list[Pivot]:
    """Sortera på tid och kollapsa intilliggande pivots av samma typ till den mest extrema."""
    pivots = sorted(pivots, key=lambda p: p.index)
    result: list[Pivot] = []
    for p in pivots:
        if result and result[-1].kind == p.kind:
            prev = result[-1]
            keep_new = p.price > prev.price if p.kind == "high" else p.price < prev.price
            if keep_new:
                result[-1] = p
        else:
            result.append(p)
    return result

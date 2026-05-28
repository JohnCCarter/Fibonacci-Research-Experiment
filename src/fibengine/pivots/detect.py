"""Detektera kandidat-pivots: lokala extrema filtrerade på ATR-skalad prominens."""

from __future__ import annotations

import pandas as pd

from fibengine.config import PivotConfig
from fibengine.data.loader import atr
from fibengine.models import Pivot


def _is_fractal_high(highs, i: int, n_side: int, n: int) -> bool:
    """Strikt Williams-topp: high[i] strikt högre än n_side barer på varje sida."""
    if i - n_side < 0 or i + n_side >= n:
        return False
    return all(highs[i] > highs[i + k] for k in range(-n_side, n_side + 1) if k != 0)


def _is_fractal_low(lows, i: int, n_side: int, n: int) -> bool:
    if i - n_side < 0 or i + n_side >= n:
        return False
    return all(lows[i] < lows[i + k] for k in range(-n_side, n_side + 1) if k != 0)


def detect_pivots(df: pd.DataFrame, cfg: PivotConfig) -> list[Pivot]:
    """Hitta kandidat-pivots och behåll de tillräckligt prominenta.

    I "window"-läge är en pivot ett lokalt extrem över ett lookback-fönster. I
    "fractal"-läge krävs ett strikt Williams-mönster (high[i] strikt högst bland
    fractal_n barer på varje sida). I båda fallen filtreras pivots på ATR-skalad
    prominens: avståndet till den motsatta extrempunkten i lookback-fönstret,
    normaliserat mot ATR — så tröskeln följer volatiliteten.
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

        if cfg.mode == "fractal":
            is_high = _is_fractal_high(highs, i, cfg.fractal_n, n)
            is_low = _is_fractal_low(lows, i, cfg.fractal_n, n)
        else:
            is_high = highs[i] == window_high
            is_low = lows[i] == window_low

        high_prominence = (highs[i] - window_low) / local_atr if is_high else None
        low_prominence = (window_high - lows[i]) / local_atr if is_low else None
        if is_high and is_low:
            if high_prominence == low_prominence:
                continue
            is_high = high_prominence > low_prominence
            is_low = not is_high

        if is_high and high_prominence is not None:
            if high_prominence >= cfg.min_prominence_atr:
                pivots.append(
                    Pivot(i, df.index[i], float(highs[i]), "high", float(high_prominence))
                )
        if is_low and low_prominence is not None:
            if low_prominence >= cfg.min_prominence_atr:
                pivots.append(
                    Pivot(i, df.index[i], float(lows[i]), "low", float(low_prominence))
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

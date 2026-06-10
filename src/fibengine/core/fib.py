"""Beräkna Fibonacci-retracement-nivåer från en vald swing-leg."""

from __future__ import annotations

import math

from fibengine.core.models import Swing


def _calc_levels(
    anchor0: float, anchor1: float, levels: list[float], scale_mode: str
) -> dict[float, float]:
    """anchor0 = ratio-0 price, anchor1 = ratio-1 price."""
    if scale_mode == "log":
        log0 = math.log(anchor0)
        log1 = math.log(anchor1)
        return {level: math.exp(log0 + level * (log1 - log0)) for level in levels}
    span = anchor1 - anchor0
    return {level: anchor0 + level * span for level in levels}


def fib_levels(swing: Swing, levels: list[float], scale_mode: str = "linear") -> dict[float, float]:
    """Mappa varje Fib-ratio till ett retracement-pris från legens endpunkt.

    0.0 ligger vid legens end, 1.0 vid dess start. För en upp-leg (low->high)
    ger högre ratio lägre pris (retracement nedåt), och tvärtom för en ned-leg.
    """
    start, end = swing.start.price, swing.end.price
    return _calc_levels(anchor0=end, anchor1=start, levels=levels, scale_mode=scale_mode)


def fib_from_prices(
    start_price: float, end_price: float, levels: list[float], scale_mode: str = "linear"
) -> dict[float, float]:
    return _calc_levels(
        anchor0=end_price, anchor1=start_price, levels=levels, scale_mode=scale_mode
    )

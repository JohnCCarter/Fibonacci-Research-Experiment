"""Beräkna Fibonacci-retracement-nivåer från en vald swing-leg."""

from __future__ import annotations

from fibengine.models import Swing


def fib_levels(swing: Swing, levels: list[float]) -> dict[float, float]:
    """Mappa varje Fib-ratio till ett pris längs legen start -> end.

    0.0 ligger vid legens start, 1.0 vid dess end. För en upp-leg (low->high)
    ger högre ratio lägre pris (retracement nedåt), och tvärtom för en ned-leg.
    """
    start, end = swing.start.price, swing.end.price
    span = end - start
    return {level: end - level * span for level in levels}


def fib_from_prices(
    start_price: float, end_price: float, levels: list[float]
) -> dict[float, float]:
    span = end_price - start_price
    return {level: end_price - level * span for level in levels}

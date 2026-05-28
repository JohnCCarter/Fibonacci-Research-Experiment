"""Marknadsstruktur: HH/HL- och LH/LL-konsistens ur pivot-sekvensen.

Används som mjuk feature — en analytiker ritar Fib *med* strukturen
(nerifrån-upp i en HH/HL-uptrend, uppifrån-ner i en LH/LL-downtrend).
"""

from __future__ import annotations

from fibengine.core.models import Pivot


def _monotonic_fraction(values: list[float], increasing: bool) -> float:
    """Andel intilliggande par som rör sig i rätt riktning. 0.5 = neutralt/för få."""
    if len(values) < 2:
        return 0.5
    good = sum(1 for a, b in zip(values, values[1:], strict=False) if (b > a) == increasing)
    return good / (len(values) - 1)


def _recent(pivots: list[Pivot], end_index: int, window: int) -> list[Pivot]:
    relevant = [p for p in pivots if p.index <= end_index]
    return relevant[-window:]


def uptrend_alignment(pivots: list[Pivot], end_index: int, window: int) -> float:
    rec = _recent(pivots, end_index, window)
    highs = [p.price for p in rec if p.kind == "high"]
    lows = [p.price for p in rec if p.kind == "low"]
    hh = _monotonic_fraction(highs, increasing=True)
    hl = _monotonic_fraction(lows, increasing=True)
    return (hh + hl) / 2.0


def downtrend_alignment(pivots: list[Pivot], end_index: int, window: int) -> float:
    rec = _recent(pivots, end_index, window)
    highs = [p.price for p in rec if p.kind == "high"]
    lows = [p.price for p in rec if p.kind == "low"]
    lh = _monotonic_fraction(highs, increasing=False)
    ll = _monotonic_fraction(lows, increasing=False)
    return (lh + ll) / 2.0


def structure_alignment(pivots: list[Pivot], end_index: int, window: int, direction: str) -> float:
    """Hur väl legens riktning sitter i den färska strukturen. ∈ [0, 1]."""
    if direction == "up":
        return uptrend_alignment(pivots, end_index, window)
    return downtrend_alignment(pivots, end_index, window)

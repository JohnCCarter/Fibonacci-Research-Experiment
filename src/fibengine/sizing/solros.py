"""Lager B: 'solros'-sizing — Fibonacci-skalad positionsuppbyggnad.

Frikopplat från swing-urvalet (Lager A). Tar en vald swing och bygger en plan
med skalade entries i retracement-nivåerna; störst storlek i gyllene zonen.
Ren simulering/illustration — ingen broker, ingen koppling till urvalets score.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from fibengine.config import SizingConfig
from fibengine.fib import fib_levels
from fibengine.models import Swing


@dataclass
class Entry:
    ratio: float
    price: float
    size: float
    filled: bool = False
    fill_bar: int | None = None

    def to_dict(self) -> dict:
        return {
            "ratio": self.ratio,
            "price": round(self.price, 4),
            "size": self.size,
            "filled": self.filled,
            "fill_bar": self.fill_bar,
        }


def build_sizing_plan(swing: Swing, cfg: SizingConfig) -> list[Entry]:
    """Skala in i retracement-nivåerna; sista (gyllene zonen) får störst storlek."""
    prices = fib_levels(swing, cfg.entry_levels)
    return [
        Entry(ratio=lvl, price=prices[lvl], size=size)
        for lvl, size in zip(cfg.entry_levels, cfg.sizes, strict=True)
    ]


def simulate_plan(df: pd.DataFrame, swing: Swing, plan: list[Entry]) -> list[Entry]:
    """Markera vilka entries pris retracade in i efter legens slut (illustrativt)."""
    start_bar = max(swing.start.index, swing.end.index)
    highs = df["high"].to_numpy()
    lows = df["low"].to_numpy()
    for entry in plan:
        for b in range(start_bar + 1, len(df)):
            if lows[b] <= entry.price <= highs[b]:
                entry.filled = True
                entry.fill_bar = b
                break
    return plan

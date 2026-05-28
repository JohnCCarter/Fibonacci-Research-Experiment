"""Delade datatyper för pivots och swing-legs."""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class Pivot:
    index: int  # bar-position i serien
    timestamp: pd.Timestamp
    price: float
    kind: str  # "high" eller "low"
    prominence: float  # ATR-skalad prominens

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp.isoformat(),
            "price": self.price,
            "kind": self.kind,
            "prominence": round(self.prominence, 4),
        }


@dataclass
class Swing:
    """En leg mellan två pivots av motsatt typ. Fib ritas från start -> end."""

    start: Pivot
    end: Pivot
    features: dict[str, float] = field(default_factory=dict)
    score: float = 0.0
    status: str = "unknown"  # "confirmed", "provisional" eller "unknown"

    @property
    def direction(self) -> str:
        return "up" if self.end.price > self.start.price else "down"

    @property
    def price_range(self) -> float:
        return abs(self.end.price - self.start.price)

    @property
    def bars(self) -> int:
        return abs(self.end.index - self.start.index)

    def to_dict(self) -> dict:
        return {
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "direction": self.direction,
            "price_range": round(self.price_range, 4),
            "bars": self.bars,
            "features": {k: round(v, 4) for k, v in self.features.items()},
            "score": round(self.score, 4),
            "status": self.status,
        }

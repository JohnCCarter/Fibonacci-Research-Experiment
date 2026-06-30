"""Chamoun structure engine v1 — propose down-structures the way Chamoun draws them.

Descriptive proposer (NOT a live/causal signal): given OHLC + detected pivots, it proposes the
down-structures a human-like drawer would anchor — origin ("1") = the swing high the move came
from, reached ("0") = the low it fell to before the structure is invalidated.

Calibrated on Chamoun's dated 1h facit (2026-06-30): each of his four clean down-origins is the
single most-prominent swing high at a ~3-day (72-bar) scale, in neutral (non-circular) windows.
This engine encodes that rule and re-finds all four. Acceptance bar = recognizably-similar + right
region, not tick-exact (Chamoun, 2026-06-30): the origin must land; the reached "0" is approximate.

FROZEN v1 PARAMS (pre-registered 2026-06-30; do NOT tune against future facit — lock-before-test):
  local_scale = 72 bars (~3 days): origin must be the max-prominence high within +/-local_scale
  min_move    = 0.02 (2%): structure must fall >= min_move from origin to its reached low
  max_horizon = 480 bars (20 days): cap if the structure is never invalidated
  min_bars    = 3: drop moves whose low is reached within < min_bars (early-spike guard)
  break rule  : structure ends at the first bar that CLOSES above the origin high (invalidation)
  reached "0" : lowest low from origin until the break

DIRECTION: down only (origin=high). UP + the 2nd-layer volume/clarity tie-break are DEFERRED.
KNOWN GAP: reached "0" takes the lowest low, but Chamoun anchors the later *sustained* low (his Q2);
  for sharp early-spike drops the "0" sits on the first spike, not his later anchor. Next layer.

Usage::

    python -m fibengine.research.chamoun_structure_engine \\
        --config config/variants/settings.1h_recent.yaml --recent 14
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np
import pandas as pd

from fibengine.core.config import load_settings
from fibengine.core.models import Pivot
from fibengine.pivots.detect import detect_pivots


@dataclass(frozen=True)
class StructureConfig:
    """Pre-registered v1 parameters. Frozen on purpose — do not tune against future facit."""

    local_scale: int = 72
    min_move: float = 0.02
    max_horizon: int = 480
    min_bars: int = 3


DEFAULT_CONFIG = StructureConfig()


@dataclass(frozen=True)
class Structure:
    """A proposed down-structure: anchor "1" = origin high, anchor "0" = reached low."""

    origin_index: int
    origin_ts: pd.Timestamp
    origin_price: float
    reached_index: int
    reached_ts: pd.Timestamp
    reached_price: float
    prominence: float
    active: bool  # True = never invalidated within the horizon (still "live" at its right edge)
    direction: str = "down"

    @property
    def move(self) -> float:
        return (self.origin_price - self.reached_price) / self.origin_price

    @property
    def bars(self) -> int:
        return self.reached_index - self.origin_index

    def to_dict(self) -> dict:
        return {
            "direction": self.direction,
            "origin": {
                "index": self.origin_index,
                "time": self.origin_ts.isoformat(),
                "price": self.origin_price,
            },
            "reached": {
                "index": self.reached_index,
                "time": self.reached_ts.isoformat(),
                "price": self.reached_price,
            },
            "move": round(self.move, 4),
            "bars": self.bars,
            "prominence": round(self.prominence, 4),
            "active": self.active,
        }


def propose_structures(
    df: pd.DataFrame,
    pivots: list[Pivot],
    config: StructureConfig = DEFAULT_CONFIG,
) -> list[Structure]:
    """Propose Chamoun-style down-structures from OHLC + detected pivots.

    An origin qualifies when its high pivot is the max-prominence high within +/-local_scale bars.
    The structure runs until the first bar that *closes* above the origin high (invalidation); its
    reached "0" is the lowest low over that span. Degenerate (``< min_bars``) and small
    (``< min_move``) moves are dropped. Pure read — mutates nothing.
    """
    highs = [p for p in pivots if p.kind == "high"]
    if not highs:
        return []
    hi_index = np.array([p.index for p in highs])
    hi_prom = np.array([p.prominence for p in highs])
    high = df["high"].to_numpy()
    low = df["low"].to_numpy()
    close = df["close"].to_numpy()
    n = len(df)

    out: list[Structure] = []
    for k, p in enumerate(highs):
        i = p.index
        in_scale = (hi_index >= i - config.local_scale) & (hi_index <= i + config.local_scale)
        if hi_prom[k] < hi_prom[in_scale].max():
            continue  # a more prominent high sits within the local scale — not a dominant origin
        end = min(i + config.max_horizon, n - 1)
        broken = False
        brk = end
        for b in range(i + 1, end + 1):
            if close[b] > high[i]:
                brk, broken = b, True
                break
        if brk - i < config.min_bars:
            continue
        j = i + 1 + int(np.argmin(low[i + 1 : brk + 1]))
        reached = float(low[j])
        if j - i < config.min_bars:
            continue  # low reached too fast (early-spike degenerate)
        if (high[i] - reached) / high[i] < config.min_move:
            continue
        out.append(
            Structure(
                origin_index=i,
                origin_ts=df.index[i],
                origin_price=float(high[i]),
                reached_index=j,
                reached_ts=df.index[j],
                reached_price=reached,
                prominence=float(p.prominence),
                active=not broken,
            )
        )
    return out


def propose_from_settings(
    config_path: str | None = None,
    config: StructureConfig = DEFAULT_CONFIG,
) -> list[Structure]:
    """Load OHLC via settings, detect pivots, and propose structures (CLI convenience)."""
    from fibengine.data.loader import load_candles

    settings = load_settings(config_path)
    df = load_candles(settings.data, fetch_if_missing=False)
    pivots = detect_pivots(df, settings.pivots)
    return propose_structures(df, pivots, config)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Propose Chamoun-style down-structures (descriptive).")
    p.add_argument(
        "--config",
        default=None,
        help="settings YAML (e.g. config/variants/settings.1h_recent.yaml)",
    )
    p.add_argument("--recent", type=int, default=14, help="How many most-recent proposals to print")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    structures = propose_from_settings(args.config)
    print(f"proposed DOWN structures: {len(structures)}  (frozen v1 {DEFAULT_CONFIG})")
    recent = sorted(structures, key=lambda s: s.origin_ts, reverse=True)[: args.recent]
    for s in recent:
        print(
            f"  origin {str(s.origin_ts)[:13]} {s.origin_price:>9.0f} -> "
            f"reached {str(s.reached_ts)[:13]} {s.reached_price:>9.0f} "
            f"move={s.move:>6.1%} prom={s.prominence:>4.1f} bars={s.bars:>4} "
            f"{'ACTIVE' if s.active else 'broken'}"
        )


if __name__ == "__main__":
    main()

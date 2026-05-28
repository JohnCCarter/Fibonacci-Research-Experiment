"""Feature-extraktion per swing-leg. Förklarbara, jämförbara features."""

from __future__ import annotations

import numpy as np
import pandas as pd

from fibengine.core.config import ScoringConfig
from fibengine.core.models import Pivot, Swing
from fibengine.core.scale import endpoint_confluence
from fibengine.core.structure import structure_alignment


def enumerate_swings(pivots: list[Pivot], max_legs: int) -> list[Swing]:
    """Bygg kandidat-legs av alla par (i<j) av motsatt pivot-typ.

    Vi prioriterar de senaste legs (de mest relevanta för en analytiker) och
    kapar antalet vid max_legs.
    """
    legs: list[Swing] = []
    for i in range(len(pivots)):
        for j in range(i + 1, len(pivots)):
            if pivots[i].kind != pivots[j].kind:
                legs.append(Swing(start=pivots[i], end=pivots[j]))
    legs.sort(key=lambda s: s.end.index, reverse=True)
    return legs[:max_legs]


def _round_number_proximity(price: float) -> float:
    """1.0 om priset ligger exakt på ett 'runt' steg, mot 0 längre bort."""
    if price <= 0:
        return 0.0
    step = 10 ** (np.floor(np.log10(price)) - 1)  # ~1% av prisskalan
    nearest = round(price / step) * step
    frac = abs(price - nearest) / step
    return max(0.0, 1.0 - 2 * frac)


def _cleanliness(df: pd.DataFrame, swing: Swing) -> float:
    """Effektivitet: netto-rörelse / total väg. 1.0 = spikrak leg."""
    lo, hi = sorted((swing.start.index, swing.end.index))
    closes = df["close"].to_numpy()[lo : hi + 1]
    if len(closes) < 2:
        return 1.0
    path = np.abs(np.diff(closes)).sum()
    if path == 0:
        return 1.0
    return float(abs(closes[-1] - closes[0]) / path)


def compute_features(
    df: pd.DataFrame,
    swing: Swing,
    atr_series: pd.Series,
    cfg: ScoringConfig,
    pivots: list[Pivot] | None = None,
    multi_pivots: dict[int, list[Pivot]] | None = None,
) -> dict[str, float]:
    n = len(df)
    end_atr = atr_series.iloc[swing.end.index]
    if not np.isfinite(end_atr) or end_atr <= 0:
        end_atr = float(np.nanmedian(atr_series.to_numpy()))

    # Mättande magnitude: stora moves är bra, men avtagande — så att en
    # gigantisk leg över hela chartet inte automatiskt slår en relevant, färsk leg.
    magnitude = float(np.tanh((swing.price_range / end_atr) / cfg.magnitude_scale_atr))
    recency = swing.end.index / (n - 1) if n > 1 else 1.0
    prominence = float(np.tanh((swing.start.prominence + swing.end.prominence) / 4.0))
    cleanliness = _cleanliness(df, swing)
    round_number = (
        _round_number_proximity(swing.start.price) + _round_number_proximity(swing.end.price)
    ) / 2.0
    duration = abs(swing.bars - cfg.duration_target) / max(cfg.duration_target, 1)
    structure = (
        structure_alignment(pivots, swing.end.index, cfg.structure_window, swing.direction)
        if pivots
        else 0.5
    )
    confluence = (
        endpoint_confluence(swing, multi_pivots, cfg.confluence_tol_bars) if multi_pivots else 0.5
    )

    return {
        "magnitude": float(magnitude),
        "recency": float(recency),
        "prominence": float(prominence),
        "cleanliness": float(cleanliness),
        "round_number": float(round_number),
        "duration": float(duration),
        "structure_alignment": float(structure),
        "scale_confluence": float(confluence),
    }

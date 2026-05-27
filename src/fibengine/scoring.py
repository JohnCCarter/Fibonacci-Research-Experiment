"""Viktad förklarbar poängsättning av swing-legs och val av bästa leg."""

from __future__ import annotations

import pandas as pd

from fibengine.config import PivotConfig, ScoringConfig
from fibengine.data.loader import atr
from fibengine.features import compute_features, enumerate_swings
from fibengine.models import Swing
from fibengine.pivots.detect import detect_pivots


def score_swing(swing: Swing, weights: dict[str, float]) -> float:
    """Linjär kombination: score = Σ vikt_k · feature_k. Helt förklarbar."""
    return sum(weights.get(k, 0.0) * v for k, v in swing.features.items())


def rank_swings(
    df: pd.DataFrame, pivot_cfg: PivotConfig, scoring_cfg: ScoringConfig
) -> list[Swing]:
    """Detektera pivots, bygg kandidat-legs, poängsätt och returnera sorterade."""
    pivots = detect_pivots(df, pivot_cfg)
    legs = enumerate_swings(pivots, scoring_cfg.max_candidate_legs)
    atr_series = atr(df, pivot_cfg.atr_period)
    for leg in legs:
        leg.features = compute_features(df, leg, atr_series, scoring_cfg)
        leg.score = score_swing(leg, scoring_cfg.weights)
    legs.sort(key=lambda s: s.score, reverse=True)
    return legs


def select_swing(
    df: pd.DataFrame, pivot_cfg: PivotConfig, scoring_cfg: ScoringConfig
) -> Swing | None:
    """Välj den swing-leg analytikern sannolikt hade ritat Fib på."""
    ranked = rank_swings(df, pivot_cfg, scoring_cfg)
    return ranked[0] if ranked else None

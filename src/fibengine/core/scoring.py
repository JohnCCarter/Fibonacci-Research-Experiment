"""Viktad förklarbar poängsättning av swing-legs och val av bästa leg."""

from __future__ import annotations

import pandas as pd

from fibengine.core.config import PivotConfig, ScoringConfig
from fibengine.core.confirm import classify_swing
from fibengine.core.features import compute_features, enumerate_swings
from fibengine.core.models import Swing
from fibengine.core.scale import detect_pivots_multi
from fibengine.data.loader import atr
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
    multi_pivots = detect_pivots_multi(df, pivot_cfg, scoring_cfg.confluence_degrees)
    for leg in legs:
        leg.features = compute_features(df, leg, atr_series, scoring_cfg, pivots, multi_pivots)
        leg.score = score_swing(leg, scoring_cfg.weights)
    legs.sort(key=lambda s: s.score, reverse=True)
    return legs


def select_swing(
    df: pd.DataFrame, pivot_cfg: PivotConfig, scoring_cfg: ScoringConfig
) -> Swing | None:
    """Välj den swing-leg analytikern sannolikt hade ritat Fib på."""
    ranked = rank_swings(df, pivot_cfg, scoring_cfg)
    if not ranked:
        return None
    swing = ranked[0]
    swing.status = classify_swing(df, swing, pivot_cfg.fractal_n, scoring_cfg.confirm_min_retrace)
    return swing


def swing_score_margin(
    df: pd.DataFrame, pivot_cfg: PivotConfig, scoring_cfg: ScoringConfig
) -> float | None:
    """Top-1 minus top-2 swing score — an *ambiguity* signal for labeling prioritisation.

    A small margin means the machine is torn between its two best swing candidates → a hard,
    high-value case for a human to label first (active-learning uncertainty sampling). Returns
    ``None`` when fewer than two candidate swings exist (nothing to disambiguate). This is a
    read-only scorer: it ranks candidates but writes nothing and promotes nothing to facit.
    """
    ranked = rank_swings(df, pivot_cfg, scoring_cfg)
    if len(ranked) < 2:
        return None
    return float(ranked[0].score - ranked[1].score)

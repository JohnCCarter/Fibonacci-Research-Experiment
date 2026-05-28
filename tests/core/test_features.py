"""Verifierar faktiska feature-värden, inte bara att nycklarna finns."""

import numpy as np

from fibengine.core.config import ScoringConfig
from fibengine.core.features import (
    _cleanliness,
    _round_number_proximity,
    compute_features,
    enumerate_swings,
)
from fibengine.core.models import Pivot, Swing
from fibengine.data.loader import atr


def _up_swing(df, start_i=40, end_i=60) -> Swing:
    return Swing(
        start=Pivot(start_i, df.index[start_i], float(df["low"].iloc[start_i]), "low", 2.0),
        end=Pivot(end_i, df.index[end_i], float(df["high"].iloc[end_i]), "high", 2.0),
    )


def test_cleanliness_is_one_for_straight_leg(synthetic_df):
    # 40->60 i synthetic_df är en monoton uppgång (105 -> 130): rak väg.
    swing = _up_swing(synthetic_df)
    assert _cleanliness(synthetic_df, swing) == 1.0


def test_round_number_proximity_peaks_on_round_values():
    assert _round_number_proximity(100.0) > _round_number_proximity(104.5)
    assert 0.0 <= _round_number_proximity(104.5) <= 1.0


def test_recency_is_one_when_leg_ends_on_last_bar(synthetic_df):
    swing = _up_swing(synthetic_df, 40, len(synthetic_df) - 1)
    feats = compute_features(synthetic_df, swing, atr(synthetic_df, 14), ScoringConfig())
    assert feats["recency"] == 1.0


def test_structure_and_confluence_default_neutral_without_pivots(synthetic_df):
    swing = _up_swing(synthetic_df)
    feats = compute_features(synthetic_df, swing, atr(synthetic_df, 14), ScoringConfig())
    assert feats["structure_alignment"] == 0.5
    assert feats["scale_confluence"] == 0.5


def test_magnitude_in_unit_range_and_monotonic(synthetic_df):
    atr_series = atr(synthetic_df, 14)
    small = _up_swing(synthetic_df, 55, 60)
    big = _up_swing(synthetic_df, 40, 60)
    f_small = compute_features(synthetic_df, small, atr_series, ScoringConfig())
    f_big = compute_features(synthetic_df, big, atr_series, ScoringConfig())
    assert 0.0 <= f_small["magnitude"] <= 1.0
    assert f_big["magnitude"] > f_small["magnitude"]


def test_enumerate_swings_only_pairs_opposite_kinds_and_caps(synthetic_df):
    pivots = [
        Pivot(0, synthetic_df.index[0], 100.0, "low", 2.0),
        Pivot(20, synthetic_df.index[20], 120.0, "high", 2.0),
        Pivot(40, synthetic_df.index[40], 105.0, "low", 2.0),
        Pivot(60, synthetic_df.index[60], 130.0, "high", 2.0),
    ]
    legs = enumerate_swings(pivots, max_legs=50)
    assert all(leg.start.kind != leg.end.kind for leg in legs)
    # Sorterade på senaste end först.
    assert legs[0].end.index >= legs[-1].end.index
    # Cap respekteras.
    assert len(enumerate_swings(pivots, max_legs=2)) == 2


def test_features_are_finite_with_nan_atr_warmup(synthetic_df):
    # ATR har NaN i uppvärmningen; magnitude ska ändå bli ändligt via fallback.
    atr_series = atr(synthetic_df, 14)
    swing = _up_swing(synthetic_df, 0, 5)
    feats = compute_features(synthetic_df, swing, atr_series, ScoringConfig())
    assert all(np.isfinite(v) for v in feats.values())

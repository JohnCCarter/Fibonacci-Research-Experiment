import pytest

from fibengine.core.config import PivotConfig, ScoringConfig
from fibengine.core.scoring import rank_swings, select_swing, swing_score_margin


def _scoring_cfg() -> ScoringConfig:
    return ScoringConfig(
        weights={
            "magnitude": 1.0,
            "recency": 0.8,
            "prominence": 0.6,
            "cleanliness": 0.5,
            "round_number": 0.2,
            "duration": -0.3,
            "structure_alignment": 0.9,
        },
        duration_target=20,
        max_candidate_legs=50,
    )


def test_rank_swings_assigns_features_and_scores(synthetic_df):
    legs = rank_swings(synthetic_df, PivotConfig(min_prominence_atr=0.3), _scoring_cfg())
    assert legs
    assert legs[0].score >= legs[-1].score
    assert set(legs[0].features) == {
        "magnitude",
        "recency",
        "prominence",
        "cleanliness",
        "round_number",
        "duration",
        "structure_alignment",
        "scale_confluence",
    }


def test_select_swing_prefers_recent_large_clean_leg(synthetic_df):
    swing = select_swing(synthetic_df, PivotConfig(min_prominence_atr=0.3), _scoring_cfg())
    assert swing is not None
    # Den sista, största legen (105 -> 130) bör väljas.
    assert swing.direction == "up"
    assert swing.end.price > 128
    assert swing.status in {"confirmed", "provisional"}


def test_swing_score_margin_is_top1_minus_top2(synthetic_df):
    pivot, cfg = PivotConfig(min_prominence_atr=0.3), _scoring_cfg()
    legs = rank_swings(synthetic_df, pivot, cfg)
    assert len(legs) >= 2  # the synthetic fixture yields multiple candidate legs
    margin = swing_score_margin(synthetic_df, pivot, cfg)
    assert margin == pytest.approx(legs[0].score - legs[1].score)
    assert margin >= 0  # ranked descending, so the gap is non-negative

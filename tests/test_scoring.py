from fibengine.config import PivotConfig, ScoringConfig
from fibengine.scoring import rank_swings, select_swing


def _scoring_cfg() -> ScoringConfig:
    return ScoringConfig(
        weights={
            "magnitude": 1.0,
            "recency": 0.8,
            "prominence": 0.6,
            "cleanliness": 0.5,
            "round_number": 0.2,
            "duration": -0.3,
        },
        duration_target=20,
        max_candidate_legs=50,
    )


def test_rank_swings_assigns_features_and_scores(synthetic_df):
    legs = rank_swings(synthetic_df, PivotConfig(min_prominence_atr=0.3), _scoring_cfg())
    assert legs
    assert legs[0].score >= legs[-1].score
    assert set(legs[0].features) == {
        "magnitude", "recency", "prominence", "cleanliness", "round_number", "duration",
    }


def test_select_swing_prefers_recent_large_clean_leg(synthetic_df):
    swing = select_swing(synthetic_df, PivotConfig(min_prominence_atr=0.3), _scoring_cfg())
    assert swing is not None
    # Den sista, största legen (105 -> 130) bör väljas.
    assert swing.direction == "up"
    assert swing.end.price > 128

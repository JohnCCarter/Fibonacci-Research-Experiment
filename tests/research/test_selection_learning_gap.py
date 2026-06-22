"""Tests for the retrospective-W / causal-availability-gap study (W-gap lock 2026-06-22).

Deterministic: the locked verdict thresholds (L5), viewport-relative recency (L9), the retrospective
feature whitelist, and a synthetic same-row reconstruction with exclusions — no real corpus /
network. Shared machinery lives in ``selection_learning`` (sl); the gap additions in
``selection_learning_gap`` (slg)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from fibengine.core.config import PivotConfig, ScoringConfig
from fibengine.research import selection_learning as sl
from fibengine.research import selection_learning_gap as slg


def _synthetic_df(n: int = 120) -> pd.DataFrame:
    # deterministic zig-zag so detect_pivots finds alternating pivots
    idx = pd.date_range("2020-01-01", periods=n, freq="D", tz="UTC")
    t = np.arange(n)
    base = 100 + 10 * np.sin(t / 4.0)
    high = base + 1.0
    low = base - 1.0
    close = base + 0.2 * np.cos(t / 4.0)
    return pd.DataFrame({"open": base, "high": high, "low": low, "close": close}, index=idx)


def test_retro_feature_names_is_all_eight_minus_interaction():
    names = slg.retro_feature_names()
    # all non-interaction features admitted in the retrospective model (incl recency + confluence)
    assert names == [
        "cleanliness",
        "duration",
        "magnitude",
        "prominence",
        "recency",
        "scale_confluence",
        "structure_alignment",
    ]
    assert "round_number" not in names  # interaction-only, never a primary input


def test_viewport_relative_recency_is_leg_over_W_plus_leg():
    # L9: viewport_start = anchor_a → leg / (W + leg)
    assert slg.viewport_relative_recency(10, 20, 180) == pytest.approx(10 / 190)
    assert slg.viewport_relative_recency(100, 100, 180) == 0.0  # zero-length leg
    # bounded, never dataset-relative: independent of absolute position, only leg + W
    assert slg.viewport_relative_recency(500, 510, 180) == pytest.approx(10 / 190)


def _gapcell(k: int, powered: bool, ci_low: float | None, ci_high: float | None = None) -> dict:
    inf = None if ci_low is None else {"ci95_low": ci_low, "ci95_high": ci_high}
    return {"k": k, "powered": powered, "gap_inference": inf}


def test_gap_verdict_persists_closes_and_none():
    # gap(3)>0 and gap(12)>0 → persists
    assert (
        slg.gap_verdict([_gapcell(3, True, 0.02, 0.10), _gapcell(12, True, 0.03, 0.12)])
        == "gap_persists"
    )
    # gap(3)>0 but gap(12) CI includes 0 → closes with buffer
    assert (
        slg.gap_verdict([_gapcell(3, True, 0.02, 0.10), _gapcell(12, True, -0.01, 0.05)])
        == "gap_closes_with_buffer"
    )
    # gap(3) CI includes 0 → no causal gap
    assert (
        slg.gap_verdict([_gapcell(3, True, -0.01, 0.05), _gapcell(12, True, 0.03, 0.12)])
        == "no_causal_gap"
    )


def test_gap_verdict_artifact_and_inconclusive():
    # robustly negative gap (CI upper < 0) → artifact check, not a finding
    assert slg.gap_verdict([_gapcell(3, True, -0.10, -0.02)]) == "artifact_check_needed"
    # k=3 unpowered / missing inference → inconclusive
    assert slg.gap_verdict([_gapcell(3, False, None)]) == "inconclusive"
    # k=3 positive but k=12 unpowered → cannot resolve → inconclusive
    assert (
        slg.gap_verdict([_gapcell(3, True, 0.02, 0.10), _gapcell(12, False, None)])
        == "inconclusive"
    )


def test_build_retro_features_same_rows_and_exclusions():
    df = _synthetic_df(120)
    pivot_cfg = PivotConfig(mode="fractal", fractal_n=1, lookback=3, min_prominence_atr=0.0)
    scoring_cfg = ScoringConfig()
    cfg = sl.SelectionConfig(k=3, max_legs_per_point=5)
    live = sl.build_candidates(df, [], pivot_cfg, scoring_cfg, cfg)
    assert live, "synthetic zig-zag should yield live candidates"
    w_bars = 6
    retro, excl = slg.build_retro_features(df, live, pivot_cfg, scoring_cfg, cfg, w_bars)

    live_keys = {(c.anchor_b_pos, c.start_pos) for c in live}
    # same-row parity: every retro row is a live row (subset, never invented)
    assert set(retro).issubset(live_keys)
    # every retro feature vector carries the full retrospective feature set
    for feats in retro.values():
        assert all(f in feats for f in slg.retro_feature_names())
    # recency overridden to the viewport-relative form (not the engine default)
    (j, s), feats0 = next(iter(retro.items()))
    assert feats0["recency"] == pytest.approx(slg.viewport_relative_recency(s, j, w_bars))
    assert set(excl) == {
        "rows_excluded_endpoint_W_beyond_data",
        "rows_excluded_pivot_not_reconstructible",
        "positives_excluded",
    }
    # paired set never exceeds the live universe (exclusion only shrinks, no imputation)
    assert len(retro) <= len(live)
    # boundary path (deterministic): W = full frame → every endpoint's anchor_b+W runs off-end →
    # all rows excluded, none invented (no peeking)
    retro_big, excl_big = slg.build_retro_features(df, live, pivot_cfg, scoring_cfg, cfg, len(df))
    assert not retro_big
    assert excl_big["rows_excluded_endpoint_W_beyond_data"] == len(live)

"""Tests for the Fib selection-learning headline harness (Stage 2, live k=3).

Deterministic: exercises the numpy model/metric helpers, the provenance whitelist, the purge
window, ε-matching, and a synthetic end-to-end candidate build — no real corpus / network."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from fibengine.core.config import PivotConfig, ScoringConfig
from fibengine.core.models import Pivot
from fibengine.research import selection_learning as sl

# --- provenance whitelist (addendum A2) -------------------------------------------------------


def test_live_features_k0_only_left_available():
    # k=0 → only k*=0 features, minus interaction-only round_number
    assert sl.live_feature_names(0) == ["cleanliness", "duration", "magnitude"]


def test_live_features_k3_admits_prominence_and_structure():
    feats = sl.live_feature_names(3)
    assert "prominence" in feats and "structure_alignment" in feats
    # k*>3 stays out at the primary cell; interaction-only excluded
    assert "scale_confluence" not in feats and "recency" not in feats
    assert "round_number" not in feats


def test_live_features_k12_admits_confluence_not_recency():
    feats = sl.live_feature_names(12)
    assert "scale_confluence" in feats  # k*=12 admitted
    assert "recency" not in feats  # k*=inf never admitted


# --- purge / embargo window (parameterized by reach) ------------------------------------------


def test_window_train_must_finish_before_split():
    # reach pushes a near-split train leg into embargo
    assert sl.window_of(anchor_b_pos=80, split_idx=100, n=200, reach=3) == "train"
    assert sl.window_of(anchor_b_pos=98, split_idx=100, n=200, reach=3) is None  # embargo


def test_window_test_needs_forward_reach_inside_data():
    assert sl.window_of(anchor_b_pos=150, split_idx=100, n=200, reach=3) == "test"
    assert sl.window_of(anchor_b_pos=199, split_idx=100, n=200, reach=3) is None  # reach off-end


def test_window_large_reach_starves_boundary():
    # the W-model's large reach (e.g. 120) embargoes a wide band — designed in, not discovered
    assert sl.window_of(anchor_b_pos=50, split_idx=100, n=300, reach=120) is None


# --- average precision (pooled, A5.1) ---------------------------------------------------------


def test_ap_perfect_ranking_is_one():
    y = np.array([0, 0, 1, 1])
    scores = np.array([0.1, 0.2, 0.9, 0.8])  # both positives ranked top
    assert sl.average_precision(y, scores) == pytest.approx(1.0)


def test_ap_none_without_positives():
    assert sl.average_precision(np.array([0, 0, 0]), np.array([0.5, 0.1, 0.9])) is None


def test_ap_worst_ranking_below_perfect():
    y = np.array([1, 0, 0, 0])
    worst = sl.average_precision(y, np.array([0.1, 0.9, 0.8, 0.7]))  # positive ranked last
    assert worst is not None and worst == pytest.approx(0.25)


# --- ROC-AUC (secondary) ----------------------------------------------------------------------


def test_auc_perfect_and_degenerate():
    assert sl.roc_auc(np.array([0, 1]), np.array([0.1, 0.9])) == pytest.approx(1.0)
    assert sl.roc_auc(np.array([1, 1]), np.array([0.1, 0.9])) is None  # no negatives


# --- AP-lift inference: decision-point cluster bootstrap --------------------------------------


def test_bootstrap_detects_real_lift():
    # model ranks positives top, baseline ranks them bottom → lift > 0 reliably
    n_groups = 40
    y, sm, sb, groups = [], [], [], []
    for g in range(n_groups):
        # one positive + three negatives per decision-point group
        y += [1, 0, 0, 0]
        sm += [0.9, 0.2, 0.1, 0.15]  # model: positive on top
        sb += [0.1, 0.9, 0.8, 0.7]  # baseline: positive at bottom
        groups += [g, g, g, g]
    out = sl.decision_point_bootstrap(
        np.array(y, float), np.array(sm), np.array(sb), np.array(groups), n_boot=300, seed=1
    )
    assert out is not None
    assert out["method"] == "decision_point_cluster_bootstrap"
    assert out["n_groups"] == n_groups
    assert out["lift_mean"] > 0
    assert out["ci95_low"] > 0  # CI excludes 0 → lift is real
    assert out["p_one_sided_lift_le_0"] < 0.05


def test_bootstrap_no_lift_when_rankers_equal():
    # identical model/baseline scores → lift ≈ 0, p should not be significant
    rng = np.random.default_rng(2)
    n = 80
    groups = np.repeat(np.arange(20), 4)
    y = (rng.random(n) < 0.25).astype(float)
    s = rng.random(n)
    out = sl.decision_point_bootstrap(y, s, s.copy(), groups, n_boot=300, seed=3)
    if out is not None:  # None only if a degenerate resample wiped positives
        assert out["lift_mean"] == pytest.approx(0.0, abs=1e-9)
        assert out["p_one_sided_lift_le_0"] >= 0.5  # cannot reject null


def test_bootstrap_none_without_positives():
    groups = np.array([0, 0, 1, 1])
    assert (
        sl.decision_point_bootstrap(
            np.zeros(4),
            np.array([0.1, 0.2, 0.3, 0.4]),
            np.array([0.4, 0.3, 0.2, 0.1]),
            groups,
            n_boot=50,
            seed=0,
        )
        is None
    )


# --- logistic regression (deterministic, interpretable) ---------------------------------------


def test_logreg_separates_and_is_deterministic():
    rng = np.random.default_rng(0)
    x = np.vstack([rng.normal(-2, 0.5, (40, 1)), rng.normal(2, 0.5, (40, 1))])
    y = np.array([0] * 40 + [1] * 40, dtype=float)
    cfg = sl.SelectionConfig()
    m1 = sl.fit_logreg(x, y, cfg)
    m2 = sl.fit_logreg(x, y, cfg)
    assert np.allclose(m1["w"], m2["w"])  # deterministic
    p = sl.predict_proba(m1, x)
    assert sl.roc_auc(y, p) > 0.95  # learns the obvious separation


# --- ε-matching (A4) --------------------------------------------------------------------------


def _ts_index(n: int) -> tuple[pd.DatetimeIndex, np.ndarray]:
    idx = pd.date_range("2020-01-01", periods=n, freq="D", tz="UTC")
    return idx, idx.values.astype("datetime64[ns]").astype("int64")


def test_matches_human_within_eps_both_anchors():
    idx, index_ns = _ts_index(50)
    leg = sl.HumanLeg(
        anchor_a_ts=idx[10],
        anchor_a_price=100.0,
        anchor_b_ts=idx[20],
        anchor_b_price=120.0,
        direction="up",
    )
    cfg = sl.SelectionConfig()
    start = Pivot(index=10, timestamp=idx[10], price=100.4, kind="low", prominence=1.0)
    end = Pivot(index=20, timestamp=idx[20], price=119.7, kind="high", prominence=1.0)
    # atr=2.0 → price_tol = 0.5*2 = 1.0; both anchors within tol and time exact
    assert sl._matches_human(start, end, [leg], index_ns, atr_at_b=2.0, cfg=cfg) == 0


def test_matches_human_rejects_wrong_direction_and_far_price():
    idx, index_ns = _ts_index(50)
    leg = sl.HumanLeg(idx[10], 100.0, idx[20], 120.0, "up")
    cfg = sl.SelectionConfig()
    start = Pivot(10, idx[10], 100.0, "low", 1.0)
    far = Pivot(20, idx[20], 130.0, "high", 1.0)  # 10 away, tol=1.0 → reject
    assert sl._matches_human(start, far, [leg], index_ns, 2.0, cfg) == -1


# --- synthetic end-to-end build_candidates (causal, truncated) --------------------------------


def _synthetic_df(n: int = 120) -> pd.DataFrame:
    # deterministic zig-zag so detect_pivots finds alternating pivots
    idx = pd.date_range("2020-01-01", periods=n, freq="D", tz="UTC")
    t = np.arange(n)
    base = 100 + 10 * np.sin(t / 4.0)
    high = base + 1.0
    low = base - 1.0
    close = base + 0.2 * np.cos(t / 4.0)
    return pd.DataFrame({"open": base, "high": high, "low": low, "close": close}, index=idx)


def test_build_candidates_is_causal_and_labels():
    df = _synthetic_df()
    pivot_cfg = PivotConfig(mode="fractal", fractal_n=1, lookback=3, min_prominence_atr=0.0)
    scoring_cfg = ScoringConfig()
    cfg = sl.SelectionConfig(k=3, max_legs_per_point=5)
    cands = sl.build_candidates(df, [], pivot_cfg, scoring_cfg, cfg)
    assert cands, "zig-zag should yield candidate legs"
    # causal: every candidate is confirmed within the data (anchor_b + k < n)
    assert all(c.anchor_b_pos + cfg.k < len(df) for c in cands)
    # no human legs → all negative; live feature columns present
    assert all(c.label == 0 for c in cands)
    feats = sl.live_feature_names(cfg.k)
    assert all(f in cands[0].features for f in feats)


def test_load_human_legs_rejects_bad_timeframe():
    with pytest.raises(ValueError, match="not allowed"):
        sl.load_human_legs("1h")

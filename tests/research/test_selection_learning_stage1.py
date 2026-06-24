"""Tests for the Stage-1 per-pivot diagnostic (Stage-1 LOCK 2026-06-24).

Deterministic: the per-pivot feature subset + k*-gating (S3/S4), a/b-pooled label (S1), the
coverage-vs-ranking separation (S6), the locked verdict thresholds (S7), and per-cell checkpoint
resume — no real corpus / network. Shared machinery lives in ``selection_learning`` (sl); the
Stage-1 pieces in ``selection_learning_stage1`` (s1)."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from fibengine.core.config import PivotConfig, ScoringConfig
from fibengine.core.models import Pivot
from fibengine.research import selection_learning as sl
from fibengine.research import selection_learning_stage1 as s1


def _synthetic_df(n: int = 120) -> pd.DataFrame:
    idx = pd.date_range("2020-01-01", periods=n, freq="D", tz="UTC")
    t = np.arange(n)
    base = 100 + 10 * np.sin(t / 4.0)
    return pd.DataFrame(
        {
            "open": base,
            "high": base + 1.0,
            "low": base - 1.0,
            "close": base + 0.2 * np.cos(t / 4.0),
        },
        index=idx,
    )


# --- feature subset + k*-gating (LOCK S3/S4) ---------------------------------------------------


def test_stage1_feature_names_k_gating_and_k0_degenerate():
    assert s1.stage1_feature_names(0) == []  # k=0 degenerate: no usable per-pivot feature
    assert s1.stage1_feature_names(3) == ["prominence", "structure_alignment"]
    assert s1.stage1_feature_names(6) == [
        "prominence",
        "structure_alignment",
    ]  # no new feature 3<k*<=6
    assert s1.stage1_feature_names(12) == ["prominence", "scale_confluence", "structure_alignment"]
    # round_number is interaction-only (never a primary input); recency is dropped (k*=inf)
    assert "round_number" not in s1.stage1_feature_names(12)
    assert "recency" not in s1.stage1_feature_names(12)
    # leg/set-level features are structurally absent from the per-pivot subset
    for leg_only in ("magnitude", "cleanliness", "duration", "exclusivity"):
        assert leg_only not in s1.stage1_feature_names(12)


def test_compute_pivot_features_faithful_and_no_leakage():
    highs = [Pivot(10, pd.Timestamp("2020-01-11", tz="UTC"), 110.0, "high", 2.0)]
    feats = s1.compute_pivot_features(highs[0], highs, None, ScoringConfig())
    # prominence = tanh(prom/2) (single-endpoint reduction of the leg formula)
    assert feats["prominence"] == pytest.approx(float(np.tanh(2.0 / 2.0)))
    # confluence neutral 0.5 when no larger degrees supplied
    assert feats["scale_confluence"] == 0.5
    # distance-to-anchor and recency are NEVER features (label-leakage / omniscience guards)
    assert set(feats) == {"prominence", "structure_alignment", "scale_confluence", "round_number"}
    assert "recency" not in feats


def test_pivot_confluence_is_per_pivot_kind_match():
    piv = Pivot(20, pd.Timestamp("2020-01-21", tz="UTC"), 100.0, "high", 1.0)
    # a higher-degree high within tol confirms; a low does not
    multi = {12: [Pivot(21, pd.Timestamp("2020-01-22", tz="UTC"), 100.0, "high", 1.0)]}
    assert s1._pivot_confluence(piv, multi, tol_bars=3) == 1.0
    multi_low = {12: [Pivot(21, pd.Timestamp("2020-01-22", tz="UTC"), 100.0, "low", 1.0)]}
    assert s1._pivot_confluence(piv, multi_low, tol_bars=3) == 0.0
    assert s1._pivot_confluence(piv, None, tol_bars=3) == 0.5


# --- label: a/b pooled, ε, causal (LOCK S1) ----------------------------------------------------


def test_human_anchor_points_pools_ab_and_dedupes():
    idx = pd.date_range("2020-01-01", periods=50, freq="D", tz="UTC")
    index_ns = idx.values.astype("datetime64[ns]").astype("int64")
    # leg1 b == leg2 a (a shared swing extreme) → one anchor, not two
    leg1 = sl.HumanLeg(idx[0], 100.0, idx[10], 110.0, "up")
    leg2 = sl.HumanLeg(idx[10], 110.0, idx[20], 90.0, "down")
    pts = s1._human_anchor_points([leg1, leg2], index_ns)
    # leg1.a, leg1.b(==leg2.a), leg2.b → 3 unique points (the shared 110@idx10 deduped)
    assert len(pts) == 3
    assert (10, 110.0) in pts


def test_matched_anchors_eps_and_causal_atr_guard():
    piv = Pivot(10, pd.Timestamp("2020-01-11", tz="UTC"), 100.0, "high", 1.0)
    anchors = [(11, 100.4), (30, 100.0)]  # first: 1 bar + 0.4 price away; second: far in time
    cfg = sl.SelectionConfig(eps_time_bars=3, eps_price_atr=0.5)
    assert s1._matched_anchors(piv, anchors, atr_at=1.0, cfg=cfg) == [0]  # 0.4 <= 0.5*1.0
    assert s1._matched_anchors(piv, anchors, atr_at=0.5, cfg=cfg) == []  # 0.4 > 0.5*0.5=0.25
    # non-finite / non-positive ATR → no match (fail-closed)
    assert s1._matched_anchors(piv, anchors, atr_at=float("nan"), cfg=cfg) == []
    assert s1._matched_anchors(piv, anchors, atr_at=0.0, cfg=cfg) == []


def test_build_pivot_candidates_causal_coverage_and_chunks():
    df = _synthetic_df(120)
    pivot_cfg = PivotConfig(mode="fractal", fractal_n=1, lookback=3, min_prominence_atr=0.0)
    cfg = sl.SelectionConfig(k=3)
    cands, covered, n_anchors = s1.build_pivot_candidates(df, [], pivot_cfg, ScoringConfig(), cfg)
    assert cands, "synthetic zig-zag should yield per-pivot candidates"
    assert n_anchors == 0 and covered == set()  # no human legs → no labels, empty coverage
    for c in cands:
        assert all(c.features[f] is not None for f in s1.stage1_feature_names(3))
        assert c.label == 0
        assert c.chunk == c.chunk and c.chunk >= 0  # chunk id assigned for the cluster bootstrap
    # no peeking: every candidate's live cutoff (pivot+max(k,fractal_n)) is inside the data
    assert all(c.pivot_pos + max(cfg.k, 1) < len(df) for c in cands)


def test_build_pivot_candidates_labels_and_covers_a_human_anchor():
    df = _synthetic_df(120)
    pivot_cfg = PivotConfig(mode="fractal", fractal_n=1, lookback=3, min_prominence_atr=0.0)
    cfg = sl.SelectionConfig(k=3)
    bare, _, _ = s1.build_pivot_candidates(df, [], pivot_cfg, ScoringConfig(), cfg)
    target = bare[len(bare) // 2]  # an actual detected pivot in the train region
    ts = df.index[target.pivot_pos]
    price = (
        df["high"].iloc[target.pivot_pos]
        if target.kind == "high"
        else df["low"].iloc[target.pivot_pos]
    )
    leg = sl.HumanLeg(ts, float(price), df.index[target.pivot_pos + 5], float(price) + 50, "up")
    cands, covered, n_anchors = s1.build_pivot_candidates(
        df, [leg], pivot_cfg, ScoringConfig(), cfg
    )
    assert n_anchors == 2  # a and b
    assert any(c.label == 1 for c in cands)  # the targeted pivot is human-anchored
    assert len(covered) >= 1  # at least the anchored pivot is covered (detection half)


# --- per-cell driver + verdict (LOCK S6/S7) ----------------------------------------------------


def test_run_stage1_cell_k0_is_degenerate_stub():
    cell = s1.run_stage1_cell("4h", 0, sl.SelectionConfig(), settings=object())
    assert cell["degenerate"] is True
    assert cell["features"] == [] and cell["powered"] is False
    assert "k=0" in cell["reason"]


def _cell(powered, recall, ci_low=None, ci_high=None, degenerate=False):
    inf = None if ci_low is None else {"ci95_low": ci_low, "ci95_high": ci_high}
    return {
        "k": 3,
        "degenerate": degenerate,
        "powered": powered,
        "detection_recall": recall,
        "ranking_lift_inference": inf,
    }


def test_stage1_verdict_all_branches():
    # underpowered first (even if a recall/inference is present)
    assert s1.stage1_verdict(_cell(False, 0.9, 0.02, 0.1)) == "inconclusive_underpowered"
    assert s1.stage1_verdict(_cell(True, 0.9, None)) == "inconclusive_underpowered"
    # coverage floor overrides the ranking label
    assert s1.stage1_verdict(_cell(True, 0.3, 0.02, 0.1)) == "detector_coverage_limited"
    # ranking lift CI excludes 0 above → learnable
    assert s1.stage1_verdict(_cell(True, 0.8, 0.02, 0.10)) == "pivot_selection_learnable"
    # ranking lift CI includes 0 → expected/publishable null
    assert s1.stage1_verdict(_cell(True, 0.8, -0.01, 0.05)) == "no_pivot_signal_above_prominence"
    # direction guard: prominence significantly beats the model (CI upper < 0)
    assert s1.stage1_verdict(_cell(True, 0.8, -0.10, -0.02)) == "artifact_check_needed"


# --- checkpoint / resume + study aggregation ---------------------------------------------------


def test_run_or_load_cell_writes_then_resumes(tmp_path, monkeypatch):
    calls = {"n": 0}

    def _fake_cell(tf, k, cfg, settings):  # noqa: ARG001 — stub, counts invocations
        calls["n"] += 1
        return {"timeframe": tf, "k": k, "powered": True, "detection_recall": 0.8}

    monkeypatch.setattr(s1, "run_stage1_cell", _fake_cell)
    cfg = sl.SelectionConfig()
    r1 = s1._run_or_load_cell("4h", 3, cfg, object(), tmp_path)
    r2 = s1._run_or_load_cell("4h", 3, cfg, object(), tmp_path)
    assert r1 == r2 and calls["n"] == 1  # second call loaded the checkpoint, no recompute
    assert (tmp_path / "4h_k3.json").exists()
    assert not (tmp_path / "4h_k3.json.tmp").exists()


def test_run_or_load_cell_recomputes_on_seed_mismatch(tmp_path, monkeypatch):
    calls = {"n": 0}

    def _fake_cell(tf, k, cfg, settings):  # noqa: ARG001 — stub
        calls["n"] += 1
        return {"timeframe": tf, "k": k}

    monkeypatch.setattr(s1, "run_stage1_cell", _fake_cell)
    (tmp_path / "4h_k3.json").write_text(
        json.dumps({"seed": 999, "cell": {"stale": True}}), encoding="utf-8"
    )
    out = s1._run_or_load_cell("4h", 3, sl.SelectionConfig(), object(), tmp_path)
    assert calls["n"] == 1 and out == {"timeframe": "4h", "k": 3}


def test_run_stage1_study_checkpoints_and_aggregates(tmp_path, monkeypatch):
    def _fake_cell(tf, k, cfg, settings):  # noqa: ARG001 — stub: k=3 4h is the powered primary
        powered = tf == "4h" and k == 3
        return {
            "timeframe": tf,
            "k": k,
            "degenerate": k == 0,
            "powered": powered,
            "detection_recall": 0.8 if powered else 0.2,
            "ranking_lift_inference": {"ci95_low": 0.02, "ci95_high": 0.1} if powered else None,
        }

    monkeypatch.setattr(s1, "run_stage1_cell", _fake_cell)
    monkeypatch.setattr(s1, "load_settings", lambda *a, **k: object())
    rep = s1.run_stage1_study(None, sl.SelectionConfig(), ckpt_dir=tmp_path)
    assert [r["k"] for r in rep["results_4h"]] == [0, 3, 6, 12]
    assert len(rep["results_context_underpowered"]) == 3
    assert rep["stage1_verdict"] == "pivot_selection_learnable"  # from the 4h k=3 primary cell
    for name in ("4h_k0", "4h_k3", "4h_k6", "4h_k12", "1M_k3", "1w_k3", "1d_k3"):
        assert (tmp_path / f"{name}.json").exists()

"""Tests for the model-enrichment shot (enrichment LOCK 2026-06-24).

Deterministic, no real corpus / network: the causal ``exclusivity`` definition (E1), no-look-ahead
beyond ``anchor_b + k``, the nested enriched feature set (E2), the distinctness check (E1), the
blind verdict thresholds (E4), and per-cell checkpoint resume. Shared machinery lives in
``selection_learning`` (sl); the enrichment pieces in ``selection_learning_enrich`` (en)."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from fibengine.core.config import PivotConfig, ScoringConfig
from fibengine.core.models import Pivot
from fibengine.research import selection_learning as sl
from fibengine.research import selection_learning_enrich as en


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


def _piv(index: int, price: float, kind: str) -> Pivot:
    ts = pd.Timestamp("2020-01-01", tz="UTC") + pd.Timedelta(days=index)
    return Pivot(index, ts, price, kind, 1.0)


# --- nested enriched feature set (LOCK E2) -----------------------------------------------------


def test_enrich_feature_names_is_stage2_plus_exclusivity():
    assert en.enrich_feature_names(3) == [
        "cleanliness",
        "duration",
        "magnitude",
        "prominence",
        "structure_alignment",
        "exclusivity",
    ]
    # baseline is exactly the current Stage-2 live set (LOCK E2) with exclusivity appended last
    assert en.enrich_feature_names(3)[:-1] == sl.live_feature_names(3)
    assert en.enrich_feature_names(3)[-1] == en.ENRICH_FEATURE


# --- the causal exclusivity feature (LOCK E1) --------------------------------------------------


def test_exclusivity_uninterrupted_impulse_is_one():
    # up-leg low@100 -> high@200, no interior counter-move -> dominant/complete -> 1.0
    assert en.exclusivity_value([], 100.0, 200.0, "up") == 1.0
    # an interior LOW with no preceding interior HIGH is not a counter-retracement (E1 wording)
    interior = [_piv(2, 120.0, "low"), _piv(4, 150.0, "high")]
    assert en.exclusivity_value(interior, 100.0, 200.0, "up") == 1.0


def test_exclusivity_partial_and_full_retracement_up():
    net = 100.0  # low@100 -> high@200
    # interior peak 150 then trough 120 -> R = 30 -> 1 - 30/100 = 0.70
    interior = [_piv(2, 150.0, "high"), _piv(4, 120.0, "low")]
    assert en.exclusivity_value(interior, 100.0, 200.0, "up") == pytest.approx(0.70)
    # deepest of several counter-moves wins (running interior high before the low): 180-110=70
    interior2 = [
        _piv(2, 150.0, "high"),
        _piv(3, 130.0, "low"),
        _piv(5, 180.0, "high"),
        _piv(6, 110.0, "low"),
    ]
    assert en.exclusivity_value(interior2, 100.0, 200.0, "up") == pytest.approx(1.0 - 70.0 / net)
    # R >= net -> clipped to 0 (deeply interrupted)
    interior3 = [_piv(2, 200.0, "high"), _piv(4, 90.0, "low")]
    assert en.exclusivity_value(interior3, 100.0, 200.0, "up") == 0.0


def test_exclusivity_down_leg_symmetric():
    # down-leg high@200 -> low@100; counter-move = bounce (interior low then higher interior high)
    interior = [_piv(2, 130.0, "low"), _piv(4, 160.0, "high")]
    assert en.exclusivity_value(interior, 200.0, 100.0, "down") == pytest.approx(0.70)
    assert en.exclusivity_value([], 200.0, 100.0, "down") == 1.0


def test_exclusivity_degenerate_net_guarded():
    assert en.exclusivity_value([_piv(2, 100.0, "high")], 100.0, 100.0, "up") == 0.0


# --- build_exclusivity: same-row, causal, no look-ahead (LOCK E1) -------------------------------


def test_build_exclusivity_covers_every_candidate_in_unit_range():
    df = _synthetic_df(120)
    pivot_cfg = PivotConfig(mode="fractal", fractal_n=1, lookback=3, min_prominence_atr=0.0)
    cfg = sl.SelectionConfig(k=3)
    cands = sl.build_candidates(df, [], pivot_cfg, ScoringConfig(), cfg)
    assert cands, "synthetic zig-zag should yield Stage-2 candidates"
    excl_map, excl = en.build_exclusivity(df, cands, pivot_cfg, cfg)
    # universe is identical to build_candidates -> every row reconstructs, no exclusions
    assert set(excl_map) == {(c.anchor_b_pos, c.start_pos) for c in cands}
    assert excl["rows_excluded_endpoint_beyond_data"] == 0
    assert excl["rows_excluded_pivot_not_reconstructible"] == 0
    assert all(0.0 <= v <= 1.0 for v in excl_map.values())


def test_build_exclusivity_ignores_data_after_anchor_b_plus_k():
    """No look-ahead: exclusivity for an endpoint depends only on bars up to ``anchor_b + k``, so
    appending arbitrary later bars must not change any already-computable row (E1 causal viewport)."""
    df = _synthetic_df(120)
    pivot_cfg = PivotConfig(mode="fractal", fractal_n=1, lookback=3, min_prominence_atr=0.0)
    cfg = sl.SelectionConfig(k=3)
    cands = sl.build_candidates(df, [], pivot_cfg, ScoringConfig(), cfg)
    base_map, _ = en.build_exclusivity(df, cands, pivot_cfg, cfg)
    # extend the frame with wild bars far beyond every existing endpoint's anchor_b + k
    extra = pd.DataFrame(
        {"open": 999.0, "high": 1500.0, "low": 1.0, "close": 999.0},
        index=pd.date_range("2021-01-01", periods=40, freq="D", tz="UTC"),
    )
    df2 = pd.concat([df, extra])
    ext_map, _ = en.build_exclusivity(df2, cands, pivot_cfg, cfg)
    for key, val in base_map.items():
        assert ext_map[key] == pytest.approx(val)


# --- distinctness check (LOCK E1) --------------------------------------------------------------


def test_train_corr_reports_value_and_handles_constant():
    a = np.array([0.1, 0.5, 0.9, 0.3])
    assert en._train_corr(a, a) == pytest.approx(1.0)
    assert en._train_corr(a, -a) == pytest.approx(-1.0)
    assert en._train_corr(np.full(4, 0.5), a) is None  # constant column -> corr undefined
    assert en._train_corr(np.zeros(0), np.zeros(0)) is None


# --- blind verdict (LOCK E4) -------------------------------------------------------------------


def _cell(powered, ci_low=None, ci_high=None, degenerate=False):
    inf = None if ci_low is None else {"ci95_low": ci_low, "ci95_high": ci_high}
    return {"degenerate": degenerate, "powered": powered, "ap_lift_inference": inf}


def test_enrich_verdict_all_branches():
    assert en.enrich_verdict(_cell(False, 0.02, 0.1)) == "inconclusive_underpowered"
    assert en.enrich_verdict(_cell(True, None)) == "inconclusive_underpowered"
    assert en.enrich_verdict(_cell(True, 0.02, 0.10)) == "enrichment_helps"
    assert en.enrich_verdict(_cell(True, -0.01, 0.05)) == "no_enrichment_signal"
    assert en.enrich_verdict(_cell(True, -0.10, -0.02)) == "enriched_worse_check"


# --- checkpoint / resume + study aggregation ---------------------------------------------------


def test_run_or_load_cell_writes_then_resumes(tmp_path, monkeypatch):
    calls = {"n": 0}

    def _fake_cell(tf, k, cfg, settings):  # noqa: ARG001 — stub, counts invocations
        calls["n"] += 1
        return {"timeframe": tf, "k": k, "powered": True}

    monkeypatch.setattr(en, "run_enrich_cell", _fake_cell)
    cfg = sl.SelectionConfig()
    r1 = en._run_or_load_cell("4h", 3, cfg, object(), tmp_path)
    r2 = en._run_or_load_cell("4h", 3, cfg, object(), tmp_path)
    assert r1 == r2 and calls["n"] == 1  # second call loaded the checkpoint, no recompute
    assert (tmp_path / "4h_k3.json").exists()
    assert not (tmp_path / "4h_k3.json.tmp").exists()


def test_run_or_load_cell_recomputes_on_seed_mismatch(tmp_path, monkeypatch):
    calls = {"n": 0}

    def _fake_cell(tf, k, cfg, settings):  # noqa: ARG001 — stub
        calls["n"] += 1
        return {"timeframe": tf, "k": k}

    monkeypatch.setattr(en, "run_enrich_cell", _fake_cell)
    (tmp_path / "4h_k3.json").write_text(
        json.dumps({"seed": 999, "cell": {"stale": True}}), encoding="utf-8"
    )
    out = en._run_or_load_cell("4h", 3, sl.SelectionConfig(), object(), tmp_path)
    assert calls["n"] == 1 and out == {"timeframe": "4h", "k": 3}


def test_run_enrich_study_checkpoints_and_reads_verdict_from_4h_k3(tmp_path, monkeypatch):
    def _fake_cell(tf, k, cfg, settings):  # noqa: ARG001 — only 4h k=3 is the powered primary
        powered = tf == "4h" and k == 3
        return {
            "timeframe": tf,
            "k": k,
            "powered": powered,
            "ap_lift_inference": {"ci95_low": -0.01, "ci95_high": 0.05} if powered else None,
        }

    monkeypatch.setattr(en, "run_enrich_cell", _fake_cell)
    monkeypatch.setattr(en, "load_settings", lambda *a, **k: object())
    rep = en.run_enrich_study(None, sl.SelectionConfig(), ckpt_dir=tmp_path)
    assert rep["results_4h_primary"]["k"] == 3
    assert len(rep["results_context_underpowered"]) == 3
    assert rep["enrichment_verdict"] == "no_enrichment_signal"  # 4h k=3 CI includes 0
    for name in ("4h_k3", "1M_k3", "1w_k3", "1d_k3"):
        assert (tmp_path / f"{name}.json").exists()


def test_enrich_preflight_delegates_to_shared_preflight(monkeypatch):
    seen = {}

    def _fake_preflight(config_path):
        seen["config"] = config_path
        return 0

    monkeypatch.setattr(en, "run_preflight", _fake_preflight)
    assert en.main(["--enrich-preflight", "--config", "cfg.yaml"]) == 0
    assert seen["config"] == "cfg.yaml"

"""Tests for the cleanliness artifact-probe (artifact LOCK 2026-06-24, b533385).

Deterministic: the source-bound cleanliness span (A1), anchor-kind derivation + ε match (A2/A3),
the quarter-block bootstrap with degenerate-resample skipping (A5), the locked verdict branches
(A7), no-imputation snap drop (A3), and checkpoint resume — no real corpus / network. Shared
machinery lives in ``selection_learning`` (sl); the probe pieces in
``selection_learning_artifact`` (art)."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from fibengine.core.config import PivotConfig
from fibengine.core.models import Pivot
from fibengine.research import selection_learning as sl
from fibengine.research import selection_learning_artifact as art


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


# --- cleanliness span (LOCK A1) ----------------------------------------------------------------


def test_cleanliness_idx_source_bound_and_order_independent():
    closes = np.array([100.0, 101.0, 102.0, 103.0])  # monotone → spikrak → 1.0
    assert art._cleanliness_idx(closes, 0, 3) == pytest.approx(1.0)
    assert art._cleanliness_idx(closes, 3, 0) == pytest.approx(1.0)  # sorts endpoints
    zig = np.array([100.0, 110.0, 100.0, 110.0])  # net 10, path 30 → 1/3
    assert art._cleanliness_idx(zig, 0, 3) == pytest.approx(10.0 / 30.0)
    assert art._cleanliness_idx(closes, 2, 2) == 1.0  # <2 bars


def test_anchor_kinds_direction_then_price_fallback():
    up = sl.HumanLeg(
        pd.Timestamp("2020-01-01", tz="UTC"),
        100.0,
        pd.Timestamp("2020-01-05", tz="UTC"),
        110.0,
        "up",
    )
    dn = sl.HumanLeg(
        pd.Timestamp("2020-01-01", tz="UTC"),
        110.0,
        pd.Timestamp("2020-01-05", tz="UTC"),
        100.0,
        "down",
    )
    assert art._anchor_kinds(up) == ("low", "high")
    assert art._anchor_kinds(dn) == ("high", "low")
    # blank direction → derive from price order (build-time resolution)
    blank_up = sl.HumanLeg(
        pd.Timestamp("2020-01-01", tz="UTC"), 100.0, pd.Timestamp("2020-01-05", tz="UTC"), 120.0, ""
    )
    blank_dn = sl.HumanLeg(
        pd.Timestamp("2020-01-01", tz="UTC"), 120.0, pd.Timestamp("2020-01-05", tz="UTC"), 100.0, ""
    )
    assert art._anchor_kinds(blank_up) == ("low", "high")
    assert art._anchor_kinds(blank_dn) == ("high", "low")


def test_nearest_match_kind_eps_and_tiebreak():
    pivots = [
        Pivot(10, pd.Timestamp("2020-01-11", tz="UTC"), 100.0, "high", 1.0),
        Pivot(11, pd.Timestamp("2020-01-12", tz="UTC"), 100.2, "high", 1.0),
        Pivot(10, pd.Timestamp("2020-01-11", tz="UTC"), 100.0, "low", 1.0),
    ]
    # nearest high to (pos=12, price=100.1) within ε: pos 11 closer in time than pos 10
    m = art._nearest_match(pivots, 12, 100.1, "high", eps_time=3, price_tol=0.5)
    assert m is not None and m.index == 11
    # kind filter: a low anchor finds the low pivot, not the highs
    assert art._nearest_match(pivots, 10, 100.0, "low", 3, 0.5).kind == "low"
    # out of ε → None
    assert art._nearest_match(pivots, 40, 100.0, "high", 3, 0.5) is None
    assert art._nearest_match(pivots, 10, 105.0, "high", 3, 0.5) is None  # price too far


# --- statistics + block bootstrap (LOCK A5) ----------------------------------------------------


def _row(q, reached, exact, snapped=None, drop=None):
    return art.ArtifactRow(
        quarter=q,
        pos_a=0,
        pos_b=1,
        exact_clean=exact,
        reached=reached,
        snapped_clean=snapped,
        drop=drop,
    )


def test_surf_and_snap_stats():
    rows = [
        _row("2020Q1", True, 0.9),
        _row("2020Q1", False, 0.5),
        _row("2020Q2", True, 0.8, snapped=0.95),
    ]
    assert art._surf_stat(rows) == pytest.approx((0.9 + 0.8) / 2 - 0.5)
    assert art._snap_stat(rows) == pytest.approx(0.95 - 0.8)  # only the one with a snap
    assert art._surf_stat([_row("q", True, 0.9)]) is None  # one group empty → skip
    assert art._snap_stat([_row("q", True, 0.9)]) is None  # no snap pair


def test_block_bootstrap_returns_effective_count_and_none_when_degenerate():
    rows = [
        _row("2020Q1", True, 0.9),
        _row("2020Q1", False, 0.4),
        _row("2020Q2", True, 0.8),
        _row("2020Q2", False, 0.5),
    ]
    inf = art._block_bootstrap(rows, art._surf_stat, n_boot=200, seed=1)
    assert inf is not None
    assert inf["point"] == pytest.approx(art._surf_stat(rows))
    assert 0 < inf["n_boot_effective"] <= 200
    assert inf["ci95_low"] <= inf["ci95_high"]
    # all-reached → surf stat always None → bootstrap returns None (not a crash)
    allr = [_row("2020Q1", True, 0.9), _row("2020Q2", True, 0.8)]
    assert art._block_bootstrap(allr, art._surf_stat, 50, 1) is None


# --- verdict branches (LOCK A7) ----------------------------------------------------------------


def _inf(lo, hi):
    return {"ci95_low": lo, "ci95_high": hi}


def test_surfacing_and_snapping_verdict_branches():
    assert art._surfacing_verdict(None) == "underpowered"
    assert art._surfacing_verdict(_inf(0.02, 0.10)) == "detector_surfacing_artifact"
    assert art._surfacing_verdict(_inf(-0.02, 0.05)) == "no_surfacing_artifact"
    assert art._surfacing_verdict(_inf(-0.10, -0.02)) == "inverse_surfacing"
    assert art._snapping_verdict(_inf(0.02, 0.10)) == "snapping_inflates_cleanliness"
    assert art._snapping_verdict(_inf(-0.02, 0.05)) == "no_snapping_inflation"
    assert art._snapping_verdict(_inf(-0.10, -0.02)) == "snapping_deflates"


def test_artifact_verdict_combined():
    assert (
        art.artifact_verdict("no_surfacing_artifact", "no_snapping_inflation", False, False)
        == "inconclusive_underpowered"
    )
    assert (
        art.artifact_verdict("detector_surfacing_artifact", "no_snapping_inflation", True, True)
        == "detector_artifact_supported"
    )
    assert (
        art.artifact_verdict("no_surfacing_artifact", "snapping_inflates_cleanliness", True, True)
        == "detector_artifact_supported"
    )
    assert (
        art.artifact_verdict("no_surfacing_artifact", "no_snapping_inflation", True, True)
        == "artifact_risk_reduced"
    )
    # powered direction guard is A7-unregistered → descriptive meta status, NOT a locked verdict and
    # NOT the inconclusive_underpowered misnomer (the cell is powered)
    assert (
        art.artifact_verdict("inverse_surfacing", "snapping_deflates", True, True)
        == art.META_POWERED_DIRECTION_GUARD
    )
    assert art.META_POWERED_DIRECTION_GUARD.startswith("meta:")
    assert (
        art.artifact_verdict("inverse_surfacing", "snapping_deflates", True, True)
        != "inconclusive_underpowered"
    )


# --- build_artifact_rows: causal reached + no-imputation drop (LOCK A2/A3) ----------------------


def test_build_artifact_rows_reached_unreached_and_quarters():
    df = _synthetic_df(120)
    pivot_cfg = PivotConfig(mode="fractal", fractal_n=1, lookback=3, min_prominence_atr=0.0)
    cfg = sl.SelectionConfig(k=3)
    pivots = art.detect_pivots(df.iloc[:60], pivot_cfg)
    a, b = pivots[1], pivots[2]  # two real detected pivots → a reached leg
    reached_leg = sl.HumanLeg(df.index[a.index], a.price, df.index[b.index], b.price, "")
    # an unreached leg: anchors on a flat synthetic region offset far in price
    far_leg = sl.HumanLeg(df.index[5], 500.0, df.index[9], 480.0, "")
    rows = art.build_artifact_rows(df, [reached_leg, far_leg], cfg, pivot_cfg)
    assert len(rows) == 2
    assert rows[0].reached is True  # anchored on real pivots
    assert rows[1].reached is False  # price-far anchors cannot ε-match
    assert all(0.0 <= r.exact_clean <= 1.0 for r in rows)
    assert all(r.quarter.startswith("2020Q") for r in rows)


def test_build_artifact_rows_degenerate_snap_dropped_not_imputed(monkeypatch):
    df = _synthetic_df(60)
    pivot_cfg = PivotConfig(mode="fractal", fractal_n=1, lookback=3, min_prominence_atr=0.0)
    cfg = sl.SelectionConfig(k=3)
    leg = sl.HumanLeg(
        df.index[10], float(df["high"].iloc[10]), df.index[14], float(df["low"].iloc[14]), "down"
    )
    # force both anchors to snap to the SAME pivot → degenerate snap, dropped + logged, not imputed
    same = Pivot(12, df.index[12], 100.0, "high", 1.0)
    monkeypatch.setattr(
        art, "detect_pivots", lambda *a, **k: [same, Pivot(12, df.index[12], 100.0, "low", 1.0)]
    )
    monkeypatch.setattr(art, "_nearest_match", lambda *a, **k: same)
    rows = art.build_artifact_rows(df, [leg], cfg, pivot_cfg)
    assert rows[0].reached is True
    assert rows[0].snapped_clean is None  # no imputation
    assert rows[0].drop == "degenerate_snap_pa_eq_pb"


# --- checkpoint resume + study aggregation -----------------------------------------------------


def test_run_or_load_cell_writes_then_resumes(tmp_path, monkeypatch):
    calls = {"n": 0}

    def _fake_cell(tf, cfg, settings):  # noqa: ARG001 — stub
        calls["n"] += 1
        return {"timeframe": tf, "k": 3, "artifact_verdict": "artifact_risk_reduced"}

    monkeypatch.setattr(art, "run_artifact_cell", _fake_cell)
    cfg = sl.SelectionConfig()
    r1 = art._run_or_load_cell("4h", cfg, object(), tmp_path)
    r2 = art._run_or_load_cell("4h", cfg, object(), tmp_path)
    assert r1 == r2 and calls["n"] == 1  # second call loaded the checkpoint
    assert (tmp_path / "4h_k3.json").exists()


def test_run_or_load_cell_recomputes_on_seed_mismatch(tmp_path, monkeypatch):
    calls = {"n": 0}

    def _fake_cell(tf, cfg, settings):  # noqa: ARG001 — stub
        calls["n"] += 1
        return {"timeframe": tf}

    monkeypatch.setattr(art, "run_artifact_cell", _fake_cell)
    (tmp_path / "4h_k3.json").write_text(
        json.dumps({"seed": 999, "cell": {"stale": True}}), encoding="utf-8"
    )
    out = art._run_or_load_cell("4h", sl.SelectionConfig(), object(), tmp_path)
    assert calls["n"] == 1 and out == {"timeframe": "4h"}


def test_run_artifact_study_aggregates(tmp_path, monkeypatch):
    def _fake_cell(tf, cfg, settings):  # noqa: ARG001 — stub: 4h is the powered primary
        return {
            "timeframe": tf,
            "k": 3,
            "artifact_verdict": "artifact_risk_reduced"
            if tf == "4h"
            else "inconclusive_underpowered",
        }

    monkeypatch.setattr(art, "run_artifact_cell", _fake_cell)
    monkeypatch.setattr(art, "load_settings", lambda *a, **k: object())
    rep = art.run_artifact_study(None, sl.SelectionConfig(), ckpt_dir=tmp_path)
    assert rep["artifact_verdict"] == "artifact_risk_reduced"  # from the 4h primary
    assert len(rep["results_context_underpowered"]) == 3
    assert rep["matched_null"].startswith("NOT built")
    for name in ("4h_k3", "1M_k3", "1w_k3", "1d_k3"):
        assert (tmp_path / f"{name}.json").exists()

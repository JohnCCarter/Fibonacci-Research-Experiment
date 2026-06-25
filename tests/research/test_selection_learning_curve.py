"""Tests for the facit learning-curve diagnostic (learning-curve LOCK 2026-06-25).

Deterministic, no real corpus / network: build-once-vary-labels (the candidate universe + feature
matrices built once, only train labels vary), the fixed held-out test set, subsample unit = whole
human legs (L2/L3), the ASYMMETRIC blind verdict incl. the underpowered/noise branch (L4/L5), and
per-cell checkpoint resume. Shared machinery lives in ``selection_learning`` (sl); the curve pieces in
``selection_learning_curve`` (cv)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from fibengine.core.config import PivotConfig, ScoringConfig
from fibengine.research import selection_learning as sl
from fibengine.research import selection_learning_curve as cv


def _synthetic_df(n: int = 160) -> pd.DataFrame:
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


class _Data:
    def model_copy(self, update=None):  # noqa: ARG002 — TF ignored; load_candles is patched
        return self


class _Settings:
    def __init__(self, pivots, scoring):
        self.data = _Data()
        self.pivots = pivots
        self.scoring = scoring


def _legs_matching_candidates(df, pivot_cfg, cfg):
    """Craft human legs that ε-match real candidates: >=2 in the train period and >=1 in the test
    period, so the curve loop runs with positives on both sides of the fixed split."""
    from fibengine.pivots.detect import detect_pivots

    cands = sl.build_candidates(df, [], pivot_cfg, ScoringConfig(), cfg)
    by_index = {p.index: p for p in detect_pivots(df, pivot_cfg)}
    n = len(df)
    split = int(n * cfg.train_frac)

    def _leg(c):
        a, b = by_index.get(c.start_pos), by_index.get(c.anchor_b_pos)
        if a is None or b is None:
            return None
        return sl.HumanLeg(
            anchor_a_ts=df.index[c.start_pos],
            anchor_a_price=float(a.price),
            anchor_b_ts=df.index[c.anchor_b_pos],
            anchor_b_price=float(b.price),
            direction="",
        )

    train_legs, test_leg, seen_ends = [], None, set()
    for c in cands:
        win = sl.window_of(c.anchor_b_pos, split, n, cfg.k)
        leg = _leg(c)
        if leg is None:
            continue
        if win == "train" and c.anchor_b_pos not in seen_ends and len(train_legs) < 2:
            train_legs.append(leg)
            seen_ends.add(c.anchor_b_pos)
        elif win == "test" and test_leg is None:
            test_leg = leg
    assert train_legs and test_leg is not None, "synthetic should yield train+test matchable legs"
    return [*train_legs, test_leg]


# --- build-once / fixed test / subsample unit = whole legs (LOCK L2/L3) ------------------------


def test_curve_cell_build_once_fixed_test_and_whole_leg_subsample(monkeypatch):
    df = _synthetic_df(160)
    pivot_cfg = PivotConfig(mode="fractal", fractal_n=1, lookback=3, min_prominence_atr=0.0)
    cfg = sl.SelectionConfig(k=3)
    legs = _legs_matching_candidates(df, pivot_cfg, cfg)
    monkeypatch.setattr(cv, "REPEATS", 4)
    monkeypatch.setattr(cv, "load_candles", lambda *a, **k: df)
    monkeypatch.setattr(cv, "load_human_legs", lambda tf: legs)
    settings = _Settings(pivot_cfg, ScoringConfig())

    cell = cv.run_curve_cell("4h", 3, cfg, settings)

    assert cell["features"] == sl.live_feature_names(3)  # the 5-feature Stage-2 model (build-once)
    assert cell["n_test_positives"] >= 1  # fixed test set carries positives
    assert cell["n_train_legs"] >= 1
    pf = cell["per_fraction"]
    assert [s["fraction"] for s in pf] == list(cv.FRACTIONS)
    # subsample unit = whole human legs: n_retain == round(f * n_train_legs)
    n_legs = cell["n_train_legs"]
    for s in pf:
        assert s["n_retain"] == max(0, min(n_legs, round(s["fraction"] * n_legs)))
    top = next(s for s in pf if s["fraction"] == 1.0)
    assert top["repeats"] == 1  # f=1.0 is the deterministic single full-facit point
    assert cell["ap_full_facit"] == top["ap_mean"] is not None


def test_curve_cell_is_deterministic(monkeypatch):
    df = _synthetic_df(160)
    pivot_cfg = PivotConfig(mode="fractal", fractal_n=1, lookback=3, min_prominence_atr=0.0)
    cfg = sl.SelectionConfig(k=3)
    legs = _legs_matching_candidates(df, pivot_cfg, cfg)
    monkeypatch.setattr(cv, "REPEATS", 4)
    monkeypatch.setattr(cv, "load_candles", lambda *a, **k: df)
    monkeypatch.setattr(cv, "load_human_legs", lambda tf: legs)
    settings = _Settings(pivot_cfg, ScoringConfig())
    a = cv.run_curve_cell("4h", 3, cfg, settings)["per_fraction"]
    b = cv.run_curve_cell("4h", 3, cfg, settings)["per_fraction"]
    assert a == b  # same seed → identical curve (no hidden RNG state leak)


def test_curve_cell_no_positives_is_degenerate(monkeypatch):
    df = _synthetic_df(160)
    pivot_cfg = PivotConfig(mode="fractal", fractal_n=1, lookback=3, min_prominence_atr=0.0)
    cfg = sl.SelectionConfig(k=3)
    monkeypatch.setattr(cv, "load_candles", lambda *a, **k: df)
    monkeypatch.setattr(cv, "load_human_legs", lambda tf: [])  # no facit → all-negative universe
    settings = _Settings(pivot_cfg, ScoringConfig())
    cell = cv.run_curve_cell("4h", 3, cfg, settings)
    assert cell["per_fraction"] == [] and cell["powered"] is False
    assert cv.curve_verdict(cell) == "inconclusive_underpowered"


# --- seed determinism (LOCK L3) ----------------------------------------------------------------


def test_seed_for_is_deterministic_and_distinct():
    assert cv._seed_for(20260618, 2, 3) == 20260618 + 2000 + 3
    seeds = {cv._seed_for(100, fi, r) for fi in range(7) for r in range(64)}
    assert len(seeds) == 7 * 64  # every (fraction, repeat) gets a distinct seed


# --- ASYMMETRIC blind verdict (LOCK L4/L5) -----------------------------------------------------


def _pf(frac, mean, p5, p95):
    return {"fraction": frac, "ap_mean": mean, "ap_p5": p5, "ap_p95": p95}


def _cell(powered, per):
    return {"powered": powered, "per_fraction": per}


def test_curve_verdict_unpowered_is_inconclusive():
    assert cv.curve_verdict(_cell(False, [])) == "inconclusive_underpowered"
    assert (
        cv.curve_verdict(_cell(True, [_pf(1.0, 0.05, 0.05, 0.05)])) == "inconclusive_underpowered"
    )


def test_curve_verdict_noise_dominates_is_inconclusive():
    # f=0.95 band half-width (0.04) >= spread of means (0.02) → per-fraction noise dwarfs the curve
    per = [_pf(0.25, 0.05, 0.05, 0.05), _pf(0.95, 0.06, 0.02, 0.10), _pf(1.0, 0.07, 0.07, 0.07)]
    assert cv.curve_verdict(_cell(True, per)) == "inconclusive_underpowered"


def test_curve_verdict_data_starved():
    # tight 0.95 band (hw 0.005), last increment 0.03 > hw, curve rising, spread 0.04 > hw
    per = [_pf(0.25, 0.04, 0.04, 0.04), _pf(0.95, 0.05, 0.045, 0.055), _pf(1.0, 0.08, 0.08, 0.08)]
    assert cv.curve_verdict(_cell(True, per)) == "data_starved"


def test_curve_verdict_saturated():
    # last increment 0.001 within the 0.95 band (hw 0.005) → flat → saturated (expected default)
    per = [
        _pf(0.25, 0.05, 0.05, 0.05),
        _pf(0.95, 0.07, 0.065, 0.075),
        _pf(1.0, 0.071, 0.071, 0.071),
    ]
    assert cv.curve_verdict(_cell(True, per)) == "saturated"


# --- checkpoint / resume + study aggregation ---------------------------------------------------


def test_run_or_load_cell_writes_then_resumes(tmp_path, monkeypatch):
    calls = {"n": 0}

    def _fake_cell(tf, k, cfg, settings):  # noqa: ARG001 — stub, counts invocations
        calls["n"] += 1
        return {"timeframe": tf, "k": k, "powered": True}

    monkeypatch.setattr(cv, "run_curve_cell", _fake_cell)
    cfg = sl.SelectionConfig()
    r1 = cv._run_or_load_cell("4h", 3, cfg, object(), tmp_path)
    r2 = cv._run_or_load_cell("4h", 3, cfg, object(), tmp_path)
    assert r1 == r2 and calls["n"] == 1  # second call loaded the checkpoint, no recompute
    assert (tmp_path / "4h_k3.json").exists()
    assert not (tmp_path / "4h_k3.json.tmp").exists()


def test_run_curve_study_reads_verdict_from_4h_primary(tmp_path, monkeypatch):
    def _fake_cell(tf, k, cfg, settings):  # noqa: ARG001 — only 4h k=3 is the powered primary
        powered = tf == "4h" and k == 3
        sat = [
            _pf(0.25, 0.05, 0.05, 0.05),
            _pf(0.95, 0.07, 0.065, 0.075),
            _pf(1.0, 0.071, 0.071, 0.071),
        ]
        return {"timeframe": tf, "k": k, "powered": powered, "per_fraction": sat if powered else []}

    monkeypatch.setattr(cv, "run_curve_cell", _fake_cell)
    monkeypatch.setattr(cv, "load_settings", lambda *a, **k: object())
    rep = cv.run_curve_study(None, sl.SelectionConfig(), ckpt_dir=tmp_path)
    assert rep["results_4h_primary"]["k"] == 3
    assert len(rep["results_context_underpowered"]) == 3
    assert rep["learning_curve_verdict"] == "saturated"  # flat 4h primary curve
    for name in ("4h_k3", "1M_k3", "1w_k3", "1d_k3"):
        assert (tmp_path / f"{name}.json").exists()


def test_curve_preflight_delegates_to_shared_preflight(monkeypatch):
    seen = {}

    def _fake_preflight(config_path):
        seen["config"] = config_path
        return 0

    monkeypatch.setattr(cv, "run_preflight", _fake_preflight)
    assert cv.main(["--curve-preflight", "--config", "cfg.yaml"]) == 0
    assert seen["config"] == "cfg.yaml"

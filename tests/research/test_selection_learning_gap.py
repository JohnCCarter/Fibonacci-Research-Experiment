"""Tests for the retrospective-W / causal-availability-gap study (W-gap lock 2026-06-22).

Deterministic: the locked verdict thresholds (L5), viewport-relative recency (L9), the retrospective
feature whitelist, and a synthetic same-row reconstruction with exclusions — no real corpus /
network. Shared machinery lives in ``selection_learning`` (sl); the gap additions in
``selection_learning_gap`` (slg)."""

from __future__ import annotations

import json
from pathlib import Path

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


# --- frozen-data parity preflight -------------------------------------------------------------


def test_frozen_reference_covers_every_run_timeframe():
    # the preflight must check exactly the TFs the W-gap run touches, with both refs defined
    for tf in slg.PREFLIGHT_TIMEFRAMES:
        assert tf in slg.FROZEN_SNAPSHOT
        assert tf in slg.FROZEN_FACIT_COUNT
        assert set(slg.FROZEN_SNAPSHOT[tf]) == {"bars", "first_ts", "last_ts"}


def test_compare_fingerprint_exact_match_is_ok():
    ref = slg.FROZEN_SNAPSHOT["4h"]
    assert (
        slg.compare_fingerprint(
            "4h", ref["bars"], ref["first_ts"], ref["last_ts"], slg.FROZEN_FACIT_COUNT["4h"]
        )
        == []
    )


def test_compare_fingerprint_flags_each_drift():
    ref = slg.FROZEN_SNAPSHOT["4h"]
    facit = slg.FROZEN_FACIT_COUNT["4h"]
    # a refresh that appends one fresh bar shifts bars AND last_ts → both flagged
    mism = slg.compare_fingerprint(
        "4h", ref["bars"] + 1, ref["first_ts"], "2026-06-09T08:00:00+00:00", facit
    )
    assert any("bars" in m for m in mism)
    assert any("last_ts" in m for m in mism)
    # a dropped/added facit file is caught even when candles are pristine
    only_facit = slg.compare_fingerprint(
        "4h", ref["bars"], ref["first_ts"], ref["last_ts"], facit - 1
    )
    assert only_facit == [f"facit {facit - 1} != frozen {facit}"]


class _StubSettings:
    class _Data:
        def model_copy(self, update):  # noqa: ARG002 — only the timeframe matters downstream
            return self

    data = _Data()


def test_check_frozen_cell_fails_on_missing_cache(monkeypatch):
    monkeypatch.setattr(slg, "cache_path", lambda cfg: Path("nowhere/limit_8000.csv"))

    def _missing(cfg, fetch_if_missing, strict):  # noqa: ARG001 — fail-closed stand-in
        raise FileNotFoundError

    monkeypatch.setattr(slg, "load_candles", _missing)
    chk = slg.check_frozen_cell("4h", _StubSettings())
    assert not chk.ok
    assert "no cache" in chk.message


def test_check_frozen_cell_fails_on_empty_frame(monkeypatch):
    monkeypatch.setattr(slg, "cache_path", lambda cfg: Path("x/limit_8000.csv"))
    monkeypatch.setattr(slg, "load_candles", lambda cfg, fetch_if_missing, strict: pd.DataFrame())
    chk = slg.check_frozen_cell("4h", _StubSettings())
    assert not chk.ok
    assert "empty" in chk.message


# --- per-cell checkpoint / resume -------------------------------------------------------------


def test_run_or_load_cell_writes_then_resumes(tmp_path, monkeypatch):
    calls = {"n": 0}

    def _fake_cell(tf, k, w, cfg, settings):  # noqa: ARG001 — stub, counts invocations
        calls["n"] += 1
        return {"timeframe": tf, "k": k, "gap": -0.004, "powered": True}

    monkeypatch.setattr(slg, "run_gap_cell", _fake_cell)
    cfg = sl.SelectionConfig()
    r1 = slg._run_or_load_cell("4h", 3, 180, cfg, object(), tmp_path)
    r2 = slg._run_or_load_cell("4h", 3, 180, cfg, object(), tmp_path)
    assert r1 == r2 == {"timeframe": "4h", "k": 3, "gap": -0.004, "powered": True}
    assert calls["n"] == 1  # second call loaded from disk, did NOT recompute the ~70-min cell
    assert (tmp_path / "4h_k3.json").exists()
    assert not (tmp_path / "4h_k3.json.tmp").exists()  # atomic rename cleaned the temp


def test_run_or_load_cell_recomputes_on_seed_mismatch(tmp_path, monkeypatch):
    calls = {"n": 0}

    def _fake_cell(tf, k, w, cfg, settings):  # noqa: ARG001 — stub, counts invocations
        calls["n"] += 1
        return {"timeframe": tf, "k": k}

    monkeypatch.setattr(slg, "run_gap_cell", _fake_cell)
    # a checkpoint from a different seed must be ignored, not silently reused
    (tmp_path / "4h_k3.json").write_text(
        json.dumps({"seed": 999, "cell": {"stale": True}}), encoding="utf-8"
    )
    out = slg._run_or_load_cell("4h", 3, 180, sl.SelectionConfig(), object(), tmp_path)
    assert calls["n"] == 1
    assert out == {"timeframe": "4h", "k": 3}


def test_run_w_gap_study_checkpoints_every_cell_and_aggregates(tmp_path, monkeypatch):
    def _fake_cell(tf, k, w, cfg, settings):  # noqa: ARG001 — stub cell
        return {"timeframe": tf, "k": k, "powered": False, "gap_inference": None}

    monkeypatch.setattr(slg, "run_gap_cell", _fake_cell)
    monkeypatch.setattr(slg, "load_settings", lambda *a, **k: object())
    rep = slg.run_w_gap_study(None, sl.SelectionConfig(), ckpt_dir=tmp_path)
    assert [r["k"] for r in rep["results_4h"]] == [3, 6, 12]
    assert len(rep["results_context_underpowered"]) == 3
    assert "gap_verdict" in rep
    # all six cells persisted (3x 4h + 1M/1w/1d)
    for name in ("4h_k3", "4h_k6", "4h_k12", "1M_k3", "1w_k3", "1d_k3"):
        assert (tmp_path / f"{name}.json").exists()

"""Tests for the artifact-probe mechanics pass (DESCRIPTIVE-ONLY, mechanics PLAN 70174df).

Deterministic: the numpy-only descriptive stats (Spearman with ties, median/IQR), the per-cell
summaries (M1 size/length, M3 snap_span_delta asymmetry), and the descriptive-only contract (no
verdict key) — no real corpus / network. The probe rows come from ``selection_learning_artifact``."""

from __future__ import annotations

import numpy as np
import pytest

from fibengine.research import selection_learning as sl
from fibengine.research import selection_learning_artifact as art
from fibengine.research import selection_learning_artifact_mechanics as mech


def _row(
    reached, exact, span, mag=None, snap_delta=None, snapped=None, q="2020Q1", sa=None, sb=None
):
    return art.ArtifactRow(
        quarter=q,
        pos_a=0,
        pos_b=span,
        exact_clean=exact,
        reached=reached,
        snapped_clean=snapped,
        span_bars=span,
        magnitude_atr=mag,
        snap_span_delta=snap_delta,
        snap_a_idx=sa,
        snap_b_idx=sb,
    )


# --- descriptive stats -------------------------------------------------------------------------


def test_rankdata_average_ties():
    r = mech._rankdata(np.array([10.0, 20.0, 20.0, 40.0]))
    assert list(r) == [1.0, 2.5, 2.5, 4.0]  # tie at 20 → average of ranks 2,3


def test_spearman_monotone_constant_and_small():
    assert mech._spearman([1, 2, 3, 4], [10, 20, 30, 40]) == pytest.approx(1.0)
    assert mech._spearman([1, 2, 3, 4], [40, 30, 20, 10]) == pytest.approx(-1.0)
    assert mech._spearman([1, 2, 3], [5, 5, 5]) is None  # constant side
    assert mech._spearman([1, 2], [3, 4]) is None  # n<3


def test_median_iqr_and_empty():
    s = mech._median_iqr([1.0, 2.0, 3.0, 4.0])
    assert s["n"] == 4 and s["median"] == pytest.approx(2.5)
    assert mech._median_iqr([]) is None
    assert mech._median_iqr([None, None]) is None


def test_net_path_idx():
    closes = np.array([100.0, 110.0, 105.0, 115.0])
    net, path = mech._net_path_idx(closes, 0, 3)
    assert net == pytest.approx(15.0) and path == pytest.approx(25.0)  # |15|, 10+5+10
    assert mech._net_path_idx(closes, 2, 2) == (None, None)  # <2 bars


def test_flip_decomposition_net_vs_path_channel():
    # closes laid out in 3 regions so two snaps are PATH-dominated (clean down) and one is
    # NET-dominated (clean up) — the decomposition must recover that split.
    closes = np.array([100.0, 110.0, 108.0, 100.0, 130.0, 128.0, 130.0, 100.0, 110.0, 107.0])
    rows = [
        # A: extend [0,1]->[0,2] adds path -> clean down (path-dominated)
        _row(True, 1.0, span=1, snapped=8.0 / 12.0, sa=0, sb=2),
        # B: shrink [3,6]->[3,4] removes a wiggle -> clean up (net-dominated)
        _row(True, 30.0 / 34.0, span=3, snapped=1.0, sa=3, sb=4, q="2020Q2"),
        # C: extend [7,8]->[7,9] adds path -> clean down (path-dominated)
        _row(True, 1.0, span=1, snapped=7.0 / 13.0, sa=7, sb=9, q="2020Q3"),
    ]
    # row B's pos_a/pos_b must point at region B (3,6); _row uses pos_a=0,pos_b=span, so fix span=3
    rows[1].pos_a, rows[1].pos_b = 3, 6
    rows[2].pos_a, rows[2].pos_b = 7, 8
    f = mech._flip_decomposition(rows, closes)
    assert f["n_moved"] == 3 and f["n_total"] == 3
    # the d_clean <-> (rel_net - rel_path) link is the arithmetic identity → Spearman ≈ +1
    assert f["spearman_dclean_vs_net_minus_path_IDENTITY"] == pytest.approx(1.0)
    # two of three snaps are path-dominated (net_minus_path < 0) → overall path-dominated, frac=1/3
    assert f["median_net_minus_path"] < 0
    assert f["frac_net_dominates"] == pytest.approx(1.0 / 3.0)
    assert f["median_rel_path"] > f["median_rel_net"]
    assert mech._flip_decomposition([], closes) == {"n_total": 0, "n_moved": 0}


# --- per-cell descriptive mechanics (no verdict) ----------------------------------------------


class _NonEmpty:
    empty = False

    def __getitem__(self, key):  # df["close"] → object with .to_numpy() (flip needs closes)
        return _Col()


class _Col:
    def to_numpy(self):
        return np.zeros(0)


def _patch_cell(monkeypatch, rows):
    class _D:
        def model_copy(self, update):  # noqa: ARG002
            return self

    class _S:
        data = _D()
        pivots = None

    monkeypatch.setattr(mech, "load_candles", lambda *a, **k: _NonEmpty())
    monkeypatch.setattr(mech, "load_human_legs", lambda tf: [])  # noqa: ARG005
    monkeypatch.setattr(mech, "build_artifact_rows", lambda *a, **k: rows)
    return _S()


def test_run_mechanics_cell_descriptive_no_verdict(monkeypatch):
    rows = [
        _row(True, 0.70, span=40, mag=3.0, snap_delta=5, snapped=0.66),  # reached: long, less clean
        _row(True, 0.72, span=50, mag=3.5, snap_delta=3, snapped=0.69),
        _row(True, 0.74, span=45, mag=3.2, snap_delta=4, snapped=0.70),
        _row(False, 0.90, span=8, mag=0.8),  # unreached: short, cleaner
        _row(False, 0.92, span=6, mag=0.7),
        _row(False, 0.88, span=10, mag=0.9),
    ]
    settings = _patch_cell(monkeypatch, rows)
    cell = mech.run_mechanics_cell("4h", sl.SelectionConfig(k=3), settings)
    assert "verdict" not in cell  # descriptive-only — no verdict key
    assert cell["n_reached"] == 3 and cell["n_unreached"] == 3
    m1 = cell["M1_size_length_confound"]
    # reached legs are longer-span than unreached (M1 prediction direction)
    assert m1["span_bars_reached"]["median"] > m1["span_bars_unreached"]["median"]
    # cleanliness decreases with span over all legs → negative Spearman
    assert m1["spearman_cleanliness_span"] < 0
    m3 = cell["M3_snap_span_delta_asymmetry"]
    assert m3["n"] == 3 and m3["median_snap_span_delta"] > 0  # all snaps extend here
    assert m3["frac_extends_gt0"] == pytest.approx(1.0)


def test_run_mechanics_study_aggregates_no_verdict(monkeypatch):
    monkeypatch.setattr(
        mech, "run_mechanics_cell", lambda tf, cfg, s: {"timeframe": tf, "k": cfg.k}
    )
    monkeypatch.setattr(mech, "load_settings", lambda *a, **k: object())
    rep = mech.run_mechanics_study(None, sl.SelectionConfig())
    assert rep["descriptive_only"] is True and rep["no_verdict"] is True
    assert rep["results_4h"]["timeframe"] == "4h"
    assert len(rep["results_context"]) == 3
    assert "verdict" not in rep and "artifact_verdict" not in rep

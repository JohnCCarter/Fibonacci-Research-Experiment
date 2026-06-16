"""Tests for the context-conditioned BTC/Fib study (Lean Fib Research).

Hermetic: synthetic data, no network/corpus. Covers causal context flags, the rank permutation
test, Holm correction, the candidate gate, and the deep-level loader path.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from fibengine.research import fib_context_conditioned_study as c
from fibengine.research.fib_behaviour_event_study import EventStudyConfig, load_fib_levels
from fibengine.research.fib_context_conditioned_study import (
    DEEP_RATIOS,
    ContextConfig,
    _gate_one,
    _holm,
    _mde,
    main,
    rank_perm_p,
    trend_flags,
    vol_high_flags,
)

CFG = EventStudyConfig()
CTX = ContextConfig()


def _df(closes, *, freq="4h", spread=1.0):
    idx = pd.date_range("2018-01-01", periods=len(closes), freq=freq, tz="UTC")
    a = np.asarray(closes, dtype=float)
    return pd.DataFrame(
        {"open": a, "high": a + spread, "low": a - spread, "close": a, "volume": 1.0}, index=idx
    )


# --- causal context flags --------------------------------------------------------------------


def test_trend_flags_warmup_is_false():
    df = _df([100.0 + i for i in range(80)])
    flags = trend_flags(df, ContextConfig(trend_lookback=50, trend_median_window=60))
    assert flags[:50].sum() == 0  # warmup bars are never "in trend" (fail-closed)
    assert flags.dtype == bool


def test_trend_flags_are_causal_no_future_leak():
    base = [100.0 + 0.1 * i for i in range(120)]
    df1 = _df(base)
    df2 = _df(base + [200.0 + 5 * i for i in range(40)])  # very different future
    f1 = trend_flags(df1, CTX)
    f2 = trend_flags(df2, CTX)
    assert np.array_equal(f1, f2[: len(f1)])  # appending future never changes earlier flags


def test_vol_high_flags_causal_and_warmup_false():
    df = _df([100.0 + (i % 5) for i in range(120)])
    atr_s = np.linspace(1.0, 3.0, 120)
    flags = vol_high_flags(df, atr_s, CTX)
    assert flags.dtype == bool
    assert flags[:49].sum() == 0  # warmup (min_periods-1 bars) → not flagged


# --- rank permutation test -------------------------------------------------------------------


def test_rank_perm_p_deterministic_and_bounded():
    a = list(np.arange(40, dtype=float) + 5)
    b = list(np.arange(40, dtype=float))
    p1 = rank_perm_p(a, b, np.random.default_rng(CFG.seed), 2000)
    p2 = rank_perm_p(a, b, np.random.default_rng(CFG.seed), 2000)
    assert p1 == p2
    assert 0.0 < p1 <= 1.0


def test_rank_perm_p_none_on_tiny():
    assert rank_perm_p([1.0], [1.0, 2.0], np.random.default_rng(1), 100) is None


def test_rank_perm_detects_clear_separation():
    a = list(np.full(60, 10.0) + np.random.default_rng(0).normal(0, 0.1, 60))
    b = list(np.full(60, 0.0) + np.random.default_rng(1).normal(0, 0.1, 60))
    p = rank_perm_p(a, b, np.random.default_rng(CFG.seed), 3000)
    assert p < 0.05  # fully separated distributions are significant


# --- Holm correction -------------------------------------------------------------------------


def test_holm_passes_small_p_only():
    out = _holm({"trend": 0.01, "deep": 0.5}, 0.05)
    assert out["trend"] is True and out["deep"] is False


def test_holm_stops_at_first_failure():
    out = _holm({"trend": 0.04, "deep": 0.5}, 0.05)  # 0.04 > 0.05/2 → both fail
    assert out["trend"] is False and out["deep"] is False


def test_holm_none_pvalue_not_significant():
    out = _holm({"trend": None, "deep": 0.001}, 0.05)
    assert out["trend"] is False and out["deep"] is True


# --- MDE -------------------------------------------------------------------------------------


def test_mde_positive_and_none_on_tiny():
    vals = list(np.random.default_rng(0).normal(0, 4.0, 100))
    mde = _mde(vals, vals, 0.025)
    assert mde is not None and mde > 0
    assert _mde([1.0], [2.0, 3.0], 0.025) is None


# --- candidate gate --------------------------------------------------------------------------


def _ctx_stats(fib_mean, plc_mean, swing_mean, fib_tr, plc_tr, n=50):
    return {
        "fib": {"n": n, "mean": fib_mean, "median": fib_mean},
        "placebo": {"n": n, "mean": plc_mean, "median": plc_mean},
        "swing": {"n": n, "mean": swing_mean, "median": swing_mean},
        "fib_train": {"n": n, "mean": fib_tr, "median": fib_tr},
        "placebo_train": {"n": n, "mean": plc_tr, "median": plc_tr},
    }


def test_gate_candidate_requires_all():
    s = _ctx_stats(0.6, 0.1, 0.2, 0.5, 0.1)
    assert _gate_one(s, holm_sig=True, min_events=30)["candidate"] is True


def test_gate_fails_on_negative_train_sign():
    s = _ctx_stats(0.6, 0.1, 0.2, -0.3, 0.1)  # train sign negative
    g = _gate_one(s, holm_sig=True, min_events=30)
    assert g["candidate"] is False and g["train_same_sign"] is False


def test_gate_fails_when_not_significant():
    s = _ctx_stats(0.6, 0.1, 0.2, 0.5, 0.1)
    assert _gate_one(s, holm_sig=False, min_events=30)["candidate"] is False


def test_gate_fails_underpowered():
    s = _ctx_stats(0.6, 0.1, 0.2, 0.5, 0.1, n=10)  # below min_events
    assert _gate_one(s, holm_sig=True, min_events=30)["candidate"] is False


# --- deep-level loader + fail-closed ---------------------------------------------------------


def test_deep_loader_selects_only_deep_ratios(tmp_path, monkeypatch):
    import fibengine.research.fib_behaviour_event_study as base

    monkeypatch.setattr(base, "HUMAN_FIB_ROOT", tmp_path)
    levels = [{"ratio": r, "price": 100.0 + r * 100} for r in (0.382, 0.5, 0.618, 0.786)]
    payload = {
        "created_by": "human",
        "anchor_a": {"time": "2020-01-01T00:00:00+00:00", "price": 100.0},
        "anchor_b": {"time": "2020-02-01T00:00:00+00:00", "price": 200.0},
        "levels": levels,
    }
    d = tmp_path / "4h"
    d.mkdir()
    (d / "fib_a.json").write_text(json.dumps(payload), encoding="utf-8")
    deep = load_fib_levels("4h", CFG, ratios=DEEP_RATIOS)
    assert len(deep) == 2  # only 0.618 + 0.786
    deep_prices = sorted(round(x.price, 3) for x in deep)
    assert deep_prices == sorted([round(100.0 + 0.618 * 100, 3), round(100.0 + 0.786 * 100, 3)])


def test_main_rejects_1h():
    with pytest.raises(SystemExit):
        main(["--timeframes", "1h"])


def test_no_genesis_reference_in_source():
    from pathlib import Path

    src = Path(c.__file__).read_text(encoding="utf-8").lower()
    import_lines = [ln for ln in src.splitlines() if ln.strip().startswith(("import ", "from "))]
    assert not any("genesis" in ln for ln in import_lines)
    assert "genesis/" not in src and "genesis\\" not in src
    assert not any(bad in ln for ln in import_lines for bad in ("torch", "optuna", "sklearn"))

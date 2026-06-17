"""Tests for the causal BTC/Fib behaviour event study (Lean Fib Research).

Hermetic: synthetic candles/levels, no network, no real corpus required (except one
opt-in mutation guard on a temp file). Covers the prereg's fail-closed + causality rules.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from fibengine.research import fib_behaviour_event_study as m
from fibengine.research.fib_behaviour_event_study import (
    Event,
    EventStudyConfig,
    Level,
    _min_distance_series,
    _window_of,
    detect_swing_levels,
    event_reject,
    find_events,
    load_fib_levels,
    main,
    make_placebo_levels,
    permutation_p,
)

CFG = EventStudyConfig()


def _df(closes: list[float], *, freq: str = "4h", spread: float = 1.0) -> pd.DataFrame:
    idx = pd.date_range("2020-01-01", periods=len(closes), freq=freq, tz="UTC")
    c = np.asarray(closes, dtype=float)
    return pd.DataFrame(
        {"open": c, "high": c + spread, "low": c - spread, "close": c, "volume": 1.0},
        index=idx,
    )


# --- fail-closed -----------------------------------------------------------------------------


def test_reject_1h_fail_closed():
    with pytest.raises(ValueError, match="not allowed"):
        load_fib_levels("1h", CFG)
    with pytest.raises(SystemExit):
        main(["--timeframes", "1h"])


def test_empty_corpus_fail_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "HUMAN_FIB_ROOT", tmp_path)
    with pytest.raises(ValueError, match="no source fibs"):
        load_fib_levels("4h", CFG)


def test_naive_anchor_timestamp_fail_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "HUMAN_FIB_ROOT", tmp_path)
    bad = {
        "created_by": "human",
        "anchor_a": {"time": "2020-01-01T00:00:00", "price": 100.0},  # no tz
        "anchor_b": {"time": "2020-02-01T00:00:00+00:00", "price": 200.0},
        "levels": [{"ratio": r, "price": 100.0 + r} for r in (0.382, 0.5, 0.618, 0.786)],
    }
    d = tmp_path / "4h"
    d.mkdir()
    (d / "fib_x.json").write_text(json.dumps(bad), encoding="utf-8")
    with pytest.raises(ValueError, match="naive anchor"):
        load_fib_levels("4h", CFG)


# --- causality -------------------------------------------------------------------------------


def test_no_future_anchor_invisible_before_known():
    df = _df([100.0] * 10)
    known = pd.Timestamp(df.index[8])
    mindist, _ = _min_distance_series(df, [Level(known, 100.0)], level_active_bars=720)
    assert not np.isfinite(mindist[:8]).any()  # invisible before known_after_ts
    assert np.isfinite(mindist[8])  # visible at/after, price inside bar range -> dist 0
    assert mindist[8] == 0.0


def test_recency_window_expires_old_levels():
    df = _df([100.0] * 10)
    known = pd.Timestamp(df.index[0])
    mindist, _ = _min_distance_series(df, [Level(known, 100.0)], level_active_bars=3)
    assert np.isfinite(mindist[:3]).all()
    assert not np.isfinite(mindist[3:]).any()  # expired after recency window


# --- placebo: deterministic + matched ---------------------------------------------------------


def _fib_levels_sample(df):
    t0, t1 = pd.Timestamp(df.index[2]), pd.Timestamp(df.index[5])
    return [Level(t0, 110.0), Level(t0, 120.0), Level(t1, 130.0)]


def test_placebo_deterministic_same_seed():
    df = _df([100.0 + i for i in range(30)])
    fib = _fib_levels_sample(df)
    a = make_placebo_levels(fib, df, np.random.default_rng(CFG.seed))
    b = make_placebo_levels(fib, df, np.random.default_rng(CFG.seed))
    assert [x.price for x in a] == [x.price for x in b]


def test_placebo_differs_other_seed():
    df = _df([100.0 + i for i in range(30)])
    fib = _fib_levels_sample(df)
    a = make_placebo_levels(fib, df, np.random.default_rng(CFG.seed))
    b = make_placebo_levels(fib, df, np.random.default_rng(CFG.seed + 1))
    assert [x.price for x in a] != [x.price for x in b]


def test_placebo_matches_count_and_times():
    df = _df([100.0 + i for i in range(30)])
    fib = _fib_levels_sample(df)
    pl = make_placebo_levels(fib, df, np.random.default_rng(CFG.seed))
    assert len(pl) == len(fib)
    assert sorted(x.known_after_ts for x in pl) == sorted(x.known_after_ts for x in fib)


def test_placebo_price_in_causal_trailing_range():
    closes = [100.0 + i for i in range(30)]
    df = _df(closes, spread=1.0)
    t = pd.Timestamp(df.index[10])
    pl = make_placebo_levels([Level(t, 999.0)], df, np.random.default_rng(CFG.seed))
    prior = df[df.index < t]
    assert prior["low"].min() <= pl[0].price <= prior["high"].max()


# --- events: dedup / one per bar --------------------------------------------------------------


def test_one_event_per_bar_multiple_levels():
    df = _df([80.0, 100.5, 80.0], spread=3.0)  # bar1 range [97.5,103.5] covers both levels
    atr_s = np.array([10.0, 10.0, 10.0])
    levels = [Level(pd.Timestamp(df.index[0]), 100.0), Level(pd.Timestamp(df.index[0]), 101.0)]
    events = find_events(df, atr_s, levels, CFG, "4h")
    positions = [e.pos for e in events]
    assert positions == [1]  # one event despite two nearby levels


def test_fresh_touch_suppresses_lingering():
    df = _df([80.0, 100.0, 100.0, 100.0], spread=1.0)  # lingers at the level bars 1-3
    atr_s = np.array([10.0, 10.0, 10.0, 10.0])
    levels = [Level(pd.Timestamp(df.index[0]), 100.0)]
    events = find_events(df, atr_s, levels, CFG, "4h")
    assert [e.pos for e in events] == [1]  # only the fresh touch counts


# --- outcome calculation ---------------------------------------------------------------------


def test_event_reject_support_bounce():
    df = _df([90.0, 100.0, 106.0, 108.0], spread=1.0)
    atr_s = np.array([10.0, 10.0, 10.0, 10.0])
    ev = Event(pos=1, level=100.0, approach_side="above")  # support
    out = event_reject(df, atr_s, ev, horizon=2, react_eps=0.5)  # thr = 5
    assert out["reject"] is True  # 106 >= 100 + 5
    assert out["close_through"] is False
    assert out["abs_fwd_move_atr"] == pytest.approx(abs(108.0 - 100.0) / 10.0)


def test_event_close_through_break():
    df = _df([110.0, 100.0, 94.0, 92.0], spread=1.0)
    atr_s = np.array([10.0, 10.0, 10.0, 10.0])
    ev = Event(pos=1, level=100.0, approach_side="above")  # support
    out = event_reject(df, atr_s, ev, horizon=2, react_eps=0.5)
    assert out["close_through"] is True  # 94 <= 100 - 5
    assert out["reject"] is False


def test_event_reject_unavailable_horizon_returns_none():
    df = _df([90.0, 100.0, 106.0], spread=1.0)
    atr_s = np.array([10.0, 10.0, 10.0])
    ev = Event(pos=1, level=100.0, approach_side="above")
    assert event_reject(df, atr_s, ev, horizon=5, react_eps=0.5) is None


# --- OOS split -------------------------------------------------------------------------------


def test_window_split_no_overlap_and_embargo():
    n, split_idx, max_h = 100, 70, 10
    wins = [_window_of(p, split_idx, n, max_h) for p in range(n)]
    train = [p for p, w in enumerate(wins) if w == "train"]
    test = [p for p, w in enumerate(wins) if w == "test"]
    assert max(train) < split_idx  # train horizon never reaches the split
    assert all(p + max_h < split_idx for p in train)
    assert min(test) >= split_idx  # test starts at split
    assert set(train).isdisjoint(test)
    assert all(w is None for p, w in enumerate(wins) if split_idx - max_h <= p < split_idx)


# --- statistics ------------------------------------------------------------------------------


def test_permutation_deterministic_and_bounded():
    a = [True] * 30 + [False] * 10
    b = [True] * 10 + [False] * 30
    p1 = permutation_p(a, b, np.random.default_rng(CFG.seed), 2000)
    p2 = permutation_p(a, b, np.random.default_rng(CFG.seed), 2000)
    assert p1 == p2  # deterministic
    assert 0.0 < p1 <= 1.0
    assert permutation_p([], b, np.random.default_rng(CFG.seed), 2000) is None


# --- swing baseline --------------------------------------------------------------------------


def test_swing_levels_causal_and_static():
    # a clear peak at pos 5; confirmable only pivot_k bars later
    closes = [10, 11, 12, 13, 14, 20, 14, 13, 12, 11, 10]
    df = _df([float(x) for x in closes], spread=0.0)
    levels = detect_swing_levels(df, EventStudyConfig(pivot_k=2))
    peak = [lv for lv in levels if lv.price == 20.0]
    assert peak, "swing high at the peak should be detected"
    assert peak[0].known_after_ts == pd.Timestamp(df.index[5 + 2])  # known pivot_k bars later


# --- governance guards -----------------------------------------------------------------------


def test_no_genesis_reference_in_source():
    src = Path(m.__file__).read_text(encoding="utf-8").lower()
    import_lines = [ln for ln in src.splitlines() if ln.strip().startswith(("import ", "from "))]
    assert not any("genesis" in ln for ln in import_lines)  # no Genesis import
    assert "genesis/" not in src and "genesis\\" not in src  # no Genesis path usage
    assert not any(
        bad in ln for ln in import_lines for bad in ("torch", "optuna", "sklearn", "tensorflow")
    )


def test_source_labels_not_mutated(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "HUMAN_FIB_ROOT", tmp_path)
    payload = {
        "created_by": "human",
        "anchor_a": {"time": "2020-01-01T00:00:00+00:00", "price": 100.0},
        "anchor_b": {"time": "2020-02-01T00:00:00+00:00", "price": 200.0},
        "levels": [{"ratio": r, "price": 100.0 + r * 100} for r in (0.382, 0.5, 0.618, 0.786)],
    }
    d = tmp_path / "4h"
    d.mkdir()
    f = d / "fib_a.json"
    f.write_text(json.dumps(payload), encoding="utf-8")
    before = hashlib.sha256(f.read_bytes()).hexdigest()
    # auto-candidate sidecar must be ignored (no hindsight auto_candidate labels used)
    (d / "fib_a_events.json").write_text(
        json.dumps({"levels": [{"level": "0", "auto_candidate": "rejection_candidate"}]}),
        encoding="utf-8",
    )
    levels = load_fib_levels("4h", CFG)
    after = hashlib.sha256(f.read_bytes()).hexdigest()
    assert before == after  # read-only
    assert len(levels) == 4  # 4 interior ratios, sidecar excluded

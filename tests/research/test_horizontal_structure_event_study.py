"""B-1 harness mechanics — verified on synthetic frames (NOT the real BTC run, which is §12-gated).

Covers level generation (prior-extreme, RW-null), the §9 gate logic + anytime-valid e-Holm wiring,
and an end-to-end run on monkeypatched synthetic candles. No network, no cache, no fib JSON.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

import fibengine.research.horizontal_structure_event_study as hs
from fibengine.research.fib_behaviour_event_study import EventStudyConfig, Level


def _osc_frame(n: int, freq: str, period: float = 16.0, amp: float = 8.0) -> pd.DataFrame:
    i = np.arange(n)
    close = 100.0 + amp * np.sin(i / period)
    idx = pd.date_range("2024-01-01", periods=n, freq=freq, tz="UTC")
    return pd.DataFrame(
        {"open": close, "high": close + 1.5, "low": close - 1.5, "close": close, "volume": 1.0},
        index=idx,
    )


def test_monthly_prior_levels_rolls_prior_12():
    df = _osc_frame(20, "30D")  # stand-in monthly-ish frame
    levels = hs._monthly_prior_levels(df)
    assert len(levels) == 2 * (20 - 12)  # high+low for each bar from index 12 on
    # first emitted level is known at bar 12 and uses the max high over bars [0,12)
    assert levels[0].known_after_ts == pd.Timestamp(df.index[12])
    assert levels[0].price == pytest.approx(float(df["high"].to_numpy()[:12].max()))


def test_higher_tf_prior_levels_known_at_close():
    df = _osc_frame(5, "1D")
    levels = hs._higher_tf_prior_levels(df, "1d")
    assert len(levels) == 2 * 5
    # each level is known one full higher-TF period after the bar's open timestamp
    assert levels[0].known_after_ts == pd.Timestamp(df.index[0]) + pd.Timedelta(days=1)


def test_rw_null_deterministic_matched_and_skips():
    cfg = EventStudyConfig()
    df = _osc_frame(80, "4h")
    subj = [
        Level(pd.Timestamp(df.index[0]), 100.0),  # no prior history → skipped
        Level(pd.Timestamp(df.index[40]), 105.0),
        Level(pd.Timestamp(df.index[70]), 108.0),
    ]
    a = hs.rw_null_levels(subj, df, cfg, np.random.default_rng(cfg.seed), "4h")
    b = hs.rw_null_levels(subj, df, cfg, np.random.default_rng(cfg.seed), "4h")
    assert [lv.price for lv in a] == [lv.price for lv in b]  # deterministic given seed
    assert len(a) <= len(subj)  # count not forced; no-history level skipped
    assert {lv.known_after_ts for lv in a} <= {lv.known_after_ts for lv in subj}  # inherited ts


def test_test_counts():
    rows = [{"reject": True}, {"reject": False}, {"reject": True}]
    assert hs._test_counts(rows) == (2, 3)
    assert hs._test_counts([]) == (0, 0)


def _result(name, tf, k_s, n_s, k_c, n_c, train_s, train_c, evalue):
    rate = lambda k, n: k / n if n else None  # noqa: E731
    return {
        "timeframe": tf,
        "subjects": {
            name: {
                "subject": {
                    "test": {"n": n_s, "reject_rate": rate(k_s, n_s)},
                    "train": {"reject_rate": train_s},
                },
                "rw_null": {
                    "test": {"n": n_c, "reject_rate": rate(k_c, n_c)},
                    "train": {"reject_rate": train_c},
                },
                "evalue": evalue,
            }
        },
    }


def test_gate_robust_requires_all_four():
    cfg = EventStudyConfig()
    # subject clearly beats RW-null on test + train, huge e-value → robust
    strong = _result("swing", "1d", 40, 60, 15, 60, 0.6, 0.2, 1e6)
    gate = hs._gate([strong], cfg)
    g = gate["swing-1d"]
    assert g["robust"] is True
    assert g["e_holm_significant"] is True and g["beats_rw_null_test"] is True


def test_gate_fails_on_weak_evalue_and_low_n():
    cfg = EventStudyConfig()
    weak = _result("prior_extreme", "1w", 12, 20, 10, 20, 0.4, 0.45, 1.2)  # n<30, train sign wrong
    g = hs._gate([weak], cfg)["prior_extreme-1w"]
    assert g["robust"] is False
    assert g["n_events_ge_min"] is False
    assert 0.0 <= g["p_anytime_valid"] <= 1.0


def test_run_study_end_to_end_on_synthetic_frames(monkeypatch):
    frames = {"4h": _osc_frame(300, "4h"), "1d": _osc_frame(80, "1D")}

    class _FakeData:
        def __init__(self, tf):
            self.timeframe = tf

        def model_copy(self, update):
            return _FakeData(update["timeframe"])

    class _FakeSettings:
        def __init__(self):
            self.data = _FakeData("init")

    monkeypatch.setattr(hs, "load_settings", lambda *a, **k: _FakeSettings())
    monkeypatch.setattr(
        hs, "load_candles", lambda cfg, fetch_if_missing=False, strict=False: frames[cfg.timeframe]
    )

    report = hs.run_study(["4h"], None, EventStudyConfig())
    assert report["generated_by"] == "horizontal_structure_event_study"
    subjects = report["results"][0]["subjects"]
    assert set(subjects) == {"swing", "prior_extreme"}
    for s in subjects.values():
        assert s["evalue"] > 0.0  # always a valid positive e-value
        assert s["n_rw_null_levels"] <= s["n_levels"]
    assert set(report["gate"]) == {"swing-4h", "prior_extreme-4h"}
    assert isinstance(report["any_robust"], bool)
    for g in report["gate"].values():
        assert 0.0 <= g["p_anytime_valid"] <= 1.0

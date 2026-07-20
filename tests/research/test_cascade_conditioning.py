"""Tests for the cascade-conditioning probe (prereg 2026-07-20) — synthetic candles only."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from fibengine.evaluation.acceptance import MatchTier
from fibengine.research.cascade_conditioning import (
    Leg,
    bootstrap_gap,
    build_pairs,
    fresh_extreme_candidate,
    h1a_hits,
    order_legs,
    origin_hit,
    permutation_null,
    predecessor_of,
)


def _df(n: int = 60, start: str = "2024-01-01", freq: str = "4h") -> pd.DataFrame:
    idx = pd.date_range(start, periods=n, freq=freq, tz="UTC")
    base = 100.0 + np.linspace(0, 10, n)
    return pd.DataFrame(
        {
            "open": base,
            "high": base + 1.0,
            "low": base - 1.0,
            "close": base,
            "volume": np.ones(n),
        },
        index=idx,
    )


def _leg(fib_id: str, a_bar: int, b_bar: int, df: pd.DataFrame, direction: str = "up") -> Leg:
    a_ts, b_ts = df.index[a_bar], df.index[b_bar]
    col_a, col_b = ("low", "high") if direction == "up" else ("high", "low")
    return Leg(
        fib_id=fib_id,
        a_ts=a_ts,
        a_price=float(df[col_a].iloc[a_bar]),
        b_ts=b_ts,
        b_price=float(df[col_b].iloc[b_bar]),
        direction=direction,
    )


def test_order_and_predecessor_prefers_latest_completed_leg() -> None:
    df = _df()
    l1 = _leg("f1", 0, 10, df)
    l2 = _leg("f2", 5, 12, df, "down")
    cur = _leg("f3", 20, 30, df)
    assert [x.fib_id for x in order_legs([cur, l2, l1])] == ["f1", "f2", "f3"]
    # l2 completed later (bar 12 > 10) and before cur's origin -> l2 is the predecessor
    assert predecessor_of(cur, [l1, l2, cur]).fib_id == "f2"


def test_predecessor_allows_exact_chain_equality() -> None:
    df = _df()
    prev = _leg("prev", 0, 20, df)
    cur = _leg("cur", 20, 30, df, "down")  # cur.anchor_a.time == prev.anchor_b.time
    assert predecessor_of(cur, [prev, cur]).fib_id == "prev"


def test_build_pairs_excludes_first_and_degenerate_cur() -> None:
    df = _df()
    first = _leg("first", 0, 10, df)
    degen = _leg("degen", 15, 15, df)
    ok = _leg("ok", 20, 30, df)
    pairs, excl = build_pairs([first, degen, ok])
    assert [p.cur.fib_id for p in pairs] == ["ok"]
    assert excl == {"no_predecessor": 1, "degenerate_cur": 1}
    # a degenerate leg may still SERVE as predecessor (prereg §4.3)
    assert pairs[0].prev.fib_id == "degen"


def test_origin_hit_exact_chain_scores_exact() -> None:
    df = _df()
    prev = _leg("prev", 0, 20, df)
    cur = _leg("cur", 20, 30, df, "down")
    pairs, _ = build_pairs([prev, cur])
    tiers = h1a_hits(df, pairs)
    assert tiers == [MatchTier.EXACT]


def test_origin_hit_far_candidate_is_miss() -> None:
    df = _df()
    cur = _leg("cur", 40, 50, df)
    ok, tier = origin_hit(df, df.index[5], float(df["high"].iloc[5]) * 2.0, cur)
    assert not ok and tier == MatchTier.MISS


def test_permutation_null_is_deterministic_and_bounded() -> None:
    df = _df()
    legs = [_leg(f"f{i}", i * 5, i * 5 + 4, df) for i in range(6)]
    pairs, _ = build_pairs(legs)
    a = permutation_null(df, pairs, legs, n_perm=50, seed=1)
    b = permutation_null(df, pairs, legs, n_perm=50, seed=1)
    assert np.array_equal(a, b)
    assert ((a >= 0.0) & (a <= 1.0)).all()


def test_fresh_extreme_excludes_origin_bar() -> None:
    df = _df()
    df.iloc[25, df.columns.get_loc("high")] = 500.0  # interior spike
    prev = _leg("prev", 0, 20, df)
    cur = _leg("cur", 30, 40, df, "down")
    ts, price = fresh_extreme_candidate(df, build_pairs([prev, cur])[0][0])
    assert ts == df.index[25] and price == 500.0
    # empty in-between window -> None
    cur2 = _leg("cur2", 21, 40, df, "down")
    assert fresh_extreme_candidate(df, build_pairs([prev, cur2])[0][0]) is None


def test_bootstrap_gap_brackets_point_estimate() -> None:
    flags = [True] * 80 + [False] * 20
    lo, hi = bootstrap_gap(flags, null_mean=0.5, n_boot=500, seed=2)
    assert lo <= 0.8 - 0.5 <= hi
    lo2, hi2 = bootstrap_gap(flags, null_mean=0.5, n_boot=500, seed=2)
    assert (lo, hi) == (lo2, hi2)


def test_run_probe_refuses_on_corpus_drift(monkeypatch: pytest.MonkeyPatch) -> None:
    from fibengine.research import cascade_conditioning as cc

    monkeypatch.setattr(cc, "verify_manifest", lambda: ["4h: count 999 != manifest 371"])
    with pytest.raises(SystemExit, match="corpus drift"):
        cc.run_probe()


def test_prominence_candidate_sees_no_post_origin_bars(monkeypatch: pytest.MonkeyPatch) -> None:
    """Amendment A1: N2 pivot detection must run on the frame truncated at cur.anchor_a's bar."""
    from fibengine.research import cascade_conditioning as cc

    df = _df()
    prev = _leg("prev", 0, 20, df)
    cur = _leg("cur", 30, 40, df, "down")
    pair = build_pairs([prev, cur])[0][0]
    seen: dict[str, int] = {}

    def fake_detect(frame: pd.DataFrame, cfg) -> list:
        seen["n_bars"] = len(frame)
        return []

    monkeypatch.setattr(cc, "detect_pivots", fake_detect)
    assert cc.prominence_candidate(df, pair, None) is None
    assert seen["n_bars"] == 31  # bars 0..30 inclusive; nothing after cur.anchor_a


class _StubData:
    def model_copy(self, update=None):
        return self


def _run_cell_stubbed(
    monkeypatch: pytest.MonkeyPatch, timeframe: str, df: pd.DataFrame, legs: list[Leg]
) -> dict:
    from types import SimpleNamespace

    from fibengine.research import cascade_conditioning as cc

    monkeypatch.setattr(cc, "load_candles", lambda cfg, fetch_if_missing=False: df)
    monkeypatch.setattr(cc, "load_legs", lambda tf: legs)
    monkeypatch.setattr(cc, "detect_pivots", lambda frame, cfg: [])
    monkeypatch.setattr(cc, "N_PERM", 10)
    monkeypatch.setattr(cc, "N_BOOT", 10)
    settings = SimpleNamespace(data=_StubData(), pivots=None)
    return cc.run_cell(timeframe, settings)


def test_run_cell_context_cell_never_bears_verdict(monkeypatch: pytest.MonkeyPatch) -> None:
    """Amendment A3: even a powered (>=50 pairs) context cell must emit context_only."""
    df = _df(n=400)
    legs = [_leg(f"f{i:03d}", i * 6, i * 6 + 4, df) for i in range(60)]
    cell = _run_cell_stubbed(monkeypatch, "1d", df, legs)
    assert cell["role"] == "context"
    assert cell["n_pairs"] >= 50
    assert cell["verdict"] == "context_only"
    assert "h1a_hit_rate" in cell  # still reported, just verdict-less
    primary = _run_cell_stubbed(monkeypatch, "4h", df, legs)
    assert primary["role"] == "primary"
    assert primary["verdict"] in {"sequential_origin_signal", "no_sequential_signal"}


def test_run_cell_counts_outside_window_exclusion(monkeypatch: pytest.MonkeyPatch) -> None:
    """Amendment A4: cur anchors beyond the loaded candle frame are excluded and counted."""
    big = _df(n=100)
    small = big.iloc[:60]
    prev = _leg("prev", 0, 20, big)
    cur_in = _leg("cur_in", 30, 40, big, "down")
    cur_out = _leg("cur_out", 70, 80, big)  # beyond the 60-bar loaded frame
    cell = _run_cell_stubbed(monkeypatch, "1M", small, [prev, cur_in, cur_out])
    assert cell["exclusions"]["cur_outside_candle_window"] == 1
    assert cell["n_pairs"] == 1
    assert cell["first_ts"] == small.index[0].isoformat()
    assert cell["last_ts"] == small.index[-1].isoformat()

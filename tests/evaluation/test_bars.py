"""Memoized bar_of_timestamp: cached results must be byte-identical to fresh computation."""

import gc

import pandas as pd

from fibengine.evaluation import bars
from fibengine.evaluation.bars import bar_of_timestamp


def _frame(n=50, freq="4h"):
    idx = pd.date_range("2024-01-01", periods=n, freq=freq, tz="UTC")
    return pd.DataFrame({"close": range(n)}, index=idx)


def _fresh(df, ts):
    """Ground truth: compute with the cache cleared (the pre-memoization behavior)."""
    bars._CACHE.clear()
    return bar_of_timestamp(df, ts)


def test_cached_equals_fresh_across_cases():
    df = _frame()
    cases = [
        df.index[0].isoformat(),  # first bar
        df.index[17].isoformat(),  # exact interior bar
        df.index[-1].isoformat(),  # last bar
        (df.index[17] + pd.Timedelta(minutes=30)).isoformat(),  # off-grid, in window
        (df.index[17] + pd.Timedelta(hours=3)).isoformat(),  # beyond half-interval
        (df.index[0] - pd.Timedelta(days=2)).isoformat(),  # before window
        (df.index[-1] + pd.Timedelta(days=2)).isoformat(),  # after window
    ]
    expected = [_fresh(df, ts) for ts in cases]
    bars._CACHE.clear()
    first = [bar_of_timestamp(df, ts) for ts in cases]
    second = [bar_of_timestamp(df, ts) for ts in cases]  # served from cache
    assert first == expected
    assert second == expected


def test_sliced_frame_gets_its_own_entry():
    df = _frame()
    ts = df.index[40].isoformat()
    assert bar_of_timestamp(df, ts) == (40, True)
    truncated = df.iloc[:20]  # new index object -> must NOT reuse the parent's cache
    assert bar_of_timestamp(truncated, ts) == _fresh(truncated, ts)
    # and the parent's answer is still intact afterwards
    assert bar_of_timestamp(df, ts) == (40, True)


def test_empty_frame_returns_no_hit():
    empty = pd.DataFrame({"close": []}, index=pd.DatetimeIndex([], tz="UTC"))
    assert bar_of_timestamp(empty, "2024-01-01T00:00:00+00:00") == (0, False)


def test_cache_evicts_when_frame_is_garbage_collected():
    bars._CACHE.clear()
    df = _frame(n=10)
    bar_of_timestamp(df, df.index[3].isoformat())
    assert len(bars._CACHE) == 1
    del df
    gc.collect()
    assert len(bars._CACHE) == 0

"""Bar index lookup for evaluation (shared by metrics, pivot_recall, MTF layer)."""

from __future__ import annotations

import weakref

import numpy as np
import pandas as pd

# Memoization keyed on the *identity* of ``df.index``. The result depends only on
# (df.index, ts) and pandas indexes are immutable, so caching is exact — a result-neutral
# perf fix (the cascade probe spent ~25 min in repeated O(n) scans of the same frame;
# deferred until after sign-off, see the 2026-07-20 cascade results doc §Reproduce).
# Entries self-evict via weakref callback when the index is garbage-collected; a sliced
# frame (``df.iloc[...]``) has a *new* index object and therefore its own entry.
_CACHE: dict[int, dict] = {}


def _cache_for(index: pd.Index) -> dict:
    key = id(index)
    entry = _CACHE.get(key)
    if entry is not None and entry["ref"]() is index:
        return entry
    entry = {
        "ref": weakref.ref(index, lambda _ref, _key=key: _CACHE.pop(_key, None)),
        "half_interval": None,
        "hits": {},
    }
    _CACHE[key] = entry
    return entry


def _median_interval_seconds(df: pd.DataFrame) -> float:
    if len(df.index) < 2:
        return float("inf")
    deltas = np.diff(df.index.view("int64")) / 1e9
    return float(np.median(deltas))


def bar_of_timestamp(df: pd.DataFrame, ts: str) -> tuple[int, bool]:
    """Nearest bar index and whether the timestamp lies in the loaded window."""
    if len(df.index) == 0:
        pd.to_datetime(ts, utc=True)  # preserve raising on an invalid ts (pre-memoization)
        return 0, False
    entry = _cache_for(df.index)
    cached = entry["hits"].get(ts)
    if cached is not None:
        return cached
    # parse only on a cache miss — a cached ts already parsed successfully once
    target = pd.to_datetime(ts, utc=True)
    dist = np.abs((df.index - target).total_seconds())
    idx = int(np.argmin(dist))
    if entry["half_interval"] is None:
        entry["half_interval"] = _median_interval_seconds(df) / 2.0
    in_range = df.index.min() <= target <= df.index.max()
    in_window = bool(in_range and dist[idx] <= entry["half_interval"])
    entry["hits"][ts] = (idx, in_window)
    return idx, in_window

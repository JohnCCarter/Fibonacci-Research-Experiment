"""Zero-span (exact-price) signature resolution for the MTF confluence atlas (CP3 slice 3).

Kept separate from ``test_mtf_confluence_atlas`` only to respect the 300-line per-file bound.
Covers the ``max_span_log == 0`` exact-price requirement used by the c004/c006/c007 cards:
a span-0 cluster resolves, any nonzero span fails-closed. The full render of all three on the
real corpus (signature → unique cluster → band reconstruction == level_count) is exercised by
the module CLI, not snapshotted here (a synthetic zero-span corpus would blow the line bound).
"""

from __future__ import annotations

import pytest

from fibengine.research.mtf_confluence import ConfluenceCluster
from fibengine.research.mtf_confluence_atlas import C007_SIGNATURE, resolve_cluster


def _zero_span_cluster(price_span_log: float) -> ConfluenceCluster:
    """A c007-shaped 3-TF cluster (1w/1d/4h at ~9085, 2019 window) with a tunable span."""
    return ConfluenceCluster(
        cluster_id="c004",  # positional id under the current corpus (signature label is c007)
        epsilon_log=0.005,
        representative_price=9084.7,
        min_price=9084.7,
        max_price=9084.7,
        price_span_log=price_span_log,
        time_window_start="2019-07-04T00:00:00+00:00",
        time_window_end="2019-07-17T00:00:00+00:00",
        timeframe_count=3,
        level_count=4,
        timeframes=("1w", "1d", "4h"),
        ratios=(0.0,),
        member_fib_ids=("a", "b", "c", "d"),
    )


def test_zero_span_signature_matches_exact_price():
    assert resolve_cluster([_zero_span_cluster(0.0)], C007_SIGNATURE).cluster_id == "c004"


def test_zero_span_signature_rejects_nonzero_span():
    # max_span_log == 0: even a tiny nonzero span is not an exact-price coincidence.
    with pytest.raises(ValueError, match="No cluster matches"):
        resolve_cluster([_zero_span_cluster(0.0001)], C007_SIGNATURE)

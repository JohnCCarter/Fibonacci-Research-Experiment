"""Tests for mtf_confluence_atlas — MTF confluence visual atlas card (CP3 slice 1).

Covers signature resolution (unique / zero / ambiguous → fail-closed), deterministic band
reconstruction, the superseded / off-protocol member guards, the cluster-centric window +
fail-closed cache, and the structural summary contract + golden snapshot.

Deterministic: synthetic fibs (a single shared confluence price) + synthetic 1d candles via
monkeypatch; no candle cache, no PNG baselines, no pixel diffing. Regenerate the golden with:
UPDATE_SNAPSHOTS=1 pytest -k atlas
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import fibengine.research.mtf_confluence_atlas as atlas_mod
from fibengine.research.mtf_confluence import (
    ConfluenceCluster,
    LevelRow,
    cluster_confluence_fixed_band,
    flatten_levels,
)
from fibengine.research.mtf_confluence_atlas import (
    ClusterSignature,
    band_member_rows,
    render_confluence_card,
    resolve_cluster,
)
from fibengine.research.render_summary import cluster_atlas_summary

SNAP_DIR = Path(__file__).parent / "snapshots"

# A test signature pinned to the synthetic confluence (30000, 2021) so the test does not
# depend on the real corpus's ~29274 cluster.
TEST_SIGNATURE = ClusterSignature(
    tf_count=4,
    timeframes=frozenset({"1M", "1w", "1d", "4h"}),
    price_approx=30000.0,
    price_tol=10.0,
    max_span_log=0.005,
    window_year=2021,
    label="c001",
)

_RATIOS = (0.0, 0.382, 0.5, 0.618, 0.786, 1.0)


def _df_1d() -> pd.DataFrame:
    """A 1d frame spanning 2020-12 → 2021-12 so the 2021 cluster window fits with pad."""
    idx = pd.date_range("2020-12-01", periods=400, freq="1D", tz="UTC")
    base = np.linspace(20000, 60000, len(idx))
    return pd.DataFrame(
        {
            "open": base * 0.99,
            "high": base * 1.03,
            "low": base * 0.97,
            "close": base,
            "volume": np.ones(len(idx)),
        },
        index=idx,
    )


def _fake_load_candles(cfg, **_kw) -> pd.DataFrame:
    return _df_1d()


def _write_fib(
    fib_root: Path,
    *,
    tf: str,
    sid: str,
    a_time: str,
    b_time: str,
    lo: float,
    hi: float,
) -> Path:
    """Write a synthetic source fib under ``fib_root/<tf>/``; levels = lo + r*(hi-lo)."""
    tf_dir = fib_root / tf
    tf_dir.mkdir(parents=True, exist_ok=True)
    fid = f"fib_BTC-USD_{tf}_{sid}"
    payload = {
        "fib_id": fid,
        "symbol": "BTC/USD",
        "timeframe": tf,
        "exchange": "bitfinex",
        "created_by": "human",
        "source": "manual_labeling_tool",
        "scale_mode": "log",
        "levels_profile": "tradingview_log_chamoun",
        "anchor_a": {"time": a_time, "price": hi},
        "anchor_b": {"time": b_time, "price": lo},
        "direction": "up" if hi >= lo else "down",
        "levels": [{"ratio": r, "price": lo + r * (hi - lo)} for r in _RATIOS],
    }
    path = tf_dir / f"{fid}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


# Four fibs (1M/1w/1d/4h), each placing exactly one endpoint (ratio 0.0 or 1.0) at 30000 in
# overlapping 2021 windows; other levels distinct → a single 4-TF confluence at 30000.
_CORPUS = (
    ("1M", "20210401T000000", "2021-04-01T00:00:00Z", "2021-02-01T00:00:00Z", 30000.0, 90000.0),
    ("1w", "20210121T000000", "2021-05-01T00:00:00Z", "2021-02-15T00:00:00Z", 30000.0, 80000.0),
    ("1d", "20210127T000000", "2021-03-01T00:00:00Z", "2021-01-21T00:00:00Z", 20000.0, 30000.0),
    ("4h", "20210126T200000", "2021-03-15T00:00:00Z", "2021-01-25T00:00:00Z", 15000.0, 30000.0),
)


def _corpus(fib_root: Path) -> None:
    for tf, sid, a_time, b_time, lo, hi in _CORPUS:
        _write_fib(fib_root, tf=tf, sid=sid, a_time=a_time, b_time=b_time, lo=lo, hi=hi)


def _check_snapshot(name: str, data: dict) -> None:
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAP_DIR / name
    if os.environ.get("UPDATE_SNAPSHOTS"):
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert path.exists(), f"missing golden snapshot {path} (run UPDATE_SNAPSHOTS=1)"
    assert json.loads(path.read_text(encoding="utf-8")) == data


# --- signature resolution -------------------------------------------------------------


def _cluster(**kw) -> ConfluenceCluster:
    base = dict(
        cluster_id="c001",
        epsilon_log=0.005,
        representative_price=30000.0,
        min_price=30000.0,
        max_price=30000.0,
        price_span_log=0.0,
        time_window_start="2021-01-21T00:00:00+00:00",
        time_window_end="2021-06-01T00:00:00+00:00",
        timeframe_count=4,
        level_count=4,
        timeframes=("1M", "1w", "1d", "4h"),
        ratios=(0.0, 1.0),
        member_fib_ids=("a", "b", "c", "d"),
    )
    base.update(kw)
    return ConfluenceCluster(**base)


def test_resolve_unique_match():
    c = _cluster()
    assert resolve_cluster([c], TEST_SIGNATURE) is c


def test_resolve_zero_match_fails():
    # 3-TF cluster does not match a 4-TF signature.
    c = _cluster(timeframe_count=3, timeframes=("1w", "1d", "4h"))
    with pytest.raises(ValueError, match="No cluster matches"):
        resolve_cluster([c], TEST_SIGNATURE)


def test_resolve_ambiguous_match_fails():
    with pytest.raises(ValueError, match="Ambiguous"):
        resolve_cluster([_cluster(), _cluster(cluster_id="c002")], TEST_SIGNATURE)


def test_resolve_rejects_wrong_year():
    c = _cluster(
        time_window_start="2022-01-01T00:00:00+00:00",
        time_window_end="2022-06-01T00:00:00+00:00",
    )
    with pytest.raises(ValueError, match="No cluster matches"):
        resolve_cluster([c], TEST_SIGNATURE)


def test_resolve_rejects_span_over_signature():
    c = _cluster(price_span_log=0.01)
    with pytest.raises(ValueError, match="No cluster matches"):
        resolve_cluster([c], TEST_SIGNATURE)


# --- band reconstruction --------------------------------------------------------------


def test_band_member_rows_reconstructs_level_count(tmp_path):
    fib_root = tmp_path / "fibs"
    _corpus(fib_root)
    rows = flatten_levels(fib_root)
    clusters = cluster_confluence_fixed_band(rows, 0.005)
    cluster = resolve_cluster(clusters, TEST_SIGNATURE)
    band = band_member_rows(rows, cluster)
    assert len(band) == cluster.level_count == 4
    assert {r.timeframe for r in band} == {"1M", "1w", "1d", "4h"}
    assert all(cluster.min_price <= r.level_price <= cluster.max_price for r in band)
    # Deterministic order: timeframe rank then price.
    assert [r.timeframe for r in band] == ["1M", "1w", "1d", "4h"]


# --- member guards --------------------------------------------------------------------


def _row(tf: str, fib_id: str, source_path: str) -> LevelRow:
    return LevelRow(
        fib_id=fib_id,
        timeframe=tf,
        ratio=0.0,
        level_price=30000.0,
        log_price=10.3,
        anchor_start_time="2021-01-21T00:00:00+00:00",
        anchor_end_time="2021-06-01T00:00:00+00:00",
        direction="up",
        source_path=source_path,
    )


def test_guard_rejects_superseded_member():
    band = [_row("4h", "fib_BTC-USD_4h_20250506T080000", "x/fib_BTC-USD_4h_20250506T080000.json")]
    with pytest.raises(ValueError, match="superseded"):
        atlas_mod._guard_members(band)


def test_guard_rejects_off_protocol_timeframe():
    band = [_row("1h", "fib_BTC-USD_1h_20210101T000000", "x/fib_BTC-USD_1h_20210101T000000.json")]
    with pytest.raises(ValueError, match="not in"):
        atlas_mod._guard_members(band)


# --- full render + summary contract + golden snapshot ---------------------------------


def test_render_card_and_summary_snapshot(tmp_path, monkeypatch):
    fib_root = tmp_path / "fibs"
    _corpus(fib_root)
    monkeypatch.setattr(atlas_mod, "load_candles", _fake_load_candles)
    out_root = tmp_path / "out"

    card = render_confluence_card(
        fib_root=fib_root,
        signature=TEST_SIGNATURE,
        out_root=out_root,
    )

    assert card.cluster_id == "c001"
    assert card.method == "fixed_band"
    assert card.epsilon_log == 0.005
    assert card.backdrop_tf == "1d"
    assert card.timeframe_count == 4
    assert card.clean.exists() and card.levels.exists()
    # Output under fixed_band/<cluster_id>/, gitignored review tree.
    assert card.clean.parent == out_root / "fixed_band" / "c001"

    summary = cluster_atlas_summary(card, out_root)
    assert summary["flow"] == "mtf_confluence_atlas"
    assert summary["method"] == "fixed_band"
    assert summary["epsilon_log"] == 0.005
    assert summary["price_span_log"] == card.price_span_log  # CP2 metric present
    assert summary["member_count"] == 4
    assert not any("20250506T080000" in m for m in summary["member_fib_ids"])  # no superseded
    assert summary["clean"] == "fixed_band/c001/clean.png"  # relative fwd-slash
    assert str(tmp_path) not in json.dumps(summary)  # no absolute paths
    _check_snapshot("cluster_atlas_summary.json", summary)


def test_render_fails_closed_when_signature_absent(tmp_path, monkeypatch):
    fib_root = tmp_path / "fibs"
    _corpus(fib_root)
    monkeypatch.setattr(atlas_mod, "load_candles", _fake_load_candles)
    # A signature for a price that does not exist in the corpus.
    sig = ClusterSignature(
        tf_count=4,
        timeframes=frozenset({"1M", "1w", "1d", "4h"}),
        price_approx=99999.0,
        price_tol=5.0,
        max_span_log=0.005,
        window_year=2021,
        label="ghost",
    )
    with pytest.raises(ValueError, match="No cluster matches"):
        render_confluence_card(fib_root=fib_root, signature=sig, out_root=tmp_path / "out")

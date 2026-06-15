"""Tests for mtf_confluence — report-only MTF level confluence table, stdlib."""

from __future__ import annotations

import json
import math
from pathlib import Path

from fibengine.research.mtf_confluence import (
    CONFLUENCE_FIELDS,
    LEVEL_FIELDS,
    LevelRow,
    cluster_confluence,
    flatten_levels,
    order_clusters,
    write_confluence_csv,
)

RATIOS = (0.0, 0.382, 0.5, 0.618, 0.786, 1.0)


def _write_fib(
    root: Path,
    *,
    tf: str,
    sid: str,
    a_time: str,
    a_price: float,
    b_time: str,
    b_price: float,
) -> Path:
    fib_dir = root / tf
    fib_dir.mkdir(parents=True, exist_ok=True)
    fid = f"fib_BTC-USD_{tf}_{sid}"
    lo, hi = min(a_price, b_price), max(a_price, b_price)
    levels = [{"ratio": r, "price": round(hi - r * (hi - lo), 8)} for r in RATIOS]
    path = fib_dir / f"{fid}.json"
    path.write_text(
        json.dumps(
            {
                "fib_id": fid,
                "symbol": "BTC/USD",
                "timeframe": tf,
                "anchor_a": {"time": a_time, "price": a_price},
                "anchor_b": {"time": b_time, "price": b_price},
                "direction": "up" if b_price > a_price else "down",
                "levels": levels,
            }
        ),
        encoding="utf-8",
    )
    return path


def _row(tf: str, fib_id: str, price: float, start: str, end: str, ratio: float = 0.0) -> LevelRow:
    return LevelRow(
        fib_id=fib_id,
        timeframe=tf,
        ratio=ratio,
        level_price=price,
        log_price=math.log(price),
        anchor_start_time=start,
        anchor_end_time=end,
        direction="up",
        source_path=f"{tf}/{fib_id}.json",
    )


def test_flatten_levels_six_rows_per_fib_and_fields(tmp_path):
    _write_fib(
        tmp_path,
        tf="4h",
        sid="x",
        a_time="2021-01-01T00:00:00+00:00",
        a_price=100.0,
        b_time="2021-01-02T00:00:00+00:00",
        b_price=200.0,
    )
    rows = flatten_levels(tmp_path)
    assert len(rows) == 6  # one fib, six levels
    r = rows[0]
    assert r.timeframe == "4h"
    assert r.anchor_start_time == "2021-01-01T00:00:00+00:00"
    assert r.anchor_end_time == "2021-01-02T00:00:00+00:00"
    assert r.log_price == math.log(r.level_price)
    assert {row.ratio for row in rows} == set(RATIOS)


def test_flatten_excludes_sidecars(tmp_path):
    _write_fib(
        tmp_path,
        tf="1d",
        sid="x",
        a_time="2021-01-01T00:00:00+00:00",
        a_price=100.0,
        b_time="2021-01-05T00:00:00+00:00",
        b_price=200.0,
    )
    # A sidecar that also matches fib_*.json must be ignored.
    (tmp_path / "1d" / "fib_BTC-USD_1d_x_events.json").write_text("[]", encoding="utf-8")
    rows = flatten_levels(tmp_path)
    assert len(rows) == 6
    assert all("_events" not in r.source_path for r in rows)


def test_flatten_does_not_mutate_source(tmp_path):
    p = _write_fib(
        tmp_path,
        tf="4h",
        sid="x",
        a_time="2021-01-01T00:00:00+00:00",
        a_price=100.0,
        b_time="2021-01-02T00:00:00+00:00",
        b_price=200.0,
    )
    before = p.read_bytes()
    flatten_levels(tmp_path)
    assert p.read_bytes() == before


def test_proximity_required_for_cluster():
    # Same time window, far apart in log-price -> no cluster.
    rows = [
        _row("1d", "f_1d", 100.0, "2021-01-01T00:00:00+00:00", "2021-01-10T00:00:00+00:00"),
        _row("4h", "f_4h", 100000.0, "2021-01-01T00:00:00+00:00", "2021-01-10T00:00:00+00:00"),
    ]
    assert cluster_confluence(rows, epsilon_log=0.005) == []


def test_time_overlap_required_for_cluster():
    # Near in price, disjoint in time -> no cluster.
    rows = [
        _row("1d", "f_1d", 100.0, "2021-01-01T00:00:00+00:00", "2021-01-02T00:00:00+00:00"),
        _row("4h", "f_4h", 100.1, "2022-01-01T00:00:00+00:00", "2022-01-02T00:00:00+00:00"),
    ]
    assert cluster_confluence(rows, epsilon_log=0.005) == []


def test_cross_timeframe_required():
    # Near in price + overlapping time but only ONE timeframe -> dropped.
    rows = [
        _row("4h", "f_a", 100.0, "2021-01-01T00:00:00+00:00", "2021-01-10T00:00:00+00:00"),
        _row("4h", "f_b", 100.1, "2021-01-05T00:00:00+00:00", "2021-01-15T00:00:00+00:00"),
    ]
    assert cluster_confluence(rows, epsilon_log=0.005, min_timeframes=2) == []


def test_two_timeframe_cluster_is_found():
    rows = [
        _row("1d", "f_1d", 100.0, "2021-01-01T00:00:00+00:00", "2021-01-10T00:00:00+00:00"),
        _row("4h", "f_4h", 100.1, "2021-01-05T00:00:00+00:00", "2021-01-15T00:00:00+00:00"),
    ]
    clusters = cluster_confluence(rows, epsilon_log=0.005)
    assert len(clusters) == 1
    c = clusters[0]
    assert c.timeframe_count == 2
    assert c.level_count == 2
    assert c.timeframes == ("1d", "4h")
    assert c.cluster_id == "c001"


def test_deterministic_ordering_and_ids():
    # Cluster A: 3 TFs; cluster B: 2 TFs. A must sort first regardless of input order.
    rows = [
        # cluster B (2 TF, ~50000)
        _row("1d", "b_1d", 50000.0, "2020-01-01T00:00:00+00:00", "2020-02-01T00:00:00+00:00"),
        _row("4h", "b_4h", 50010.0, "2020-01-05T00:00:00+00:00", "2020-02-05T00:00:00+00:00"),
        # cluster A (3 TF, ~100)
        _row("1M", "a_1M", 100.0, "2021-01-01T00:00:00+00:00", "2021-03-01T00:00:00+00:00"),
        _row("1w", "a_1w", 100.1, "2021-01-10T00:00:00+00:00", "2021-02-10T00:00:00+00:00"),
        _row("1d", "a_1d", 100.2, "2021-01-15T00:00:00+00:00", "2021-02-15T00:00:00+00:00"),
    ]
    clusters = cluster_confluence(rows, epsilon_log=0.005)
    assert [c.cluster_id for c in clusters] == ["c001", "c002"]
    assert clusters[0].timeframe_count == 3  # higher tf_count sorts first
    assert clusters[1].timeframe_count == 2
    # order_clusters is idempotent on an already-ordered list
    again = order_clusters(list(clusters))
    assert [c.cluster_id for c in again] == ["c001", "c002"]


def test_confluence_csv_header_stable(tmp_path):
    rows = [
        _row("1d", "f_1d", 100.0, "2021-01-01T00:00:00+00:00", "2021-01-10T00:00:00+00:00"),
        _row("4h", "f_4h", 100.1, "2021-01-05T00:00:00+00:00", "2021-01-15T00:00:00+00:00"),
    ]
    clusters = cluster_confluence(rows, epsilon_log=0.005)
    out = write_confluence_csv(tmp_path / "conf.csv", clusters)
    header = out.read_text(encoding="utf-8").splitlines()[0]
    assert header == ",".join(CONFLUENCE_FIELDS)


def test_level_fields_constant_shape():
    assert LEVEL_FIELDS[0] == "fib_id"
    assert "log_price" in LEVEL_FIELDS
    assert LEVEL_FIELDS[-1] == "source_path"

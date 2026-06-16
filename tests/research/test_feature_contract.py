"""Tests for feature_contract — Phase 2 dummy contract validator, stdlib-only.

Proves the question: can a future external Fib feature contract be validated
mechanically, without leakage and without any Genesis coupling? No real export, no
fib computation, no Genesis import.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from fibengine.research.feature_contract import (
    BAR_FEATURE_FIELDS,
    BAR_JOIN_KEYS,
    BAR_META_FIELDS,
    BAR_TABLE_FIELDS,
    ZONE_REGISTRY_FIELDS,
    BarRow,
    ZoneRow,
    check_causality,
    check_join_keys,
    read_bar_features,
    read_zone_registry,
    validate_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DUMMY = REPO_ROOT / "docs/research_wiki/reviews/contracts/phase2_dummy"


def _zone(**over) -> dict[str, str]:
    base = {
        "zone_id": "zone_x",
        "symbol": "BTC/USD",
        "method": "fixed_band",
        "epsilon_log": "0.005",
        "zone_price_repr": "29274.0",
        "zone_price_min": "29247.0",
        "zone_price_max": "29283.0",
        "price_span_log": "0.00123",
        "tf_count": "4",
        "level_count": "4",
        "timeframes": "1M,1w,1d,4h",
        "ratios": "0.5,0.618,0.618,0.786",
        "anchor_a_min": "2021-01-01T00:00:00Z",
        "anchor_b_max": "2021-05-01T00:00:00Z",
        "known_after_ts": "2021-05-03T00:00:00Z",
        "confirmation_buffer_hours": "48",
        "source_member_count": "4",
        "feature_version": "v0",
    }
    base.update(over)
    return base


def _bar(**over) -> dict[str, str]:
    base = dict.fromkeys(BAR_TABLE_FIELDS, "0")
    base.update(
        {
            "symbol": "BTC/USD",
            "timeframe": "1d",
            "timestamp": "2021-06-01T00:00:00Z",
            "feature_version": "v0",
            "in_confluence_band": "false",
            "nearest_zone_method": "fixed_band",
            "has_robust_4tf_zone_nearby": "true",
            "meta_referenced_zone_ids": "zone_x",
        }
    )
    base.update(over)
    return base


# --- Committed dummy artifact is genuine ---------------------------------------------


def test_committed_dummy_pair_validates():
    summary = validate_contract(DUMMY / "zone_registry.csv", DUMMY / "bar_features.csv")
    assert summary["zones"] == 3 and summary["bars"] == 4
    assert summary["timeframes"] == ["1d", "1w", "4h"]


# --- Schema --------------------------------------------------------------------------


def test_schema_field_sets_stable():
    assert ZONE_REGISTRY_FIELDS[0] == "zone_id" and "known_after_ts" in ZONE_REGISTRY_FIELDS
    assert len(ZONE_REGISTRY_FIELDS) == 18
    assert BAR_JOIN_KEYS == ("symbol", "timeframe", "timestamp")
    assert BAR_TABLE_FIELDS[-1] == "meta_referenced_zone_ids"


def test_read_rejects_header_drift(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("foo,bar\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="header"):
        read_zone_registry(bad)
    with pytest.raises(ValueError, match="header"):
        read_bar_features(bad)


# --- Feature / metadata boundary (mechanical invariant) ------------------------------


def test_feature_metadata_boundary_disjoint():
    assert not (set(BAR_META_FIELDS) & set(BAR_FEATURE_FIELDS))
    assert not (set(BAR_META_FIELDS) & set(BAR_JOIN_KEYS))
    assert "meta_referenced_zone_ids" in BAR_META_FIELDS
    assert "meta_referenced_zone_ids" not in BAR_FEATURE_FIELDS


# --- Join keys -----------------------------------------------------------------------


def test_join_keys_must_be_non_null():
    with pytest.raises(ValueError, match="symbol"):
        BarRow.from_row(_bar(symbol=""))
    with pytest.raises(ValueError, match="timestamp"):
        BarRow.from_row(_bar(timestamp=""))


def test_duplicate_join_key_rejected():
    bars = [BarRow.from_row(_bar()), BarRow.from_row(_bar())]  # identical (symbol, tf, ts)
    errors = check_join_keys(bars)
    assert errors and "duplicate join key" in errors[0]


def test_distinct_join_keys_ok():
    bars = [
        BarRow.from_row(_bar(timestamp="2021-06-01T00:00:00Z")),
        BarRow.from_row(_bar(timestamp="2021-06-02T00:00:00Z")),
    ]
    assert check_join_keys(bars) == []


# --- Causality: known_after_ts <= timestamp ------------------------------------------


def test_causality_leakage_rejected():
    # Zone becomes known AFTER the bar timestamp -> leakage.
    zones = [ZoneRow.from_row(_zone(zone_id="zone_x", known_after_ts="2021-12-01T00:00:00Z"))]
    bars = [
        BarRow.from_row(_bar(timestamp="2021-06-01T00:00:00Z", meta_referenced_zone_ids="zone_x"))
    ]
    errors = check_causality(bars, zones)
    assert errors and "LEAKAGE" in errors[0]


def test_causality_known_zone_ok():
    zones = [ZoneRow.from_row(_zone(zone_id="zone_x", known_after_ts="2021-05-03T00:00:00Z"))]
    bars = [
        BarRow.from_row(_bar(timestamp="2021-06-01T00:00:00Z", meta_referenced_zone_ids="zone_x"))
    ]
    assert check_causality(bars, zones) == []


def test_causality_multi_zone_set_checked():
    # A row causal at its nearest zone but referencing a not-yet-known zone is still leakage.
    zones = [
        ZoneRow.from_row(_zone(zone_id="z_known", known_after_ts="2021-05-03T00:00:00Z")),
        ZoneRow.from_row(_zone(zone_id="z_future", known_after_ts="2022-01-01T00:00:00Z")),
    ]
    bars = [
        BarRow.from_row(
            _bar(timestamp="2021-06-01T00:00:00Z", meta_referenced_zone_ids="z_known;z_future")
        )
    ]
    errors = check_causality(bars, zones)
    assert any("z_future" in e and "LEAKAGE" in e for e in errors)


def test_causality_unknown_zone_id_rejected():
    zones = [ZoneRow.from_row(_zone(zone_id="zone_x"))]
    bars = [BarRow.from_row(_bar(meta_referenced_zone_ids="zone_ghost"))]
    errors = check_causality(bars, zones)
    assert errors and "unknown zone_id" in errors[0]


# --- Zone-knowability floor (known_after_ts >= anchor_b_max + buffer) -----------------


def test_knowability_floor_violation_rejected():
    with pytest.raises(ValueError, match="knowability"):
        # buffer 48h after 2021-05-01 => floor 2021-05-03; this is one hour early.
        ZoneRow.from_row(_zone(known_after_ts="2021-05-02T23:00:00Z"))


def test_knowability_stricter_than_floor_allowed():
    # "or stricter": known_after later than the floor is fine.
    zone = ZoneRow.from_row(_zone(known_after_ts="2021-06-01T00:00:00Z"))
    assert zone.zone_id == "zone_x"


# --- 1H fail-closed (Phase 1 §5.2) ---------------------------------------------------


def test_bar_rejects_1h_timeframe():
    with pytest.raises(ValueError, match="no 1H"):
        BarRow.from_row(_bar(timeframe="1h"))


def test_zone_rejects_1h_member_timeframe():
    with pytest.raises(ValueError, match="no 1H"):
        ZoneRow.from_row(_zone(timeframes="1d,4h,1h", tf_count="3"))


# --- Other fail-closed row checks ----------------------------------------------------


def test_zone_rejects_bad_method():
    with pytest.raises(ValueError, match="invalid method"):
        ZoneRow.from_row(_zone(method="kmeans"))


def test_zone_rejects_price_ordering():
    with pytest.raises(ValueError, match="price ordering"):
        ZoneRow.from_row(_zone(zone_price_min="30000.0"))  # min > repr


def test_zone_rejects_tf_count_mismatch():
    with pytest.raises(ValueError, match="distinct timeframes"):
        ZoneRow.from_row(_zone(timeframes="1d,4h", tf_count="4"))


def test_bar_rejects_naive_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        BarRow.from_row(_bar(timestamp="2021-06-01T00:00:00"))


def test_bar_rejects_bad_feature_type():
    with pytest.raises(ValueError, match="not a float"):
        BarRow.from_row(_bar(nearest_confluence_price="cheap"))

"""Tests for review_ledger — source-quality verdict tracking, stdlib-only."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fibengine.research.review_ledger import (
    LEDGER_FIELDS,
    LedgerRow,
    read_ledger,
    row_for_source_fib,
    source_hash,
    write_ledger,
)


def _write_fib(path: Path, *, fib_id: str = "fib_BTC-USD_4h_20171228T200000") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"fib_id": fib_id, "symbol": "BTC/USD", "timeframe": "4h", "anchor_a": {}}),
        encoding="utf-8",
    )
    return path


def _row(**over) -> LedgerRow:
    base = dict(
        fib_id="fib_BTC-USD_4h_20170702T040000",
        symbol="BTC/USD",
        timeframe="4h",
        scope="2017_h2",
        review_type="tier2_zoom",
        verdict="ok",
        status="accepted",
        note="clean",
        source_fib_path="data/labels/.../fib.json",
        artifact_path="experiments/review/.../",
        source_hash="sha256:deadbeefdeadbeef",
        reviewed_at="2026-06-15",
        reviewer="human",
    )
    base.update(over)
    return LedgerRow(**base)


def test_source_hash_deterministic_and_content_sensitive(tmp_path):
    f = _write_fib(tmp_path / "fib.json")
    h1 = source_hash(f)
    h2 = source_hash(f)
    assert h1 == h2 and h1.startswith("sha256:")
    f.write_text(f.read_text(encoding="utf-8") + " ", encoding="utf-8")
    assert source_hash(f) != h1  # any edit changes the reference


def test_validate_rejects_bad_verdict_and_status():
    with pytest.raises(ValueError, match="invalid verdict"):
        _row(verdict="great").validate()
    with pytest.raises(ValueError, match="invalid status"):
        _row(status="maybe").validate()


def test_validate_rejects_empty_fib_id():
    with pytest.raises(ValueError, match="fib_id"):
        _row(fib_id="").validate()


def test_correction_candidate_is_representable():
    row = _row(verdict="suspicious", status="correction-candidate").validate()
    assert row.verdict == "suspicious" and row.status == "correction-candidate"


@pytest.mark.parametrize("verdict", ["ok", "ok-with-note", "watchlist", "suspicious"])
def test_all_verdicts_accepted(verdict):
    _row(verdict=verdict).validate()


def test_write_read_roundtrip_preserves_rows(tmp_path):
    rows = [_row(), _row(verdict="suspicious", status="correction-candidate", note="a, b")]
    out = write_ledger(tmp_path / "ledger.csv", rows)
    back = read_ledger(out)
    assert [r.fib_id for r in back] == [r.fib_id for r in rows]
    assert back[1].note == "a, b"  # comma survives CSV quoting
    assert back[1].status == "correction-candidate"


def test_read_rejects_wrong_header(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("foo,bar\n1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="header"):
        read_ledger(bad)


def test_row_for_source_fib_pulls_identity_and_hash(tmp_path):
    f = _write_fib(tmp_path / "fib_BTC-USD_4h_20171228T200000.json")
    row = row_for_source_fib(
        f,
        scope="2017_h2",
        review_type="tier2_zoom",
        verdict="suspicious",
        status="correction-candidate",
        note="better anchor_a adjacent to leg A",
        artifact_path="experiments/review/fourh_source_fib_zoom/2017_h2/",
        reviewed_at="2026-06-15",
    )
    assert row.fib_id == "fib_BTC-USD_4h_20171228T200000"
    assert row.symbol == "BTC/USD" and row.timeframe == "4h"
    assert row.source_hash == source_hash(f)
    assert row.status == "correction-candidate"


def test_ledger_fields_stable():
    # The CSV schema is a contract; lock the column set/order.
    assert LEDGER_FIELDS[0] == "fib_id" and "source_hash" in LEDGER_FIELDS
    assert len(LEDGER_FIELDS) == 13

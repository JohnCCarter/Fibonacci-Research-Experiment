import json

import pytest

from fibengine.research.level_event_review_tool import (
    _load_anchor_overrides,
    _load_rows,
    _override_key,
    _save_anchor_overrides,
)


def test_load_rows_from_jsonl(tmp_path):
    run_dir = tmp_path / "review_run"
    run_dir.mkdir()
    row = {"review_id": "x", "human_label": "", "auto_candidate": "rejection_candidate"}
    (run_dir / "review_sample.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    loaded = _load_rows(run_dir)
    assert len(loaded) == 1
    assert loaded[0]["review_id"] == "x"


# ---------------------------------------------------------------------------
# Anchor override: key derivation
# ---------------------------------------------------------------------------


def test_override_key_uses_fib_id_and_event_time():
    row = {"fib_id": "fib_BTC-USD_1d_20230101T000000", "event_time": "2023-03-15T08:00:00+00:00"}
    assert _override_key(row) == "fib_BTC-USD_1d_20230101T000000|2023-03-15T08:00:00+00:00"


def test_override_key_missing_fields_does_not_raise():
    key = _override_key({})
    assert key == "|"


# ---------------------------------------------------------------------------
# Anchor override: round-trip save / load
# ---------------------------------------------------------------------------


def _make_override(fib_id: str, event_time: str) -> dict:
    return {
        "fib_id": fib_id,
        "event_time": event_time,
        "based_on_fib_id": fib_id,
        "source": "review_tool_correction",
        "corrected_by": "human",
        "corrected_at": "2026-06-09T12:00:00+00:00",
        "high_anchor": {"time": "2023-11-15T00:00:00+00:00", "price": 37500.0},
    }


def test_save_and_load_overrides_round_trip(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    fib_id = "fib_BTC-USD_1d_20231101T000000"
    event_time = "2023-11-15T08:00:00+00:00"
    override = _make_override(fib_id, event_time)
    overrides = {f"{fib_id}|{event_time}": override}

    _save_anchor_overrides(overrides, run_dir)
    loaded = _load_anchor_overrides(run_dir)

    key = f"{fib_id}|{event_time}"
    assert key in loaded
    assert loaded[key]["high_anchor"]["price"] == pytest.approx(37500.0)
    assert loaded[key]["source"] == "review_tool_correction"


def test_save_multiple_overrides(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    o1 = _make_override("fib_BTC-USD_1d_20230101T000000", "2023-03-01T00:00:00+00:00")
    o2 = _make_override("fib_BTC-USD_1d_20230601T000000", "2023-08-01T00:00:00+00:00")
    o2["low_anchor"] = {"time": "2023-08-05T00:00:00+00:00", "price": 28000.0}
    overrides = {
        _override_key(o1): o1,
        _override_key(o2): o2,
    }

    _save_anchor_overrides(overrides, run_dir)
    loaded = _load_anchor_overrides(run_dir)

    assert len(loaded) == 2
    assert loaded[_override_key(o2)]["low_anchor"]["price"] == pytest.approx(28000.0)


def test_load_returns_empty_when_file_missing(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    result = _load_anchor_overrides(run_dir)
    assert result == {}


# ---------------------------------------------------------------------------
# Data safety: original fib file must not be modified
# ---------------------------------------------------------------------------


def test_save_does_not_touch_original_fib_file(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    fib_file = tmp_path / "fib_BTC-USD_1d_20230101T000000.json"
    original_content = '{"fib_id": "fib_BTC-USD_1d_20230101T000000", "anchor_a": {"price": 30000}}'
    fib_file.write_text(original_content, encoding="utf-8")

    override = _make_override("fib_BTC-USD_1d_20230101T000000", "2023-03-01T00:00:00+00:00")
    _save_anchor_overrides({_override_key(override): override}, run_dir)

    assert fib_file.read_text(encoding="utf-8") == original_content


def test_overrides_file_separate_from_sample_jsonl(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    sample = run_dir / "review_sample.jsonl"
    sample.write_text(
        '{"fib_id": "x", "event_time": "2023-01-01T00:00:00+00:00"}\n', encoding="utf-8"
    )

    override = _make_override("x", "2023-01-01T00:00:00+00:00")
    _save_anchor_overrides({_override_key(override): override}, run_dir)

    # review_sample.jsonl must be unchanged
    assert sample.read_text(encoding="utf-8").startswith('{"fib_id": "x"')
    # overrides go to the separate file
    assert (run_dir / "review_anchor_overrides.jsonl").exists()


def test_load_skips_malformed_lines(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    path = run_dir / "review_anchor_overrides.jsonl"
    path.write_text(
        '{"fib_id": "a", "event_time": "2023-01-01T00:00:00+00:00"}\n'
        "not valid json\n"
        '{"fib_id": "b", "event_time": "2023-02-01T00:00:00+00:00"}\n',
        encoding="utf-8",
    )
    loaded = _load_anchor_overrides(run_dir)
    assert len(loaded) == 2

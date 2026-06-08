"""Tests for the fib fingerprint × outcome triage top-list export."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from fibengine.research.fib_toplist import (
    build_candidate_toplist,
    compare_runs,
    fingerprint_hints,
    run_compare,
    run_toplist,
    sample_inventory,
    spearman,
    triage_fields,
)


def _event(idx: int, candidate: str, relation: str, level: str) -> dict:
    return {
        "event_id": f"{candidate}-{relation}-{level}-{idx}",
        "auto_candidate": candidate,
        "relation": relation,
        "fib_level": level,
        "timeframe": "1d",
        "direction_inferred": True,
        "pre_bars_approaching_level": 10,
        "pre_distance_atr_norm": float(idx),  # monotonic vs mfe below
        "pre_approach_choppiness": 5.0,  # constant -> no covariation
        "at_wick_through_level": 100.0,
        "at_close_distance_atr_norm": 0.1,
        "post_bars_on_break_side": float(idx),
        "post_retest_count": 2,
        "post_remained_near_level_rate": 0.1,
    }


def _rows(events: list[dict], horizons: list[int]) -> list[dict]:
    rows: list[dict] = []
    for idx, ev in enumerate(events):
        for h in horizons:
            row = dict(ev)
            row["horizon"] = h
            row["mfe"] = round(0.01 * idx, 6)  # increases with idx (and pre_distance)
            row["mae"] = round(0.02 - 0.001 * idx, 6)  # decreases with idx
            row["forward_return"] = -0.01
            row["close_on_approach_side"] = idx % 2 == 0
            row["crossed_back"] = idx % 2 == 1
            rows.append(row)
    return rows


def test_spearman_monotonic_inverse_and_constant():
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == 1.0
    assert spearman([1, 2, 3, 4], [40, 30, 20, 10]) == -1.0
    assert spearman([1, 1, 1, 1], [1, 2, 3, 4]) is None  # zero variance
    assert spearman([1, 2], [1, 2]) is None  # < 3 pairs


def test_build_candidate_toplist_ranks_and_flags_low_sample():
    big = [_event(i, "continuation_candidate", "touch", "0.5") for i in range(5)]
    small = [_event(i, "rejection_candidate", "touch", "0.382") for i in range(2)]
    joined = _rows(big, [5, 10]) + _rows(small, [5, 10])

    toplist = build_candidate_toplist(joined)

    # 2 candidates × 1 bucket each × 2 horizons = 4 bucket rows
    assert len(toplist) == 4
    cont = [r for r in toplist if r["auto_candidate"] == "continuation_candidate"]
    rej = [r for r in toplist if r["auto_candidate"] == "rejection_candidate"]
    assert all(r["n_events"] == 5 and r["sample_flag"] == "ok" for r in cont)
    assert all(r["n_events"] == 2 and r["sample_flag"] == "LOW SAMPLE" for r in rej)
    # single bucket per (candidate, horizon) -> rank 1
    assert all(r["rank_in_candidate_horizon"] == 1 for r in toplist)


def test_fingerprint_hints_and_triage_detect_monotonic_field():
    events = [_event(i, "continuation_candidate", "touch", "0.5") for i in range(6)]
    joined = _rows(events, [5, 10])

    hints = fingerprint_hints(joined)
    assert hints["horizons"] == [5, 10]
    # pre_distance_atr_norm is monotonic with mfe -> rho 1.0; with mae -> -1.0
    rho = hints["per_field"]["pre_distance_atr_norm"]
    assert rho["rho_mfe"][5] == 1.0
    assert rho["rho_mae"][5] == -1.0
    # constant field -> no covariation
    assert hints["per_field"]["pre_approach_choppiness"]["rho_mfe"][5] is None

    triage = triage_fields(hints)
    assert "pre_distance_atr_norm" in triage["watch"]
    assert "pre_approach_choppiness" in triage["noise"]


def test_run_toplist_writes_csv_and_notes(tmp_path):
    big = [_event(i, "continuation_candidate", "touch", "0.5") for i in range(5)]
    small = [_event(i, "rejection_candidate", "touch", "0.382") for i in range(2)]
    joined = _rows(big, [5, 10]) + _rows(small, [5, 10])

    run_dir = tmp_path / "fp_outcomes_test"
    run_dir.mkdir()
    with (run_dir / "fingerprint_outcomes.jsonl").open("w", encoding="utf-8") as f:
        for row in joined:
            f.write(json.dumps(row, sort_keys=True) + "\n")

    result = run_toplist(run_dir)

    csv_path = Path(result["toplist_csv"])
    md_path = Path(result["notes_md"])
    assert csv_path.exists()
    assert md_path.exists()
    assert result["low_sample_buckets"] == 2  # rejection bucket at both horizons

    with csv_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 4
    assert {"LOW SAMPLE", "ok"} == {r["sample_flag"] for r in rows}

    notes = md_path.read_text(encoding="utf-8")
    assert "LOW-SAMPLE" in notes
    assert "Spearman" in notes


def _write_run(run_dir: Path, joined: list[dict]) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    with (run_dir / "fingerprint_outcomes.jsonl").open("w", encoding="utf-8") as f:
        for row in joined:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def test_sample_inventory_counts_thresholds():
    big = [_event(i, "continuation_candidate", "touch", "0.5") for i in range(10)]
    toplist = build_candidate_toplist(_rows(big, [5]))
    inv = sample_inventory(toplist)
    assert inv["total_buckets"] == 1
    assert inv["buckets_n_ge_5"] == 1
    assert inv["buckets_n_ge_10"] == 1
    assert inv["buckets_n_ge_20"] == 0
    assert inv["low_sample_buckets"] == 0


def test_compare_runs_inventory_and_newly_reached(tmp_path):
    base_events = [_event(i, "continuation_candidate", "touch", "0.5") for i in range(2)]
    exp_events = [_event(i, "continuation_candidate", "touch", "0.5") for i in range(8)]
    base_dir = tmp_path / "baseline"
    exp_dir = tmp_path / "expanded"
    _write_run(base_dir, _rows(base_events, [5, 10]))
    _write_run(exp_dir, _rows(exp_events, [5, 10]))

    cmp = compare_runs(base_dir, exp_dir)
    assert cmp["baseline"]["inventory"]["buckets_n_ge_5"] == 0
    assert cmp["expanded"]["inventory"]["buckets_n_ge_5"] == 2  # both horizons
    assert cmp["newly_reached_5"] == 2
    assert cmp["still_low_sample"] == 0
    # bucket rows carry baseline + expanded counts
    row = cmp["bucket_rows"][0]
    assert row["n_baseline"] == 2
    assert row["n_expanded"] == 8
    assert row["delta"] == 6


def test_run_compare_writes_multirun_artifacts(tmp_path):
    base_events = [_event(i, "continuation_candidate", "touch", "0.5") for i in range(2)]
    exp_events = [_event(i, "continuation_candidate", "touch", "0.5") for i in range(8)]
    base_dir = tmp_path / "baseline"
    exp_dir = tmp_path / "expanded"
    _write_run(base_dir, _rows(base_events, [5, 10]))
    _write_run(exp_dir, _rows(exp_events, [5, 10]))

    result = run_compare(base_dir, exp_dir)
    inv_csv = Path(result["sample_inventory_csv"])
    notes_md = Path(result["multirun_notes_md"])
    assert inv_csv.exists()
    assert notes_md.exists()
    assert result["newly_reached_5"] == 2

    with inv_csv.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert {"n_baseline", "n_expanded", "delta", "reached_5"} <= set(rows[0].keys())

    notes = notes_md.read_text(encoding="utf-8")
    assert "Sample-size inventory" in notes
    assert "Fingerprint stability" in notes

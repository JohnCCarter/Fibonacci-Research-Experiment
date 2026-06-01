import json

from fibengine.research.level_event_review_tool import _load_rows


def test_load_rows_from_jsonl(tmp_path):
    run_dir = tmp_path / "review_run"
    run_dir.mkdir()
    row = {"review_id": "x", "human_label": "", "auto_candidate": "rejection_candidate"}
    (run_dir / "review_sample.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    loaded = _load_rows(run_dir)
    assert len(loaded) == 1
    assert loaded[0]["review_id"] == "x"

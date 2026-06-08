import json
from pathlib import Path

from fibengine.research.ledger_query import run_sql_file


def test_run_sql_file_counts_jsonl_rows(tmp_path: Path):
    jsonl = tmp_path / "ledger.jsonl"
    rows = [{"a": 1}, {"a": 2}, {"a": 3}]
    jsonl.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")

    sql = tmp_path / "count.sql"
    sql.write_text(
        "SELECT COUNT(*) AS row_count FROM read_json_auto($jsonl_path);",
        encoding="utf-8",
    )
    df = run_sql_file(sql, {"jsonl_path": str(jsonl)})
    assert int(df.iloc[0]["row_count"]) == 3

"""Run DuckDB SQL files against JSONL experiment ledgers."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import duckdb
import pandas as pd

from fibengine.core.config import REPO_ROOT

_PARAM_RE = re.compile(r"\$(\w+)")


def run_sql_file(path: Path, params: dict | None = None) -> pd.DataFrame:
    """Execute a ``.sql`` file with optional ``:name`` parameter substitution."""
    sql = path.read_text(encoding="utf-8")
    params = params or {}
    for name in _PARAM_RE.findall(sql):
        if name not in params:
            raise ValueError(f"Missing SQL parameter :{name}")
    con = duckdb.connect()
    try:
        return con.execute(sql, params).df()
    finally:
        con.close()


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run DuckDB SQL against JSONL ledgers.")
    p.add_argument("--sql", type=Path, required=True, help="Path to .sql file.")
    p.add_argument(
        "--jsonl",
        type=Path,
        default=REPO_ROOT / "experiments" / "results" / "mtf_fib_level_projection.jsonl",
        help="JSONL path for :jsonl_path parameter.",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    sql_path = args.sql if args.sql.is_absolute() else REPO_ROOT / args.sql
    jsonl = args.jsonl if args.jsonl.is_absolute() else REPO_ROOT / args.jsonl
    df = run_sql_file(sql_path, {"jsonl_path": str(jsonl)})
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()

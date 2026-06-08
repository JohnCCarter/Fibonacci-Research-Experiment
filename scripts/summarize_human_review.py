#!/usr/bin/env python3
"""Summarize a completed human_review_level_events package (Hypothesis A)."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def _load_rows(run_dir: Path) -> list[dict]:
    jsonl = run_dir / "review_sample.jsonl"
    csv_path = run_dir / "review_sample.csv"
    if jsonl.exists():
        return [
            json.loads(line)
            for line in jsonl.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    if csv_path.exists():
        import csv

        with csv_path.open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))
    raise FileNotFoundError(f"Need {jsonl} or {csv_path}")


def summarize(run_dir: Path) -> dict:
    rows = _load_rows(run_dir)
    labels = Counter(r.get("human_label") or "(empty)" for r in rows)
    confidence = Counter(r.get("human_confidence") or "(empty)" for r in rows)
    by_candidate: dict[str, Counter] = {}
    for r in rows:
        key = r.get("auto_candidate", "?")
        by_candidate.setdefault(key, Counter())[r.get("human_label") or "(empty)"] += 1

    n = len(rows)
    n_labeled = sum(1 for r in rows if (r.get("human_label") or "").strip())
    agree = sum(1 for r in rows if r.get("human_label") == "agree")
    return {
        "run_dir": str(run_dir),
        "n_events": n,
        "n_labeled": n_labeled,
        "agree_rate": round(agree / n_labeled, 4) if n_labeled else None,
        "human_label_counts": dict(labels),
        "human_confidence_counts": dict(confidence),
        "by_auto_candidate": {k: dict(v) for k, v in by_candidate.items()},
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Summarize human review JSONL in a review run folder.")
    p.add_argument(
        "run_dir",
        type=Path,
        help="e.g. experiments/review/fib_level_events/review_20260601T152524Z",
    )
    args = p.parse_args()
    out = summarize(args.run_dir.resolve())
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()

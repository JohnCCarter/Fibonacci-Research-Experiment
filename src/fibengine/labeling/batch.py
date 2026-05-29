"""Create lightweight label-review checkpoints for reproducible tuning.

Run:
    uv run python -m fibengine.labeling.batch
    uv run python -m fibengine.labeling.batch --batch-id 2026-05-28_round4 --note "UX"
    uv run python -m fibengine.labeling.batch --copy-labels  # full archived copy
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from shutil import copy2

from fibengine.core.config import REPO_ROOT, load_settings
from fibengine.labeling.store import LABELS_DIR, iter_label_files

REVIEW_ROOT = REPO_ROOT / "experiments" / "label_review"
BATCHES_DIR = REVIEW_ROOT / "batches"
PIVOT_RECALL_JSONL = REPO_ROOT / "experiments" / "results" / "pivot_recall.jsonl"
LEADERBOARD_JSONL = REPO_ROOT / "experiments" / "results" / "leaderboard.jsonl"


def _default_batch_id() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d_label_batch_%H%M%S")


def _safe_batch_id(value: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
    cleaned = "".join(ch if ch in allowed else "-" for ch in value.strip())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-._") or _default_batch_id()


def _last_jsonl_row(path: Path) -> dict | None:
    if not path.exists():
        return None
    lines = [line.strip() for line in path.read_text().splitlines() if line.strip()]
    if not lines:
        return None
    return json.loads(lines[-1])


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _label_manifest(label_files: list[Path]) -> list[dict]:
    manifest = []
    for file in label_files:
        rel = file.relative_to(LABELS_DIR)
        manifest.append(
            {
                "file": str(rel).replace("\\", "/"),
                "path": str(file.relative_to(REPO_ROOT)).replace("\\", "/"),
                "sha256": _file_sha256(file),
                "size_bytes": file.stat().st_size,
            }
        )
    return manifest


def create_label_batch(
    batch_id: str | None = None,
    note: str | None = None,
    copy_labels: bool = False,
) -> Path:
    settings = load_settings()
    resolved_batch = _safe_batch_id(batch_id or _default_batch_id())
    out_dir = BATCHES_DIR / resolved_batch
    out_dir.mkdir(parents=True, exist_ok=False)

    label_files = iter_label_files()
    manifest = _label_manifest(label_files)
    manifest_path = out_dir / "labels_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))

    snapshot_dir = None
    if copy_labels:
        snapshot_dir = out_dir / "labels_snapshot"
        snapshot_dir.mkdir()
        for file in label_files:
            dest = snapshot_dir / file.relative_to(LABELS_DIR)
            dest.parent.mkdir(parents=True, exist_ok=True)
            copy2(file, dest)

    latest_pivot = _last_jsonl_row(PIVOT_RECALL_JSONL)
    latest_leaderboard = _last_jsonl_row(LEADERBOARD_JSONL)
    payload = {
        "batch_id": resolved_batch,
        "created_at": datetime.now(UTC).isoformat(),
        "note": note or "",
        "config_hash": settings.config_hash(),
        "label_count": len(label_files),
        "labels_source_dir": str(LABELS_DIR),
        "labels_manifest": str(manifest_path),
        "labels_snapshot_dir": str(snapshot_dir) if snapshot_dir else None,
        "labels_copied": copy_labels,
        "latest_pivot_recall": latest_pivot,
        "latest_leaderboard_row": latest_leaderboard,
    }
    (out_dir / "metadata.json").write_text(json.dumps(payload, indent=2))

    notes = [
        f"# Label Batch {resolved_batch}",
        "",
        f"- Created: {payload['created_at']}",
        f"- Labels tracked: {payload['label_count']}",
        f"- Labels copied: {payload['labels_copied']}",
        f"- Config hash: `{payload['config_hash']}`",
        "- Manifest: `labels_manifest.json`",
    ]
    if note:
        notes.extend(["", "## Note", note])
    notes.extend(
        [
            "",
            "## Next Step",
            "Run pivot_recall and experiment against this batch:",
            "`uv run python -m fibengine.evaluation.pivot_recall`",
            "`uv run python -m fibengine.experiment`",
            "to compare this batch against previous batches.",
        ]
    )
    (out_dir / "notes.md").write_text("\n".join(notes) + "\n")
    return out_dir


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a versioned label-review batch.")
    parser.add_argument("--batch-id", help="Custom batch id/folder name.")
    parser.add_argument("--note", help="Optional note describing this labeling round.")
    parser.add_argument(
        "--copy-labels",
        action="store_true",
        help="Also copy label JSON files into labels_snapshot/. Default is manifest-only.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    path = create_label_batch(
        batch_id=args.batch_id,
        note=args.note,
        copy_labels=args.copy_labels,
    )
    print(path)

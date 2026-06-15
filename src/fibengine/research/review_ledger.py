"""Source-quality review ledger — stdlib-only, lightweight, no database.

A flat CSV that makes source-fib **review verdicts** machine-trackable instead of living
only in prose review docs. One row per (fib, review pass): verdict, status, a note, the
source-fib path, the (gitignored) artifact path, and a deterministic ``source_hash`` of
the committed fib JSON so a verdict is tied to the exact facit version it was based on.

This is **review metadata only**: it never edits source labels, never renders artifacts,
never touches reaction-review / auto-fib. The CSV is a committed text record under
``docs/research_wiki/reviews/ledgers/`` (not under ``experiments/review/**``).

Controlled vocabulary keeps the ledger queryable:

- ``verdict`` ∈ :data:`VERDICTS` — the review outcome.
- ``status`` ∈ :data:`STATUSES` — the lifecycle state (e.g. a suspicious fib becomes a
  ``correction-candidate``).

Usage::

    # validate an existing ledger
    python -m fibengine.research.review_ledger \\
        --validate docs/research_wiki/reviews/ledgers/btc-4h-source-quality-ledger.csv
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

# Column order of the ledger CSV (also the schema).
LEDGER_FIELDS: tuple[str, ...] = (
    "fib_id",
    "symbol",
    "timeframe",
    "scope",
    "review_type",
    "verdict",
    "status",
    "note",
    "source_fib_path",
    "artifact_path",
    "source_hash",
    "reviewed_at",
    "reviewer",
)

# Review outcome.
VERDICTS: frozenset[str] = frozenset({"ok", "ok-with-note", "watchlist", "suspicious"})
# Lifecycle state of the reviewed fib. ``superseded`` = retired from active facit (e.g. a
# near-duplicate removed in favour of a better fib); its source_fib_path may no longer
# exist on disk — the row is provenance for the dedup decision.
STATUSES: frozenset[str] = frozenset(
    {
        "accepted",
        "noted",
        "open",
        "correction-candidate",
        "deferred",
        "corrected",
        "superseded",
    }
)


def source_hash(path: Path | str) -> str:
    """Deterministic ``"sha256:<16 hex>"`` reference for a source fib JSON file.

    Hashes the raw file bytes, so the same committed fib always yields the same value and
    any edit to the facit changes it. Truncated to 16 hex chars for a readable CSV cell.
    """
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return f"sha256:{digest[:16]}"


@dataclass
class LedgerRow:
    """One review verdict for one fib. Validate before writing/after reading."""

    fib_id: str
    symbol: str
    timeframe: str
    scope: str
    review_type: str
    verdict: str
    status: str
    note: str
    source_fib_path: str
    artifact_path: str
    source_hash: str
    reviewed_at: str
    reviewer: str

    def validate(self) -> LedgerRow:
        """Raise ``ValueError`` on an unknown verdict/status or a missing fib_id."""
        if not self.fib_id:
            raise ValueError("LedgerRow.fib_id must be non-empty")
        if self.verdict not in VERDICTS:
            raise ValueError(
                f"{self.fib_id}: invalid verdict {self.verdict!r}; allowed: {sorted(VERDICTS)}"
            )
        if self.status not in STATUSES:
            raise ValueError(
                f"{self.fib_id}: invalid status {self.status!r}; allowed: {sorted(STATUSES)}"
            )
        return self


def row_for_source_fib(
    source_fib_path: Path | str,
    *,
    scope: str,
    review_type: str,
    verdict: str,
    status: str,
    note: str,
    artifact_path: str = "",
    reviewed_at: str,
    reviewer: str = "human",
) -> LedgerRow:
    """Build a validated row, pulling fib_id/symbol/timeframe + hash from the fib JSON.

    ``source_fib_path`` is read for the hash and identity fields and stored verbatim (pass
    a repo-relative path to keep the ledger portable).
    """
    p = Path(source_fib_path)
    payload = json.loads(p.read_text(encoding="utf-8"))
    return LedgerRow(
        fib_id=payload["fib_id"],
        symbol=payload["symbol"],
        timeframe=payload["timeframe"],
        scope=scope,
        review_type=review_type,
        verdict=verdict,
        status=status,
        note=note,
        source_fib_path=str(source_fib_path).replace("\\", "/"),
        artifact_path=artifact_path,
        source_hash=source_hash(p),
        reviewed_at=reviewed_at,
        reviewer=reviewer,
    ).validate()


def write_ledger(path: Path | str, rows: list[LedgerRow]) -> Path:
    """Write rows to a CSV (validating each first). Returns the path."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row.validate()))
    return out


def read_ledger(path: Path | str) -> list[LedgerRow]:
    """Read + validate a ledger CSV into rows. Raises on unknown columns or bad values."""
    with Path(path).open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or tuple(reader.fieldnames) != LEDGER_FIELDS:
            raise ValueError(f"ledger header {reader.fieldnames} != expected {list(LEDGER_FIELDS)}")
        return [LedgerRow(**row).validate() for row in reader]


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate a source-quality review ledger CSV.")
    p.add_argument("--validate", required=True, help="Path to the ledger CSV to validate")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    ledger_rows = read_ledger(args.validate)
    print(f"ledger OK: {len(ledger_rows)} row(s) validated in {args.validate}")

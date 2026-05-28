"""Läs/skriv manuellt facit (swing high/low) som JSON i data/labels/."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from fibengine.core.config import REPO_ROOT

LABELS_DIR = REPO_ROOT / "data" / "labels"


@dataclass
class Point:
    timestamp: str  # ISO-8601 UTC
    price: float


@dataclass
class SwingLabel:
    exchange: str
    symbol: str
    timeframe: str
    high: Point
    low: Point
    note: str = ""
    created_at: str = ""

    def __post_init__(self):
        if isinstance(self.high, dict):
            self.high = Point(**self.high)
        if isinstance(self.low, dict):
            self.low = Point(**self.low)
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()


def _symbol_dir(symbol: str) -> str:
    return symbol.replace("/", "-")


def label_path(label: SwingLabel) -> Path:
    """Kategoriserad sökväg: data/labels/{exchange}/{symbol}/{timeframe}.json"""
    return (
        LABELS_DIR / label.exchange.lower() / _symbol_dir(label.symbol) / f"{label.timeframe}.json"
    )


def legacy_label_path(label: SwingLabel) -> Path:
    """Platt legacy-format (migration)."""
    return LABELS_DIR / f"{label.exchange}_{_symbol_dir(label.symbol)}_{label.timeframe}.json"


def iter_label_files() -> list[Path]:
    """Alla label-JSON under data/labels/ (rekursivt, exkl. legacy-platta filer på rot)."""
    if not LABELS_DIR.exists():
        return []
    nested = [p for p in LABELS_DIR.rglob("*.json") if p.parent != LABELS_DIR]
    flat = [p for p in LABELS_DIR.glob("*.json")]
    return sorted(set(nested) | set(flat))


def save_label(label: SwingLabel, path: Path | None = None) -> Path:
    path = path or label_path(label)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(label), indent=2))
    legacy = legacy_label_path(label)
    if legacy != path and legacy.exists():
        legacy.unlink()
    return path


def delete_label(label: SwingLabel) -> bool:
    removed = False
    for path in (label_path(label), legacy_label_path(label)):
        if path.exists():
            path.unlink()
            removed = True
    return removed


def find_label(exchange: str, symbol: str, timeframe: str) -> SwingLabel | None:
    placeholder = SwingLabel(
        exchange=exchange,
        symbol=symbol,
        timeframe=timeframe,
        high=Point("", 0.0),
        low=Point("", 0.0),
    )
    for path in (label_path(placeholder), legacy_label_path(placeholder)):
        if path.exists():
            return load_label(path)
    return None


def load_label(path: str | Path) -> SwingLabel:
    data = json.loads(Path(path).read_text())
    return SwingLabel(**data)


def list_labels() -> list[SwingLabel]:
    return [load_label(p) for p in iter_label_files()]

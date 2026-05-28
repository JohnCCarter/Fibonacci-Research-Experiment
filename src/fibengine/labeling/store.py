"""Läs/skriv manuellt facit (swing high/low) som JSON i data/labels/."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from fibengine.config import REPO_ROOT

LABELS_DIR = REPO_ROOT / "data" / "labels"


@dataclass
class Point:
    timestamp: str   # ISO-8601 UTC
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


def label_path(label: SwingLabel) -> Path:
    symbol = label.symbol.replace("/", "-")
    return LABELS_DIR / f"{label.exchange}_{symbol}_{label.timeframe}.json"


def save_label(label: SwingLabel, path: Path | None = None) -> Path:
    path = path or label_path(label)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(label), indent=2))
    return path


def delete_label(label: SwingLabel) -> bool:
    path = label_path(label)
    if not path.exists():
        return False
    path.unlink()
    return True


def find_label(exchange: str, symbol: str, timeframe: str) -> SwingLabel | None:
    placeholder = SwingLabel(
        exchange=exchange,
        symbol=symbol,
        timeframe=timeframe,
        high=Point("", 0.0),
        low=Point("", 0.0),
    )
    path = label_path(placeholder)
    return load_label(path) if path.exists() else None


def load_label(path: str | Path) -> SwingLabel:
    data = json.loads(Path(path).read_text())
    return SwingLabel(**data)


def list_labels() -> list[SwingLabel]:
    if not LABELS_DIR.exists():
        return []
    return [load_label(p) for p in sorted(LABELS_DIR.glob("*.json"))]

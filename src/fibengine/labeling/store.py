"""Läs/skriv manuellt facit (swing high/low) som JSON i data/labels/."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from fibengine.core.config import REPO_ROOT

LABELS_DIR = REPO_ROOT / "data" / "labels"
_LABELS_DIR_OVERRIDE: Path | None = None


def get_labels_dir() -> Path:
    return _LABELS_DIR_OVERRIDE or LABELS_DIR


def set_labels_dir(path: str | Path | None) -> None:
    """Override label read/write root (e.g. data/labels/tmp). None = default."""
    global _LABELS_DIR_OVERRIDE
    if path is None:
        _LABELS_DIR_OVERRIDE = None
        return
    p = Path(path)
    _LABELS_DIR_OVERRIDE = p if p.is_absolute() else REPO_ROOT / p


@dataclass
class Point:
    timestamp: str  # ISO-8601 UTC
    price: float


@dataclass
class LegLabel:
    """One fib leg (high + low) within a symbol/timeframe facit file."""

    high: Point
    low: Point
    id: str = ""
    role: str = ""
    note: str = ""
    same_candle_mtf_resolution: dict | None = None

    def __post_init__(self) -> None:
        if isinstance(self.high, dict):
            self.high = Point(**self.high)
        if isinstance(self.low, dict):
            self.low = Point(**self.low)


@dataclass
class SwingLabel:
    exchange: str
    symbol: str
    timeframe: str
    high: Point
    low: Point
    note: str = ""
    created_at: str = ""
    # "human" = manuellt facit (golden set). "machine" = maskingenererad kandidat
    # (provisorisk, EXKLUDERAS från recall/agreement — får aldrig bli domare).
    source: str = "human"
    # Research (labeling.tool): 1w H+L same bar resolved via 1d pivots. Ignored by motor/eval.
    same_candle_mtf_resolution: dict | None = None
    # Research: multiple daily (or HTF) fib legs in one file. Motor/eval use top-level high/low.
    legs: list[LegLabel] | None = None

    def __post_init__(self) -> None:
        if isinstance(self.high, dict):
            self.high = Point(**self.high)
        if isinstance(self.low, dict):
            self.low = Point(**self.low)
        if self.legs:
            parsed: list[LegLabel] = []
            for i, leg in enumerate(self.legs):
                parsed.append(leg if isinstance(leg, LegLabel) else LegLabel(**leg))
                if not parsed[-1].id:
                    parsed[-1].id = f"leg_{i + 1}"
            self.legs = parsed
        if not self.created_at:
            self.created_at = datetime.now(UTC).isoformat()

    def all_legs(self) -> list[LegLabel]:
        if self.legs:
            return self.legs
        return [
            LegLabel(
                high=self.high,
                low=self.low,
                id="leg_1",
                note=self.note,
                same_candle_mtf_resolution=self.same_candle_mtf_resolution,
            )
        ]


def _leg_payload(leg: LegLabel) -> dict:
    out = asdict(leg)
    if out.get("same_candle_mtf_resolution") is None:
        out.pop("same_candle_mtf_resolution", None)
    if not out.get("role"):
        out.pop("role", None)
    if not out.get("note"):
        out.pop("note", None)
    return out


def _symbol_dir(symbol: str) -> str:
    return symbol.replace("/", "-")


def label_path(label: SwingLabel) -> Path:
    """Kategoriserad sökväg: data/labels/{exchange}/{symbol}/{timeframe}.json"""
    return (
        get_labels_dir()
        / label.exchange.lower()
        / _symbol_dir(label.symbol)
        / f"{label.timeframe}.json"
    )


def legacy_label_path(label: SwingLabel) -> Path:
    """Platt legacy-format (migration)."""
    return get_labels_dir() / f"{label.exchange}_{_symbol_dir(label.symbol)}_{label.timeframe}.json"


def iter_label_files() -> list[Path]:
    """Alla label-JSON under data/labels/ (rekursivt, exkl. legacy-platta filer på rot)."""
    root = get_labels_dir()
    if not root.exists():
        return []
    nested = [p for p in root.rglob("*.json") if p.parent != root and "human_fib" not in p.parts]
    flat = [p for p in root.glob("*.json")]
    return sorted(set(nested) | set(flat))


def save_label(label: SwingLabel, path: Path | None = None) -> Path:
    path = path or label_path(label)
    path.parent.mkdir(parents=True, exist_ok=True)
    legs = label.all_legs()
    if len(legs) > 1:
        payload = {
            "exchange": label.exchange,
            "symbol": label.symbol,
            "timeframe": label.timeframe,
            "high": asdict(legs[0].high),
            "low": asdict(legs[0].low),
            "legs": [_leg_payload(leg) for leg in legs],
            "note": label.note,
            "created_at": label.created_at or datetime.now(UTC).isoformat(),
            "source": label.source,
        }
    else:
        leg = legs[0]
        payload = {
            "exchange": label.exchange,
            "symbol": label.symbol,
            "timeframe": label.timeframe,
            "high": asdict(leg.high),
            "low": asdict(leg.low),
            "note": label.note or leg.note,
            "created_at": label.created_at or datetime.now(UTC).isoformat(),
            "source": label.source,
        }
        if leg.same_candle_mtf_resolution:
            payload["same_candle_mtf_resolution"] = leg.same_candle_mtf_resolution
    if payload.get("note") == "":
        payload.pop("note", None)
    path.write_text(json.dumps(payload, indent=2))
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
    legs_raw = data.get("legs")
    if legs_raw:
        legs = [LegLabel(**leg) for leg in legs_raw]
        return SwingLabel(
            exchange=data["exchange"],
            symbol=data["symbol"],
            timeframe=data["timeframe"],
            high=Point(**data["high"]),
            low=Point(**data["low"]),
            note=data.get("note", ""),
            created_at=data.get("created_at", ""),
            source=data.get("source", "human"),
            same_candle_mtf_resolution=data.get("same_candle_mtf_resolution"),
            legs=legs,
        )
    return SwingLabel(**data)


def list_labels(source: str | None = None) -> list[SwingLabel]:
    """Alla labels, eller bara de med given `source` ("human"/"machine")."""
    labels = [load_label(p) for p in iter_label_files()]
    if source is None:
        return labels
    return [lbl for lbl in labels if lbl.source == source]

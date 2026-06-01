"""Fas 3: fib-level behavior facit (research only — not used by motor/eval).

Facit model (v3+): each fib **level** (grid from leg H/L) has ``events[]`` — daily
interactions over time. ``human_label`` on an event is ground truth; ``auto_candidate``
is suggestion only and must never be copied to ``human_label`` by tooling.

Legacy v1/v2: single ``human_label`` per level is loaded as one event on read.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from fibengine.core.config import REPO_ROOT, load_settings
from fibengine.core.fib import fib_from_prices
from fibengine.data.loader import load_candles
from fibengine.labeling.store import LegLabel, load_label

SCHEMA_VERSION = 3
KIND = "fib_level_behavior_facit"
FACIT_MODEL = "events_per_level"
DEFAULT_LEVELS = ("0.382", "0.5", "0.618", "0.786")
DEFAULT_GOLDEN_LEG_IDS = ("leg_1", "leg_8", "leg_10", "leg_20", "leg_24")

BEHAVIORS = frozenset(
    {
        "reaction",
        "rejection",
        "continuation",
        "failure",
        "not_reached",
        "unknown",
    }
)


def normalize_event_bar(value: str) -> str:
    """Accept YYYY-MM-DD or full ISO; store as ISO day UTC."""
    if not value:
        return ""
    text = value.strip()
    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        return f"{text}T00:00:00+00:00"
    return text


@dataclass
class LevelEvent:
    """One daily interaction at a fib level (research facit)."""

    event_bar: str = ""
    level: str = ""
    price: float | None = None
    human_label: str | None = None
    auto_candidate: str | None = None
    note: str = ""

    @classmethod
    def from_dict(cls, ratio: str, data: dict[str, Any]) -> LevelEvent:
        bar = data.get("event_bar") or data.get("date") or ""
        human = data.get("human_label")
        if human is None:
            human = data.get("label")
        legacy = data.get("behavior")
        if human is None and legacy is not None:
            human = legacy
        price = data.get("price")
        return cls(
            event_bar=normalize_event_bar(str(bar)) if bar else "",
            level=str(data.get("level") or ratio),
            price=float(price) if price is not None else None,
            human_label=human,
            auto_candidate=data.get("auto_candidate"),
            note=data.get("note", "") or "",
        )

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "event_bar": self.event_bar,
            "level": self.level,
        }
        if self.price is not None:
            out["price"] = round(self.price, 2)
        if self.auto_candidate is not None:
            out["auto_candidate"] = self.auto_candidate
        if self.human_label is not None:
            out["human_label"] = self.human_label
        else:
            out["human_label"] = None
        if self.note:
            out["note"] = self.note
        return out

    def has_human_facit(self) -> bool:
        return self.human_label is not None


@dataclass
class LevelBehavior:
    """Fib grid price + timeline of daily events at that ratio."""

    level: str = ""
    price: float | None = None
    events: list[LevelEvent] = field(default_factory=list)
    # Legacy v2 (read-only after load; migrated into events on save)
    auto_candidate: str | None = None
    human_label: str | None = None
    event_bar: str = ""
    note: str = ""
    behavior: str | None = None

    def _ensure_legacy_migrated(self) -> None:
        if self.events:
            return
        human = self.human_label if self.human_label is not None else self.behavior
        if human is None and self.auto_candidate is None and not self.event_bar and not self.note:
            return
        self.events.append(
            LevelEvent(
                event_bar=self.event_bar,
                level=self.level,
                price=self.price,
                human_label=human,
                auto_candidate=self.auto_candidate,
                note=self.note,
            )
        )

    def has_human_facit(self) -> bool:
        self._ensure_legacy_migrated()
        return any(ev.has_human_facit() for ev in self.events)

    def effective_human_label(self) -> str | None:
        """Last event with human_label (legacy helper). Prefer iterating events."""
        self._ensure_legacy_migrated()
        labeled = [ev.human_label for ev in self.events if ev.human_label is not None]
        if labeled:
            return labeled[-1]
        if self.human_label is not None:
            return self.human_label
        return self.behavior

    @classmethod
    def from_dict(cls, ratio: str, data: dict[str, Any] | None) -> LevelBehavior:
        if not data:
            return cls(level=ratio)
        events_raw = data.get("events")
        events: list[LevelEvent] = []
        if events_raw:
            events = [LevelEvent.from_dict(ratio, ev) for ev in events_raw]
        human = data.get("human_label")
        legacy = data.get("behavior")
        if human is None and legacy is not None:
            human = legacy
        lb = cls(
            level=str(data.get("level") or ratio),
            price=float(data["price"]) if data.get("price") is not None else None,
            events=events,
            auto_candidate=data.get("auto_candidate"),
            human_label=human,
            event_bar=data.get("event_bar", "") or "",
            note=data.get("note", "") or "",
            behavior=None,
        )
        if not lb.events:
            lb._ensure_legacy_migrated()
        for ev in lb.events:
            if ev.price is None and lb.price is not None:
                ev.price = lb.price
            if not ev.level:
                ev.level = ratio
        return lb

    def to_dict(self) -> dict[str, Any]:
        self._ensure_legacy_migrated()
        out: dict[str, Any] = {
            "level": self.level or "",
            "events": [ev.to_dict() for ev in self.events],
        }
        if self.price is not None:
            out["price"] = round(self.price, 2)
        return out


@dataclass
class LegBehavior:
    leg_id: str
    leg_direction: str
    included_in_golden_subset: bool = True
    derived_prices: dict[str, float] = field(default_factory=dict)
    levels: dict[str, LevelBehavior] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "leg_id": self.leg_id,
            "leg_direction": self.leg_direction,
            "included_in_golden_subset": self.included_in_golden_subset,
        }
        if self.derived_prices:
            out["derived_prices"] = {k: round(v, 2) for k, v in self.derived_prices.items()}
        if self.levels:
            out["levels"] = {
                ratio: lb.to_dict()
                for ratio, lb in sorted(self.levels.items(), key=lambda x: float(x[0]))
            }
        return out


@dataclass
class BehaviorFacit:
    parent_label_path: str
    exchange: str
    symbol: str
    timeframe: str
    legs: list[LegBehavior]
    schema_version: int = SCHEMA_VERSION
    kind: str = KIND
    source: str = "human"
    created_at: str = ""
    updated_at: str = ""
    annotator: str = ""
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        return {
            "schema_version": self.schema_version,
            "kind": self.kind,
            "facit_model": FACIT_MODEL,
            "weekly_role": "grid",
            "daily_role": "events",
            "parent_label_path": self.parent_label_path,
            "exchange": self.exchange,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "source": self.source,
            "created_at": self.created_at or now,
            "updated_at": now,
            "annotator": self.annotator,
            "notes": self.notes,
            "facit_policy": (
                "Weekly (HTF) leg defines fib grid (derived_prices). "
                "Daily interactions are events[] per level with human_label as facit. "
                "auto_candidate is suggestion only — never copy to human_label in tooling."
            ),
            "legs": [leg.to_dict() for leg in self.legs],
        }


def leg_direction(leg: LegLabel) -> str:
    hi = pd.to_datetime(leg.high.timestamp, utc=True)
    lo = pd.to_datetime(leg.low.timestamp, utc=True)
    return "up" if lo < hi else "down"


def derive_level_prices(
    leg: LegLabel, ratios: tuple[str, ...] = DEFAULT_LEVELS
) -> dict[str, float]:
    direction = leg_direction(leg)
    floats = [float(r) for r in ratios]
    if direction == "up":
        prices = fib_from_prices(leg.low.price, leg.high.price, floats)
    else:
        prices = fib_from_prices(leg.high.price, leg.low.price, floats)
    return {str(r): prices[float(r)] for r in ratios}


def empty_levels(
    leg: LegLabel,
    ratios: tuple[str, ...] = DEFAULT_LEVELS,
) -> dict[str, LevelBehavior]:
    prices = derive_level_prices(leg, ratios)
    return {r: LevelBehavior(level=r, price=prices[r], events=[]) for r in ratios}


def scaffold_leg_behavior(
    leg: LegLabel,
    *,
    golden: bool = True,
    ratios: tuple[str, ...] = DEFAULT_LEVELS,
) -> LegBehavior:
    return LegBehavior(
        leg_id=leg.id,
        leg_direction=leg_direction(leg),
        included_in_golden_subset=golden,
        derived_prices=derive_level_prices(leg, ratios),
        levels=empty_levels(leg, ratios),
    )


def resolve_parent_path(parent_label_path: str) -> Path:
    path = Path(parent_label_path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def scaffold_from_parent(
    parent_path: str | Path,
    *,
    leg_ids: tuple[str, ...] = DEFAULT_GOLDEN_LEG_IDS,
    all_legs: bool = False,
    notes: str = "Fas 3 — add events[] per level (daily interactions at HTF fib grid)",
) -> BehaviorFacit:
    parent = Path(parent_path)
    label = load_label(parent)
    rel_parent = (
        parent.as_posix()
        if parent.is_absolute()
        else str(parent.relative_to(REPO_ROOT)).replace("\\", "/")
    )
    by_id = {leg.id: leg for leg in label.all_legs()}
    if all_legs:
        leg_ids = tuple(leg.id for leg in label.all_legs())
    missing = [lid for lid in leg_ids if lid not in by_id]
    if missing:
        raise ValueError(f"leg_id not in parent label: {missing}")

    legs = [scaffold_leg_behavior(by_id[lid], golden=True) for lid in leg_ids]
    return BehaviorFacit(
        parent_label_path=rel_parent,
        exchange=label.exchange,
        symbol=label.symbol,
        timeframe=label.timeframe,
        legs=legs,
        notes=notes,
    )


def load_behavior_facit(path: str | Path) -> BehaviorFacit:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    legs = []
    for raw in data.get("legs", []):
        levels = {k: LevelBehavior.from_dict(k, v) for k, v in (raw.get("levels") or {}).items()}
        legs.append(
            LegBehavior(
                leg_id=raw["leg_id"],
                leg_direction=raw["leg_direction"],
                included_in_golden_subset=bool(raw.get("included_in_golden_subset", True)),
                derived_prices={k: float(v) for k, v in (raw.get("derived_prices") or {}).items()},
                levels=levels,
            )
        )
    return BehaviorFacit(
        parent_label_path=data["parent_label_path"],
        exchange=data["exchange"],
        symbol=data["symbol"],
        timeframe=data["timeframe"],
        legs=legs,
        schema_version=int(data.get("schema_version", SCHEMA_VERSION)),
        kind=data.get("kind", KIND),
        source=data.get("source", "human"),
        created_at=data.get("created_at", ""),
        updated_at=data.get("updated_at", ""),
        annotator=data.get("annotator", ""),
        notes=data.get("notes", ""),
    )


def save_behavior_facit(facit: BehaviorFacit, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        facit.created_at = facit.created_at or existing.get("created_at", "")
    facit.schema_version = SCHEMA_VERSION
    path.write_text(json.dumps(facit.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path


def _first_auto_slot(level: LevelBehavior, ratio: str) -> LevelEvent:
    """Reuse empty auto-only event or append a new slot."""
    level._ensure_legacy_migrated()
    for ev in level.events:
        if ev.human_label is None and ev.auto_candidate is not None:
            return ev
    ev = LevelEvent(level=ratio, price=level.price)
    level.events.append(ev)
    return ev


def apply_auto_candidates(
    facit: BehaviorFacit,
    candles: pd.DataFrame,
    *,
    overwrite_auto: bool = True,
) -> int:
    """Add/update one heuristic event per level (first touch). Never sets human_label."""
    from fibengine.labeling.behavior_candidates import annotate_leg_levels

    parent = resolve_parent_path(facit.parent_label_path)
    label = load_label(parent)
    by_id = {leg.id: leg for leg in label.all_legs()}
    updated = 0

    for lb in facit.legs:
        parent_leg = by_id.get(lb.leg_id)
        if not parent_leg:
            continue
        candidates = annotate_leg_levels(candles, parent_leg)
        for ratio, cand in candidates.items():
            level = lb.levels.setdefault(
                ratio, LevelBehavior(level=ratio, price=cand.price, events=[])
            )
            level.price = cand.price
            slot = _first_auto_slot(level, ratio)
            if slot.human_label is not None:
                continue
            if not overwrite_auto and slot.auto_candidate is not None:
                continue
            slot.level = ratio
            slot.price = cand.price
            slot.auto_candidate = cand.auto_candidate
            if cand.event_bar:
                slot.event_bar = cand.event_bar
            if cand.note and not slot.note:
                slot.note = cand.note
            updated += 1

    return updated


def annotate_behavior_file(
    path: str | Path,
    *,
    fetch_if_missing: bool = True,
    overwrite_auto: bool = True,
) -> tuple[BehaviorFacit, int]:
    """Load behavior JSON, apply auto candidates, save. human_label is never modified."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No behavior file: {path}. Run scaffold first.")

    facit = load_behavior_facit(path)
    settings = load_settings()
    cfg = settings.data.model_copy(
        update={
            "exchange": facit.exchange,
            "symbol": facit.symbol,
            "timeframe": facit.timeframe,
        }
    )
    candles = load_candles(cfg, fetch_if_missing=fetch_if_missing)
    count = apply_auto_candidates(facit, candles, overwrite_auto=overwrite_auto)
    save_behavior_facit(facit, path)
    return facit, count


def validate_behavior_facit(
    facit: BehaviorFacit,
    parent_path: str | Path | None = None,
    *,
    require_human: bool = True,
) -> list[str]:
    """Validate grid + events. auto_candidate alone is never valid facit."""
    from fibengine.labeling.behavior_candidates import AUTO_CANDIDATES

    issues: list[str] = []
    parent = Path(parent_path) if parent_path else resolve_parent_path(facit.parent_label_path)
    if not parent.exists():
        issues.append(f"parent label missing: {parent}")
        return issues

    label = load_label(parent)
    by_id = {leg.id: leg for leg in label.all_legs()}

    for lb in facit.legs:
        if lb.leg_id not in by_id:
            issues.append(f"{lb.leg_id}: not found in parent")
            continue
        parent_leg = by_id[lb.leg_id]
        expected_dir = leg_direction(parent_leg)
        if lb.leg_direction != expected_dir:
            issues.append(f"{lb.leg_id}: leg_direction {lb.leg_direction!r} != {expected_dir!r}")

        for ratio in DEFAULT_LEVELS:
            if ratio not in lb.levels:
                continue
            level = lb.levels[ratio]
            level._ensure_legacy_migrated()

            if not level.events:
                continue

            for i, ev in enumerate(level.events):
                prefix = f"{lb.leg_id} @ {ratio} event[{i}]"
                if require_human and ev.human_label is None:
                    hint = ""
                    if ev.auto_candidate:
                        hint = f" (auto_candidate={ev.auto_candidate!r} is not facit)"
                    issues.append(f"{prefix}: human_label not set{hint}")
                elif ev.human_label is not None and ev.human_label not in BEHAVIORS:
                    issues.append(f"{prefix}: invalid human_label {ev.human_label!r}")
                if ev.auto_candidate is not None and ev.auto_candidate not in AUTO_CANDIDATES:
                    issues.append(f"{prefix}: invalid auto_candidate {ev.auto_candidate!r}")
                if not ev.event_bar:
                    issues.append(f"{prefix}: event_bar missing")

        if lb.derived_prices:
            expected = derive_level_prices(parent_leg)
            for ratio, price in lb.derived_prices.items():
                exp = expected.get(ratio)
                if exp is not None and abs(price - exp) > 0.02:
                    issues.append(
                        f"{lb.leg_id} derived_prices[{ratio}]: {price} != expected {exp:.2f}"
                    )

    return issues


def default_behavior_path(
    exchange: str,
    symbol: str,
    timeframe: str,
    *,
    research_subdir: str = "",
) -> Path:
    sym = symbol.replace("/", "-")
    research_root = REPO_ROOT / "data" / "labels" / "research"
    if research_subdir:
        research_root = research_root / research_subdir.strip("/\\")
    return research_root / exchange.lower() / sym / f"{timeframe}-behavior.json"

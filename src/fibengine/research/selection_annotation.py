"""Contrastive fib-selection annotation schema (Issue #42 v0 — selection-learning, NOT edge).

The selection campaign has only ever had **accepted** examples (the human facit). This module adds
the missing half: a durable schema for **contrastive** annotations — for one chart window, the
candidate A/B legs the human *accepts*, *rejects*, or marks *ambiguous*, each with a free-text
reason and optional structured tags. That is the un-captured signal the geometric-feature campaign
kept concluding it lacked (`no_pivot_signal_above_prominence`; positive rule non-geometric).

Reuses the human-fib anchor vocabulary (``anchor_a``/``anchor_b``/``direction``) — no new leg
representation. Provenance is explicit: ``created_by: human`` is real judgment (facit-grade for the
accept/reject call); ``created_by: fixture`` is illustrative scaffolding and is NEVER truth
(mirrors the ``*_candidate`` ≠ facit rule).

NO edge / PnL / auto-fib claim. This is a data schema + round-trip only.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

LABELS: tuple[str, ...] = ("accepted", "rejected", "ambiguous")
DIRECTIONS: tuple[str, ...] = ("up", "down")
PROVENANCE: tuple[str, ...] = ("human", "fixture")

# Optional structured tags (Issue #42). Free-text ``reason`` is primary; tags are for later slicing.
OPTIONAL_TAGS: frozenset[str] = frozenset(
    {
        "too_local",
        "wrong_scale",
        "right_A_wrong_B",
        "right_B_wrong_A",
        "not_ready_yet",
        "separate_cascade",
        "same_cascade",
    }
)


@dataclass(frozen=True)
class Anchor:
    """A fib anchor: an ISO-8601 timestamp string and a price. Same shape as human_fib facit."""

    time: str
    price: float

    def __post_init__(self) -> None:
        if self.price <= 0:
            raise ValueError(f"anchor price must be > 0, got {self.price}")


@dataclass(frozen=True)
class Candidate:
    """One candidate A/B leg for a window, with the human's verdict and why.

    ``direction`` must agree with the anchor price ordering (a leg's 0/1 mapping): ``down`` runs
    high→low so ``anchor_a.price > anchor_b.price``; ``up`` runs low→high so ``a < b``. A rejected
    candidate is still a real leg, so this structural check applies to every label.
    """

    id: str
    anchor_a: Anchor
    anchor_b: Anchor
    direction: str
    label: str
    reason: str = ""
    tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.direction not in DIRECTIONS:
            raise ValueError(f"direction must be one of {DIRECTIONS}, got {self.direction!r}")
        if self.label not in LABELS:
            raise ValueError(f"label must be one of {LABELS}, got {self.label!r}")
        if self.anchor_a.price == self.anchor_b.price:
            raise ValueError(f"degenerate candidate {self.id}: equal anchor prices")
        want_down = self.anchor_a.price > self.anchor_b.price
        if (self.direction == "down") != want_down:
            raise ValueError(
                f"candidate {self.id}: direction {self.direction!r} disagrees with price "
                f"ordering ({self.anchor_a.price} -> {self.anchor_b.price})"
            )
        bad = set(self.tags) - OPTIONAL_TAGS
        if bad:
            raise ValueError(f"candidate {self.id}: unknown tags {sorted(bad)}")


@dataclass(frozen=True)
class AnnotationWindow:
    """A chart window and the set of contrastive candidates the human judged within it."""

    symbol: str
    timeframe: str
    exchange: str
    window_start: str
    window_end: str
    regime_label: str
    structure_label: str
    created_by: str
    candidates: tuple[Candidate, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.created_by not in PROVENANCE:
            raise ValueError(f"created_by must be one of {PROVENANCE}, got {self.created_by!r}")
        if not self.candidates:
            raise ValueError("window has no candidates")
        ids = [c.id for c in self.candidates]
        if len(ids) != len(set(ids)):
            raise ValueError(f"duplicate candidate ids in window: {ids}")

    @property
    def accepted_ids(self) -> list[str]:
        return [c.id for c in self.candidates if c.label == "accepted"]

    @property
    def is_human(self) -> bool:
        return self.created_by == "human"


# ------------------------------------------------------------------ (de)serialization


def _candidate_from_dict(d: dict[str, Any]) -> Candidate:
    return Candidate(
        id=str(d["id"]),
        anchor_a=Anchor(str(d["anchor_a"]["time"]), float(d["anchor_a"]["price"])),
        anchor_b=Anchor(str(d["anchor_b"]["time"]), float(d["anchor_b"]["price"])),
        direction=str(d["direction"]),
        label=str(d["label"]),
        reason=str(d.get("reason", "")),
        tags=tuple(d.get("tags", []) or []),
    )


def window_from_dict(d: dict[str, Any]) -> AnnotationWindow:
    return AnnotationWindow(
        symbol=str(d["symbol"]),
        timeframe=str(d["timeframe"]),
        exchange=str(d["exchange"]),
        window_start=str(d["window_start"]),
        window_end=str(d["window_end"]),
        regime_label=str(d.get("regime_label", "")),
        structure_label=str(d.get("structure_label", "")),
        created_by=str(d["created_by"]),
        candidates=tuple(_candidate_from_dict(c) for c in d["candidates"]),
    )


def window_to_dict(window: AnnotationWindow) -> dict[str, Any]:
    out = asdict(window)
    out["candidates"] = [{**asdict(c), "tags": list(c.tags)} for c in window.candidates]
    return out


def load_window(path: str | Path) -> AnnotationWindow:
    """Load and validate one annotation window from YAML."""
    with open(path, encoding="utf-8") as fh:
        return window_from_dict(yaml.safe_load(fh))


def dump_window(window: AnnotationWindow, path: str | Path) -> None:
    """Write an annotation window to YAML (round-trips through ``load_window``)."""
    with open(path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(window_to_dict(window), fh, sort_keys=False, allow_unicode=True)

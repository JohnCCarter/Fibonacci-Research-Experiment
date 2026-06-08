"""Constants and config for human Fibonacci level-event review (research-only)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from fibengine.core.config import REPO_ROOT

REVIEW_ROOT = REPO_ROOT / "experiments" / "review" / "fib_level_events"

HUMAN_LABELS = ["agree", "wrong_type", "missed_context", "noise", "unclear"]
HUMAN_CONFIDENCE = ["high", "medium", "low"]

ReviewViewMode = Literal["fib_context", "event_zoom"]
CANDIDATE_TYPES = [
    "continuation_candidate",
    "rejection_candidate",
    "reaction_candidate",
    "failure_candidate",
]

_LABEL_HELP = {
    "agree": "The auto_candidate type matches what the chart shows.",
    "wrong_type": "There is an event here, but it is a different candidate type.",
    "missed_context": "Technically a touch, but context (trend/structure) makes it misleading.",
    "noise": "Not a meaningful interaction with the level — noise.",
    "unclear": "Cannot tell from the chart / ambiguous.",
}

_CANDIDATE_SHORT = {
    "continuation_candidate": "cont",
    "rejection_candidate": "rej",
    "reaction_candidate": "react",
    "failure_candidate": "fail",
}

REVIEW_COLUMNS = [
    "review_id",
    "symbol",
    "timeframe",
    "exchange",
    "fib_source",
    "fib_id",
    "fib_level",
    "fib_price",
    "fib_levels",
    "event_bar",
    "event_time",
    "relation",
    "auto_candidate",
    "touch_type",
    "approach_side",
    "note",
    "evidence_forward_bars",
    "evidence_closes_beyond",
    "evidence_closes_back",
    "evidence_max_penetration_atr",
    "swing_start_time",
    "swing_end_time",
    "swing_direction",
    "swing_start_bar",
    "swing_end_bar",
    "anchor_a_time",
    "anchor_a_price",
    "anchor_a_bar",
    "anchor_b_time",
    "anchor_b_price",
    "anchor_b_bar",
    "chart_path",
    "human_label",
    "human_confidence",
    "human_note",
]


class HumanReviewConfig(BaseModel):
    """Research-only config för review-paketet."""

    max_events: int = Field(default=40, ge=1)
    max_per_candidate: int | None = Field(default=None, ge=1)
    max_per_level: int | None = Field(default=None, ge=1)
    candidate_types: list[str] = Field(default_factory=list)
    levels: list[str] = Field(default_factory=list)
    seed: int | None = Field(default=None)
    context_before: int = Field(default=25, ge=1)
    context_after: int = Field(default=25, ge=1)
    fib_context_pad_bars: int = Field(default=15, ge=0)
    default_view_mode: ReviewViewMode = Field(default="fib_context")
    candlestick: bool = Field(default=True)

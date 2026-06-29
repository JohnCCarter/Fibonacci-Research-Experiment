"""Leg-agreement ruler — facit-localized scoring of "same A/B leg as the human".

The free facit-checker the selection campaign lacked: in #38 `agreement` floored for both arms
because `compare_label`/`select_swing` are not localized to the facit leg. It scores a candidate leg
against a human facit leg directly — selection-vs-selection: no detector, no target, no leakage.

LOCKED metric (prereg `btc-fib-leg-agreement-ruler-prereg-20260629`, knobs fixed by
selector-independent pre-lock calibration). Both anchors are candle extremes, so a leg is a pair of
**bars**. Compare by role (high to high, low to low), require same direction, decay linearly in bar
distance:

    primary:  leg_agreement = mean(s_high, s_low),  s = max(0, 1 − Δbar / W),  W = 2 absolute bars

`leg_agreement_min` (strict both-endpoints) and `leg_agreement_iou` (bar-span overlap) are
**secondary diagnostics — never the gate**. `auc` is the gate statistic (ceiling-vs-null sep).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

W_LOCKED = 2  # locked tolerance window (bars); see prereg + calibration (median spacing 2.0)


@dataclass(frozen=True)
class Leg:
    """A fib leg as two candle-bar endpoints: the high-price bar and the low-price bar.

    Direction falls out of bar order (the swing origin is the earlier bar): high earlier → ``down``,
    low earlier → ``up``. Endpoints must differ.
    """

    high_bar: int
    low_bar: int

    def __post_init__(self) -> None:
        if self.high_bar == self.low_bar:
            raise ValueError(f"degenerate leg: high_bar == low_bar == {self.high_bar}")

    @property
    def direction(self) -> str:
        return "down" if self.high_bar < self.low_bar else "up"

    @property
    def span_bars(self) -> int:
        return abs(self.high_bar - self.low_bar)


def _endpoint_score(dbar: int, w: float) -> float:
    return max(0.0, 1.0 - dbar / w)


def leg_agreement(facit: Leg, cand: Leg, *, w: float = W_LOCKED) -> float:
    """PRIMARY locked metric: mean endpoint bar-agreement, direction-gated. Returns [0, 1]."""
    if facit.direction != cand.direction:
        return 0.0
    sh = _endpoint_score(abs(facit.high_bar - cand.high_bar), w)
    sl = _endpoint_score(abs(facit.low_bar - cand.low_bar), w)
    return (sh + sl) / 2.0


def leg_agreement_min(facit: Leg, cand: Leg, *, w: float = W_LOCKED) -> float:
    """SECONDARY diagnostic — strict both-endpoints (min). NOT the gate."""
    if facit.direction != cand.direction:
        return 0.0
    sh = _endpoint_score(abs(facit.high_bar - cand.high_bar), w)
    sl = _endpoint_score(abs(facit.low_bar - cand.low_bar), w)
    return min(sh, sl)


def leg_agreement_iou(facit: Leg, cand: Leg) -> float:
    """SECONDARY diagnostic — bar-span IoU, direction-gated. Price-IoU deferred. Not the gate."""
    if facit.direction != cand.direction:
        return 0.0
    fa, fb = sorted((facit.high_bar, facit.low_bar))
    ca, cb = sorted((cand.high_bar, cand.low_bar))
    inter = max(0, min(fb, cb) - max(fa, ca))
    union = max(fb, cb) - min(fa, ca)
    return inter / union if union > 0 else 1.0


def best_match(cand: Leg, facit_legs: list[Leg], *, w: float = W_LOCKED) -> tuple[int, float]:
    """Score a candidate leg against its CLOSEST facit leg in a window (best-match assignment).

    Returns ``(index, score)`` of the best-matching facit leg. No Hungarian solver — each candidate
    is judged against the single facit leg it most resembles.
    """
    if not facit_legs:
        raise ValueError("facit_legs is empty")
    scores = [leg_agreement(f, cand, w=w) for f in facit_legs]
    j = int(max(range(len(scores)), key=scores.__getitem__))
    return j, scores[j]


def auc(pos: np.ndarray | list[float], neg: np.ndarray | list[float]) -> float:
    """Gate statistic — tie-aware AUC = P(pos > neg) + 0.5·P(pos == neg).

    `pos` = coverage-ceiling scores, `neg` = random-null scores. `ruler_usable` requires AUC ≥ 0.90.
    """
    pos = np.asarray(pos, dtype=float)
    neg = np.asarray(neg, dtype=float)
    if len(pos) == 0 or len(neg) == 0:
        raise ValueError("auc needs non-empty pos and neg")
    neg_sorted = np.sort(neg)
    lt = np.searchsorted(neg_sorted, pos, side="left")
    le = np.searchsorted(neg_sorted, pos, side="right")
    return float((lt + 0.5 * (le - lt)).sum() / (len(pos) * len(neg)))

"""Deterministic baseline scorer + selection metrics for the fib-selection learner (Issue #42 v0).

This is the honest floor the campaign already earned: **rank candidates by log-magnitude**
(a prominence-ish structural prior — bigger swings first), score selection match against the
human's ``accepted`` label, and report Top-1 / Top-3 / reject-precision. Any ML ranker (deferred,
gated — see ``selection_ranker_ml``) must beat THIS before it is worth its dependencies, exactly as
``no_pivot_signal_above_prominence`` demanded on the powered cell.

Also provides ``split_by_window`` — the leakage guard. Splits are by whole **window**, never by
candidate row, so no window's candidates straddle train/val (Issue #42 evaluation requirement).

NO edge / PnL claim: "selection match" is agreement with the human's pick, not a trading outcome.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable

from fibengine.research.selection_annotation import AnnotationWindow, Candidate

ScoreFn = Callable[[Candidate], float]


def candidate_magnitude(cand: Candidate) -> float:
    """Log-price magnitude of the leg — the deterministic baseline prior (bigger swing = higher)."""
    return abs(math.log(cand.anchor_a.price) - math.log(cand.anchor_b.price))


def rank_candidates(window: AnnotationWindow, score_fn: ScoreFn = candidate_magnitude) -> list[str]:
    """Candidate ids sorted by score descending. Ties broken by id for determinism."""
    return [c.id for c in sorted(window.candidates, key=lambda c: (-score_fn(c), c.id))]


def top1_match(window: AnnotationWindow, score_fn: ScoreFn = candidate_magnitude) -> bool:
    """Did the top-ranked candidate carry the human's ``accepted`` label?"""
    accepted = set(window.accepted_ids)
    if not accepted:
        return False
    return rank_candidates(window, score_fn)[0] in accepted


def top3_coverage(window: AnnotationWindow, score_fn: ScoreFn = candidate_magnitude) -> bool:
    """Was an ``accepted`` candidate within the top 3 ranked?"""
    accepted = set(window.accepted_ids)
    if not accepted:
        return False
    return bool(accepted & set(rank_candidates(window, score_fn)[:3]))


def reject_precision(window: AnnotationWindow, score_fn: ScoreFn = candidate_magnitude) -> float:
    """Fraction of ``rejected`` candidates ranked strictly below the best accepted candidate.

    Returns ``nan`` when the window has no accepted or no rejected candidate (undefined).
    """
    accepted = [c for c in window.candidates if c.label == "accepted"]
    rejected = [c for c in window.candidates if c.label == "rejected"]
    if not accepted or not rejected:
        return math.nan
    best_acc = max(score_fn(c) for c in accepted)
    below = sum(1 for c in rejected if score_fn(c) < best_acc)
    return below / len(rejected)


def evaluate(
    windows: list[AnnotationWindow], score_fn: ScoreFn = candidate_magnitude
) -> dict[str, float]:
    """Pooled selection metrics over windows that have an accepted candidate."""
    scored = [w for w in windows if w.accepted_ids]
    if not scored:
        return {"n": 0, "top1": math.nan, "top3": math.nan, "reject_precision": math.nan}
    rp = [reject_precision(w, score_fn) for w in scored]
    rp = [x for x in rp if not math.isnan(x)]
    return {
        "n": float(len(scored)),
        "top1": sum(top1_match(w, score_fn) for w in scored) / len(scored),
        "top3": sum(top3_coverage(w, score_fn) for w in scored) / len(scored),
        "reject_precision": (sum(rp) / len(rp)) if rp else math.nan,
    }


def split_by_window(
    windows: list[AnnotationWindow], train_frac: float = 0.7, seed: int = 20260701
) -> tuple[list[AnnotationWindow], list[AnnotationWindow]]:
    """Leakage-safe split: whole windows to train or val, never individual candidate rows.

    Deterministic given ``seed``. Every window ends up wholly in exactly one side, so no window's
    candidates leak across the split (the guard the ML ranker will rely on).
    """
    if not 0.0 < train_frac < 1.0:
        raise ValueError(f"train_frac must be in (0, 1), got {train_frac}")
    idx = list(range(len(windows)))
    random.Random(seed).shuffle(idx)
    cut = round(len(windows) * train_frac)
    train_idx = set(idx[:cut])
    train = [windows[i] for i in range(len(windows)) if i in train_idx]
    val = [windows[i] for i in range(len(windows)) if i not in train_idx]
    return train, val

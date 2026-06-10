from __future__ import annotations

from collections import Counter

from fibengine.research.human_review_level_events import (
    HumanReviewConfig,
    sample_candidates,
)


def test_sampling_balances_across_candidate_types():
    rows = []
    plan = {
        "continuation_candidate": 20,
        "rejection_candidate": 10,
        "reaction_candidate": 4,
        "failure_candidate": 2,
    }
    for ctype, count in plan.items():
        for i in range(count):
            rows.append(
                {
                    "review_id": f"{ctype}_{i:03d}",
                    "auto_candidate": ctype,
                    "fib_level": ["0.382", "0.5", "0.618"][i % 3],
                }
            )

    sampled = sample_candidates(rows, HumanReviewConfig(max_events=16, seed=11))
    counts = Counter(r["auto_candidate"] for r in sampled)

    assert len(sampled) == 16
    assert counts["failure_candidate"] == 2
    assert counts["reaction_candidate"] == 4
    assert counts["continuation_candidate"] == 5
    assert counts["rejection_candidate"] == 5
    assert counts["continuation_candidate"] < 20


def _rows_by_level(plan: dict[str, int]) -> list[dict]:
    rows = []
    for level, count in plan.items():
        for i in range(count):
            lvl = level.replace(".", "p")
            rows.append(
                {
                    "review_id": f"L{lvl}_{i:03d}",
                    "auto_candidate": "continuation_candidate",
                    "fib_level": level,
                }
            )
    return rows


def test_levels_sampled_equally_no_golden_bias():
    # Equal pool per level → equal sampling. No golden-zone / primary-level bias
    # (Addendum 2): 0.5 and 0.618 are not favored over 0.382 / 0.786.
    rows = _rows_by_level({"0.5": 10, "0.618": 10, "0.382": 10, "0.786": 10})
    sampled = sample_candidates(rows, HumanReviewConfig(max_events=20, seed=7))

    by_level = Counter(r["fib_level"] for r in sampled)
    assert len(sampled) == 20
    # Round-robin across the four levels pulls evenly — no level dominates.
    assert set(by_level) == {"0.382", "0.5", "0.618", "0.786"}
    assert max(by_level.values()) - min(by_level.values()) <= 1


def test_explicit_level_filter_still_works():
    rows = _rows_by_level({"0.5": 10, "0.618": 10, "0.382": 10})
    cfg = HumanReviewConfig(max_events=20, seed=7, levels=["0.382"])
    sampled = sample_candidates(rows, cfg)

    assert sampled, "explicit --level filter must still return its rows"
    assert all(r["fib_level"] == "0.382" for r in sampled)

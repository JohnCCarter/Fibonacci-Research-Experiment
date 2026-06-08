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

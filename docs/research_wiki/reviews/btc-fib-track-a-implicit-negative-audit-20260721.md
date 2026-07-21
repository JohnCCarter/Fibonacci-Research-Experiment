# Audit — Track-A implicit negatives (coverage exposure of the Stage-2 negative labels)

**Date:** 2026-07-21 (autonomous session, owner blanket GO) · **Type:** descriptive audit — **no
verdict family, no AP recompute, nothing here is a study result or may be cited as one.** The
open audit item "negative-audit of track-A implicit negatives" (2026-07-20 systematic audit,
"needs owner" — GO given). Method frozen in the harness docstring before any number was
computed: [`scratchpad/negative_audit_track_a.py`](../../../scratchpad/negative_audit_track_a.py);
summary JSON gitignored/regenerable (`experiments/review/negative_audit/`).

## Question

Stage-2 selection-learning labels every candidate leg that fails the ε-match against facit as a
**negative**. How exposed is that labeling to *unlabeled-positive contamination* — negatives that
mean "the human never reviewed this region" rather than "the human saw it and did not select it"?

## Method (short)

Full-frame pivot universe (baseline `PivotConfig`, disclosed proxy — no per-endpoint truncated
re-detect; fine for coverage geometry, not for study metrics), each pivot paired with its ≤ 12
prior opposite pivots; ε-match exactly as `_matches_human` (3 bars, 0.5×ATR(14), direction).
Frozen a-priori definitions: **near-miss** = matches at 2× both tolerances but not 1×;
**coverage-weak** = nearest facit `anchor_b` further than the median inter-facit gap.
Data: frozen 2026-07-21 cache; corpus 484 (manifest-verified world).

## Findings (Observed)

| Metric | 4h (primary) | 1d (context) |
|---|---|---|
| Candidates (proxy universe) | 87 528 | 13 788 |
| Proxy-positives / negatives | 404 / 87 124 | 79 / 13 709 |
| Near-miss (1×–2× ε shell), share of negatives | 467 = **0.54 %** | 77 = **0.56 %** |
| Median inter-facit-b gap | 13 bars (~2.2 d) | 20 bars |
| Negative→nearest-facit-b distance p25/p50/p75/p90 | 14 / **47** / 114 / 214 bars | 7 / 20 / 44 / 77 bars |
| **Coverage-weak share of negatives** | **75.3 %** | **48.6 %** |

Facit-endpoint density is strongly era-skewed (4h per year): 2017 = **115** of 371 (31 %),
2018 = 34, 2019 = 26, 2020 = 31, 2021 = 55, 2022 = 24, 2023 = **17**, 2024 = 24, 2025 = 35,
2026 = 10. Top facit deserts (zero endpoints): **2018-02-23 → 2018-11-25 (1 652 bars ≈ 9
months)**, 2023-03→06 (588), 2026-03→06 (570), 2022-06→09 (548), 2019-12→2020-03 (511).

## Reading (Inferred, modest — binding when citing this)

1. **The ε band is not the problem.** Only ~0.5 % of negatives sit in the 1×–2× near-miss shell —
   borderline-positive leakage through the tolerance is negligible.
2. **The deserts are the problem.** Three quarters of 4h negatives lie outside the region the
   facit plausibly "reviewed". For those rows, label=0 encodes *absence of attention*, not
   *rejection*. The Stage-2 AP denominator is dominated by evidentially weak negatives.
3. **Consequence for the known numbers (re-framing, not revision):** the "low absolute AP
   (0.057 vs 0.83 ceiling)" headline is measured against a negative set that is ~75 %
   coverage-weak. The internal comparisons (baseline families, controls, nulls) stay valid —
   both sides saw the same negatives — but the *absolute* reproduction gap is partly a
   coverage artifact of the passive corpus. Do **not** re-run Stage-2 with filtered negatives
   without a fresh prereg (that is exactly the post-hoc trap).
4. **Track B is the cure, and this quantifies why:** contrastive capture (#42) creates
   *explicit* negatives (seen-and-rejected inside a reviewed window). This audit says those
   explicit negatives are ~200× rarer than implicit ones today (0 vs 87k) and carry the
   information the implicit set structurally lacks. Priority of resuming capture is *raised*.
5. 1d shows the same pattern at half strength (49 % coverage-weak).

## Non-claims

No study verdict is changed; no model, no edge/behaviour claim; facit untouched. The proxy
universe differs from the causal Stage-2 universe (disclosed above); all numbers are
coverage geometry, not performance metrics.

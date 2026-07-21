# Results — Sequential-conditioning selection feature (`chained_origin`)

**Date run:** 2026-07-21 (autonomous session, owner blanket GO) · **Prereg (locked incl. §9
A1–A7 after two-pass leakage review):**
[prereg](btc-fib-sequential-feature-prereg-20260721.md) · **Status:** **SIGNED OFF by owner
2026-07-21** (mobile session). Executed verbatim: seed 20260721, B=2000, LOCKED band, fail-closed manifest
check (484), frozen 2026-07-21 cache (4h 21 273 bars). Runtime ~35 min. **Multiplicity
disclosure (§9 A5): third sequential-axis test on the same 484-fib snapshot** (after the signed
cascade probe and the chain-clustering null). **Teacher-forcing frame (§2/§9 A2) binds every
number below**: reproduction conditional on the human's own prior (hindsight-drawn) fibs —
never a live-availability, edge, or behaviour claim.

## Verdict (primary cell, 4h k=3)

**`no_sequential_feature_signal`** — adding `chained_origin` to the Stage-2 base model does
NOT improve OOS reproduction of human selection:

| Cell | Cands | Test / pos | AP base | AP +chained | Lift | CI95 | p(lift≤0) | Verdict |
|------|-------|-----------|---------|-------------|------|------|-----------|---------|
| **4h** | 87 324 | 25 188 / 68 | **0.0710** | **0.0532** | **−0.018** | **[−0.082, +0.045]** | 0.70 | **`no_sequential_feature_signal`** |
| 1d (context) | 13 764 | 4 176 / 11 | 0.1186 | 0.0564 | −0.062 | [−0.175, −0.000] | 1.00 | `context_only` |

Bookkeeping (per §9): degenerate misclick legs excluded 6 (4h) + 1 (1d) → 365/75 legs used;
predecessor-rule (A1 self-leg guard) changed the nearest predecessor for only 274/87 324
candidates (0.3 %); `chain_prox` variant AP 0.0573 (also below base); inference on 2 099
decision-point clusters, 2000/2000 effective.

## The honest tension in the data (descriptive, never verdict-bearing)

- **The univariate signal EXISTS**: chained-rate among test positives **17.6 %** vs **3.8 %**
  among test negatives (≈ 4.7×) — the candidate-level echo of the signed leg-level cascade
  (0.256). The feature's standardized weight is positive (+0.11); AUC even ticks up
  (0.916 → 0.922).
- **But it does not convert to AP**: early-precision *falls* when the feature is added. The
  base features (cleanliness/prominence/magnitude…) already rank chained candidates highly —
  the feature's information overlaps rather than adds, and at 68 test positives the extra
  parameter costs more than it buys.
- 1d context is starker: **0 of 11** test positives chain, and the feature actively hurts
  (CI excludes 0 from above there — would read `sequential_feature_worse` were it
  verdict-bearing; it is not, per §3).

## Where this leaves the sequential axis (Inferred, modest — binding when citing)

Three locked results now bound the axis on this corpus: **(1)** origins chain far above chance
(signed cascade, 0.256 vs 0.005); **(2)** chaining is not serially clustered
(`no_chain_clustering`, hub-guarded); **(3)** chaining adds no incremental teacher-forced
ranking signal over the geometric features (`no_sequential_feature_signal`, this study).
Consistent reading: **sequential chaining is a byproduct of how the human selects (zigzag
drawing rhythm), not an independent driver the model was missing** — "a component, not the
selector" now extends to "not an incremental feature either", at current power and feature
form. The lever for selection remains richer supervision — contrastive capture (#42, incl.
the desert batch 2) — not more sequential engineering on the passive corpus. Any chase of
this null (different feature forms, interactions, more data) is a NEW prereg.

## Non-claims (§7 hold)

No edge/behaviour/backtest/PnL/Genesis claim; no live-availability claim; no model promoted;
no facit touched; no auto-fib; 1H/ETH untouched.

## Reproduce

`PYTHONUNBUFFERED=1 uv run --no-sync python -u -m fibengine.research.selection_sequential
--sequential --config config/settings.expansion.yaml` →
`experiments/review/selection_sequential/summary.json` (gitignored/regenerable), ~35 min.

## Owner sign-off

- [x] **Signed 2026-07-21** — verdict accepted advisory→signed, no objections; teacher-forcing
      frame (§2/§9 A2) stays binding on every citation.
- [x] Sequential axis considered **bounded** (3 signed results) — next lever = contrastive
      capture (#42, batch 1 + desert batch 2).

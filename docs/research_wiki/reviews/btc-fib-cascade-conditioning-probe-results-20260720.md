# Results — Cascade-conditioning probe (does the previous fib predict the next origin?)

**Date run:** 2026-07-20 (labeling machine, Bitfinex egress OK) · **Prereg (locked, incl. pre-run
amendments §9):** [prereg](btc-fib-cascade-conditioning-probe-prereg-20260720.md) · **Status:**
**SIGNED OFF by owner 2026-07-21** (prereg §8). Executed verbatim: seed 20260720, n_perm=2000,
n_boot=2000, LOCKED acceptance origin band (`ACCEPT_AT=NEAR`), fail-closed corpus-manifest check
passed (484 base fibs, 13/24/76/371 — CRLF-normalized fingerprint, sibling commit).

## Verdict (primary cell, 4h)

**`sequential_origin_signal`** — the origin of the next human fib IS predicted by the endpoint
(`anchor_b`) of the most recently completed fib, far above a sequence-destroying permutation null:

| Cell | Role | Pairs | HR(H1a) | mean HR(N1) | p (one-sided) | gap CI95 | Verdict |
|------|------|-------|---------|-------------|---------------|----------|---------|
| **4h** | **primary** | **363** | **0.256** | **0.005** | **< 0.0005** (0/2000) | **[0.205, 0.298]** | **`sequential_origin_signal`** |
| 1d | context | 74 | 0.189 | 0.031 | < 0.0005 | [0.077, 0.253] | `context_only` |
| 1w | context | 23 | 0.391 | 0.084 | < 0.0005 | [0.133, 0.525] | `context_only` |
| 1M | context | 12 | 0.167 | 0.118 | 0.416 | [−0.118, 0.299] | `context_only` |

Exclusions (4h): 2 no-predecessor, 6 degenerate `cur`, **0 outside candle window** (full facit
coverage: 21 269 bars, 2016-11-05 → 2026-07-20). Both context cells with any power agree
directionally; 1M (12 pairs) shows nothing.

## What carries the signal

The effect is overwhelmingly **exact chaining**, not near-matching: of 93 4h hits, **76 are EXACT**
(1 bar / 0.75%), 12 SNARLIKT, 5 NEAR. Sensitivity at `ACCEPT_AT=EXACT`: HR = **0.209** (vs the
audit's descriptive 85/371 = 0.229 bar-exact links — consistent; the probe's predecessor is
*only* the latest completed leg, so links to older endpoints don't count). On 1w every hit is
EXACT (9/9).

**Per-direction split (declared sensitivity, never verdict-bearing):** 4h up 49/170 = 0.288,
down 44/193 = 0.228 — present in both directions, no direction artifact. (1d 0.222/0.158,
1w 0.267/0.625, 1M 0.000/0.400 — small-N context.)

**Secondary/descriptive (non-causal, prereg §9 A2):** H1b (fresh same-side extreme, conditions on
`cur`'s future direction) = 0.300 — only +0.044 over the parameter-free causal H1a; N2 (prominence
pivot, causally truncated per A1) = 0.072 — the already-falsified prominence rule stays weak even
as an inter-leg-window candidate.

## Interpretation (modest framing, binding when citing this)

- **First positive selection finding on the sequential axis**: ~1 in 4 origins is the previous
  endpoint (a random earlier endpoint lands there ~0.5% of the time). The self-reported cascade
  ("nästa rena impuls i sekvensen", U1) has measurable support in the facit.
- **It is a component, not the selector**: 74% of 4h origins are NOT the previous endpoint. This
  bounds sequential conditioning as one input alongside whatever the contrastive capture (#42) is
  hunting; it does **not** solve selection.
- Residual caveat for sign-off (prereg §2/§9): the probe was *motivated* by same-corpus descriptive
  counts. Mitigations (parameter-free H1a, independently locked band, 4h chosen for power not
  effect size) are in the prereg; the honest reading is "confirmed and quantified against a proper
  null", not "independently discovered".
- **Non-claims (§7) hold:** no edge / behaviour / backtest / PnL / Genesis claim; no model; no
  cascade data model built (P3 stays evidence-gated behind a separate GO); no facit touched;
  no auto-fib; 1H/ETH untouched.

## Reproduce

Deterministic, frozen data (no `--refresh`):
`uv run --no-sync python -m fibengine.research.cascade_conditioning --probe --config config/settings.expansion.yaml`
→ `experiments/review/cascade_conditioning/summary.json` (gitignored/regenerable). Original run
~25 min (O(n) `bar_of_timestamp` dominated). **Post-sign-off 2026-07-21:** the deferred
result-neutral memoization landed in `evaluation/bars.py` (exact per-index cache, ~2000× on the
hot path; bar-lookup cost ~25 min → ~1 s) — a re-run should now be minutes, dominated by N2's
`detect_pivots`. Not applied mid-prereg; the signed numbers above are from the original run.

## Owner sign-off

- [x] **Signed 2026-07-21** — verdict accepted advisory→signed, no objections; modest framing
      above stays binding when citing this ("component, not the selector").
- [x] **Degenerate-fib classification (2026-07-21): misclicks, not intentional.** All 7
      same-candle fibs are to be corrected/redrawn (or deleted) in the labeling GUI on the home
      machine — worklist in [handoff Next Step](../handoff.md). Until fixed they remain excluded
      as degenerate (as this probe already did); the fix does **not** retroactively touch this
      result (6 excluded `cur` on 4h regardless of classification).
- [x] Next: resume contrastive capture (#42) with the cascade result as context

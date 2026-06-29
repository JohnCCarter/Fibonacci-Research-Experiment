# Post-lock addenda — leg-agreement ruler prereg (2026-06-29)

Append-only companion to the **locked** prereg
[`btc-fib-leg-agreement-ruler-prereg-20260629.md`](btc-fib-leg-agreement-ruler-prereg-20260629.md).
The locked file is immutable; build notes, the run result, and sign-off status live here so the
registration is never edited against its result.

### A1 — Build under the lock (2026-06-29)

[`evaluation/leg_agreement.py`](../../../src/fibengine/evaluation/leg_agreement.py) — locked knobs
(`mean`, absolute, `W=2`, direction-gated `Leg`), secondary diagnostics `leg_agreement_min` +
`leg_agreement_iou` (bar-span), `best_match` assignment, and the gate statistic `auc` (tie-aware).
21 unit tests cover the synthetic sanity table + diagnostics + best-match + AUC. Confirm-run
`scratchpad/run_leg_agreement_ruler.py` imports the **committed** module (not the calibration copy).

### A2 — Run result: `ruler_usable` (2026-06-29, pending human sign-off)

Committed-module confirm-run (seed 20260629):

- **Synthetic sanity (Gate 1): PASS** — identity = 1.0, off-by-one = 0.75, direction-flip = 0,
  disjoint = 0.
- **4h ceiling vs null: AUC = 0.976 ≥ 0.90 → `ruler_usable`.** ceiling mean-median 1.000 (strict
  `min`-diagnostic median also 1.000), null median 0.000. n: 359 legs, 359 ceiling, 17 950 null.

**Honest notes (BINDING):**

- **AUC 0.976 here vs 0.968 in the pre-lock calibration** — same locked metric, no knob change. Precise
  cause: the confirm-run applies a `ti != tj` guard (`run_leg_agreement_ruler.py`) that excludes intra-
  bar legs; the calibration did not. That leg-set difference (+ independent random draw order) accounts
  for the gap. Both clear 0.90.
- **359 vs 365 legs: 6 facit legs are *intra-bar*** (both anchors map to the **same** 4h candle, so
  `high_bar == low_bar`). A bar-resolution ruler cannot represent a within-one-candle leg, so `Leg`
  rejects them and they are excluded — **flagged, not silently dropped** (<2% of corpus).

### A3 — Reference-selector colour omitted from the confirm-run (deviation disclosed)

Locked Method step 3 lists the most-prominent-adjacent-pair reference selector as **colour**. The
confirm-run scored only ceiling + null and omitted it. Benign (the reference selector is **never** in
the gate), but the deviation from the locked method is recorded here rather than left silent.

### A4 — Leakage-review HIGH finding + hard-null remediation (BINDING re-scope)

`leakage-validity-reviewer` (2026-06-29) cleared facit integrity, leakage, and no-post-hoc-gate-swap,
but raised a correct **HIGH** finding: **`ruler_usable` as worded overclaims.** Three real points:
(a) the locked gate `AUC(ceiling vs null) ≥ 0.90` is **in-sample** — calibration *maximized* that
statistic on the same 4h facit, so it cannot fail by construction; (b) `AUC ~0.97` is
**near-tautological** (ceiling ≈ exact match vs random ≈ 0 — already proven analytically by the
synthetic identity/disjoint sanity); (c) **near-miss discrimination — the regime a real selector lives
in — was untested.**

**Hard-null supplement** (`scratchpad/hard_null_leg_agreement_ruler.py`, committed metric): ceiling
vs the **2nd-nearest** pivot pair (a plausible-but-wrong pick).

| quantity | value |
|---|---|
| 2nd-nearest pivot distance | median **4.0 bars**, 0% within 1 bar |
| hard-null score | median 0, mean 0, **>0 share 0%** |
| ceiling score | median 1.000, **mean 0.792** |
| ceiling buckets | **=0: 5.3% · in(0,1): 39.3% · =1.0: 55.4%** |
| AUC(ceiling vs hard-null) | 0.974 |

→ **For *selection quality* the ruler is effectively BINARY** — every wrong (2nd-nearest) pick is
≥2 bars off and scores exactly 0 (`>0 share` = 0%). A selector either picks the right pivot pair (→ up
to the coverage-capped ceiling) or it scores 0. The high hard-null AUC is because the hard-null is
uniformly 0, **not** gradation.

→ **The sub-1.0 ceiling values are detector-COVERAGE artifacts, not selection near-misses** (sharpened
by the leakage-review). 2nd-nearest alternatives are ≥2 bars off (0% within 1 bar), so the in-(0,1)
band (39.3% of ceilings) cannot come from "close selections" — it comes from the *human's anchor not
sitting exactly on a detected pivot* (one endpoint 1 bar off → s=0.5). So "off-by-one graded" is a
true **synthetic unit-test** property that **does not fire on real candidate pairs**; it must not be
read as live real-data gradation. Effective ceiling mean **0.792** = the detector-coverage cap at
1-bar resolution (only 55.4% of legs have both anchors exactly on pivots).

→ **Do NOT re-open the W/aggregation calibration.** The discreteness is intrinsic to the pivot
universe (pivots ≥3–4 bars apart); no W and no mean-vs-min recovers a graded *selection* regime — they
differ only at ±1 bar, which never occurs among alternatives. The calibration was really choosing how
to weight coverage gaps (the 0.5s), not selection tolerance.

**Re-scoped verdict (BINDING):**
- **Valid as a STRICT selection-scorer** — it scores a *selection* (the A/B pair), which per-anchor
  recall (Stage-1 both_hit 0.90) cannot, so it is **not** redundant. Right pivot pair → high, any other
  pick → 0. Effective ceiling mean ~0.79.
- **Narrow, lumpy dynamic range** — ceiling scores cluster at {0, ~0.5, 1.0}, capped at 0.79; sub-1.0
  is coverage error. As a **training objective** this gives a near-binary signal → the
  separately-registered **learned-selector prereg must confront whether this range can distinguish a
  good selector from a mediocre one at all** (ranking/classification target, or an auxiliary continuous
  signal — not regression on this score).
- The locked decision rule returns `ruler_usable` (AUC 0.974 ≥ 0.90), but the locked AUC gate is
  **in-sample / near-tautological** (findings (a)/(b)); disclosed, not edited (lock is immutable). The
  hard-null + bucket histogram are the real evidence; the strict-scorer reading above is the honest one.

### Status

**SIGNED OFF 2026-06-29 (human).** The re-scoped verdict (A4) is the confirmed result: the
leg-agreement ruler is a **valid strict selection-scorer** (scores the A/B *selection*, which per-anchor
recall cannot — not redundant) with a **narrow, coverage-capped dynamic range** (effective ceiling mean
~0.79; sub-1.0 values are detector-coverage artifacts, not selection near-misses; for selection quality
it is effectively binary, hard-null 100% zero). **Usable as a strict evaluation instrument; NOT a graded
training objective as-is** — the separately-registered learned-selector prereg must confront the narrow
dynamic range (ranking/classification target or an auxiliary continuous signal). The locked AUC gate is
acknowledged in-sample/near-tautological; the W/aggregation calibration is **not** re-opened (the
discreteness is intrinsic to the pivot universe). Descriptive, step-1; no edge/OOS/PnL claim. No new
facit created by this sign-off.

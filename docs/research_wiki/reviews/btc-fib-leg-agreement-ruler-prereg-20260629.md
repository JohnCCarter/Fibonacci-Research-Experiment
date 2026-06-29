<!-- prereg:locked -->
<!-- This file is immutable after lock. Run results / addenda go in the *-postlock.md sibling.
     A PreToolUse hook (.claude/hooks/guard-locked-prereg.sh) asks before any Edit/Write here. -->
# Leg-agreement ruler — measurement pre-reg (LOCKED 2026-06-29)

**Status:** LOCKED 2026-06-29 (human sign-off). Knobs fixed by *selector-independent* pre-lock
calibration (below) and frozen. Build of `evaluation/leg_agreement.py` + sanity + 4h scoring
authorized under this lock. Registers the **measurement instrument** for north-star step 1 — it is the
free facit-checker the selection campaign lacked (in #38 `agreement` floored for **both** arms because
`compare_label`/`select_swing` are not localized to the facit leg). Scope is **a usable measurement,
not a selection result** — no edge / OOS / PnL / Genesis / auto-fib claim.
Relates to: the closed per-leg-feature line (`exclusivity`, `impulse_leg`), the standing candidate
**#31** (fractal anchor detection), and the [north star](../north-star.md).

## Question

Is the **facit-localized leg-agreement metric** `leg_agreement(facit_leg, candidate_leg)` in [0,1]
a trustworthy ruler for "did the machine pick the same A/B leg as Chamoun" — i.e. (a) identical leg →
1.0, (b) graded in endpoint distance, (c) it **separates a known-good selection (coverage ceiling)
from a random pair** on the real 4h candidate universe?

A leg = an ordered anchor pair (A, B) = a price–time span with a direction. This prereg registers the
**ruler only**. The *learned* selector the ruler will train/evaluate is a **separate, later prereg** —
building it now would repeat #38's "unmeasurable result" mistake.

## Why the ruler first (background — locked framing)

- **Detection is solved, selection is the crux.** Stage-1 `no_pivot_signal_above_prominence` (4h recall
  0.90) + the transcribe facit-validation (all 142 anchors sit exactly on candle extremes, max
  delta 0.0046%) → the open question is **which pair of extremes** the human connects into a meaningful
  leg, not whether extremes are found.
- **Hand-engineered features plateaued.** The `selection_learning` campaign (gestalt, `cleanliness`,
  prominence-family, `exclusivity`, `impulse_leg`, wick-pair) is modest/null. The frontier is (1) a
  ruler, then (2) learn-to-select directly. This prereg is (1).
- **4h is the only powered cell** (N≈365); 1M/1w/1d are context only (structurally data-starved). The
  ruler is exercised on 4h.

## Key risks this study confronts (honesty — BINDING)

1. **A new ruler can be tuned post-hoc to flatter a result.** → Metric form, aggregator, tolerance, and
   the pass threshold are **fixed by selector-independent calibration only** (ceiling-vs-null + synthetic
   sanity), locked before any selector exists. Synthetic sanity cannot be gamed by a selector.
2. **"Ruler broken" must not be confused with "selector bad".** → Resolved in the GATE: the verdict
   rests on **[synthetic sanity] + [coverage-ceiling vs random-null AUC]**. The ceiling (nearest
   candidate pair to each facit leg) scores high **only if the ruler discriminates when a good pick
   exists** — independent of any selector. A trivial reference selector is **descriptive colour, never
   in the gate**.

## Metric (LOCKED — knobs fixed by pre-lock calibration)

Both anchors are candle extremes (proven), so a leg's endpoints are **bars**. Compare by role
(high↔high, low↔low), require same direction.

- **Primary:** endpoint bar-agreement with linear decay. Per endpoint `s = max(0, 1 − Δbar / W)` with
  `Δbar` = |bar_index(facit) − bar_index(candidate)|. **`leg_agreement = mean(s_high, s_low)`;
  direction mismatch → 0.** **LOCKED knobs: AGG = `mean`, tolerance = absolute bars, `W = 2`.**
- **Secondary diagnostic field (NOT primary, NOT in the gate):** `min(s_high, s_low)` (strict
  both-endpoints reading) and IoU(price–time span).
- **Multi-leg-per-window assignment:** best-match (each candidate leg scored against its **closest**
  facit leg in the window) — no Hungarian solver.

## Pre-lock instrument calibration (selector-independent — DONE 2026-06-29)

Script `scratchpad/calibrate_leg_agreement_ruler.py` (seed 20260629), read-only, no selector involved.
365 4h facit legs; fractal universe 7215 pivots. **Inter-pivot spacing median 2.0 bars** (p10 1, p90 6).
AUC(coverage-ceiling vs random-null):

| AGG | W=1 | W=2 | W=3 | W=5 |
|---|---|---|---|---|
| **mean** | 0.951 | **0.968** | 0.973 | 0.977 |
| min / product | 0.773 | 0.873 | 0.914 | 0.956 |

(relative tolerance never beat absolute.) **Spacing guard:** W must be < typical spacing (median 2.0)
or a match lands on a *neighbouring* pivot → **W=5 rejected despite its higher AUC** (leniency, not
correctness). At the spacing-safe W=2, only `mean` clears AUC ≥ 0.90 (min/product 0.873 would force
W=3, loosening past the guard). → **mean / absolute / W=2 locked.** Calibrating on the full facit's
geometry is instrument design (thermometer scale), not fitting the selector under test.

## Sanity cases (synthetic — must PASS in the build before any real score)

| Case | Construction | Required | (mean, W=2) |
|---|---|---|---|
| Identity | facit vs itself | `= 1.0` | 1.0 |
| Off-by-one | one endpoint ±1 bar | strictly in (0,1) | 0.75 |
| Direction flip | same endpoints, opposite dir | `= 0` | 0 |
| Random pair | random A/B from 4h universe | null band ≈0 | ~0 |
| Disjoint | clearly different leg | ≈0 | ~0 |

## Baselines (LOCKED)

- **Random-pair null:** random A/B from the fractal universe (#31 `pivots/detect.py` `mode:"fractal"`),
  per facit window. The floor the ruler must separate from.
- **Coverage ceiling (IN the gate):** nearest candidate pair to each facit leg.
- **Reference selector (descriptive colour, NOT in the gate):** most-prominent adjacent pivot pair.

## Method (built only under this lock)

1. New `src/fibengine/evaluation/leg_agreement.py` — the metric (locked knobs; secondary fields).
   Reuses facit loading (`labeling/human_fib`) + fractal universe (`pivots/detect.py`,
   `evaluation/pivot_recall.py`); no detector, no target/outcome — pure selection-vs-selection.
2. Run the **synthetic** sanity table (selector-independent). Gate 1 (must pass).
3. On 4h facit (N≈365): score random-null, coverage ceiling, and (colour only) the reference selector;
   report distributions + **AUC(ceiling vs null)**.
4. Causal hygiene: a candidate leg uses only pivots with index ≤ its later endpoint (no peek). The
   comparison itself is outcome-free.

## Decision rule (LOCKED)

- **`ruler_usable`** if: synthetic identity = 1.0; off-by-one graded; direction-flip = 0; **and
  AUC(coverage-ceiling vs random-null) ≥ 0.90** on 4h. → ready as the objective + eval for a
  separately-registered learned selector. (Calibration already shows 0.968 at the locked knobs;
  the build re-confirms with the committed module.)
- **`ruler_inconclusive`** if synthetic sanity passes but AUC < 0.90 → metric sound, selection on 4h
  genuinely hard at this granularity; diagnose before a learned selector. First-class outcome.
- **`ruler_unsound`** if synthetic sanity fails → redesign; no real-data score reported until it passes.
- The reference selector is **never** a pass/fail input. No redefinition against the result. The ruler
  is an **instrument**, not a finding.

## Non-claims (BINDING)

North-star **step 1, descriptive only**. No edge / OOS-significance / PnL / backtest / Genesis /
auto-fib. 4h is the only powered cell; HTF context only. A high score for some selector is **not**
"the machine selects like Chamoun" — that needs the separately-registered learned-selector run, signed
off by the human.

## Gate

LOCKED 2026-06-29 (human sign-off). Build (metric + sanity + 4h scoring) authorized under this lock.
`leakage-validity-reviewer` runs before any score is trusted. Result becomes "truth" only after human
sign-off of the run output.

---

## Post-lock addenda

This prereg is **immutable** after lock. All post-lock material — build notes, the run result, and
sign-off status — lives in a **separate, unguarded** companion file so the registration is never
edited against its own result:

→ [`btc-fib-leg-agreement-ruler-prereg-20260629-postlock.md`](btc-fib-leg-agreement-ruler-prereg-20260629-postlock.md)

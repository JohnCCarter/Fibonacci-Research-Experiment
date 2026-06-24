# BTC Fib Selection-Learning — `cleanliness` artifact-probe RESULTS (2026-06-24)

**Lean Fib Research. Research-only. Selection learning — NOT a behaviour/edge claim, no
backtest/PnL, no Genesis, no auto-fib-as-truth, no label mutation.** First (and only) run of the
cheap-first `cleanliness` artifact-probe, executed exactly per the
[artifact LOCK](btc-fib-selection-learning-artifact-lock-20260624.md) (`b533385`): two existing-data
contrasts (surfacing A2, snapping A3), quarter-block bootstrap (A5), **per-contrast verdict rules A7
fixed blind before any number existed**. Tests the open crux from the
[campaign checkpoint](btc-fib-selection-learning-checkpoint-20260624.md). **No matched-null, no new
candidate universe** (gated, A8). Builds on the [Stage-2 lead](btc-fib-selection-learning-results-20260618.md),
[W-gap](btc-fib-selection-learning-w-gap-results-20260623.md), and
[Stage-1](btc-fib-selection-learning-stage1-results-20260624.md).

> **STATUS — the inflationary detector-artifact hypothesis gets NO support on the 4h primary; both
> contrasts point the OTHER way, but marginally / non-replicating → "investigate, not a finding".**
> Fidelity holds (reached = **0.860**, in band, reproduces the Stage-2 ~0.83 split). **Surfacing:**
> reached legs are *less* clean than unreached (gap **−0.0557**, 95% CI **[−0.1150, −0.00095]** excludes
> 0 **below**, `p(gap≤0)=0.977`) → the locked direction guard **`inverse_surfacing`** — *investigate,
> not a finding* (and **marginal**: CI upper −0.00095, a hair under 0, the mirror image of the
> W-gap k=12 +0.0004 caveat). **Snapping:** snapping to detector pivots *lowers* cleanliness (gap
> **−0.0219**, 95% CI **[−0.0320, −0.0102]**, `p=1.0`) → the locked direction guard
> **`snapping_deflates`** — *investigate, not a finding*. Both guards point **against** the
> inflationary artifact (which predicted reached>unreached and snapped>exact). **But this is NOT
> `artifact_risk_reduced`** — that locked label requires both CIs to *include* 0, which did NOT happen.
> And the snapping effect **does not replicate**: the 1d context cell shows snapping *inflates*
> (+0.0222, CI [0.0007, 0.0492]) — **opposite sign** → TF-dependent / investigate. **No positive claim,
> no lock change, no matched-null.**

## Combined outcome — A7 unregistered (reported verbatim, no new verdict)

**A7 did not pre-register a combined powered direction-guard outcome.** Therefore **no new combined
verdict is assigned.** The correct handling — and the one applied here — is to report the two locked
per-contrast direction guards verbatim as **"investigate, not a finding"**. The harness emits a
**descriptive `meta:` status** (`meta:a7_unregistered_powered_direction_guard`) for this case, **not** a
locked verdict, and explicitly **not** `inconclusive_underpowered` (the cells ARE powered — 314 reached
/ 51 unreached, 2000 effective resamples; that label would be a misnomer). **The lock was not changed.**

## What was built + run

**New module** `src/fibengine/research/selection_learning_artifact.py` (own `--artifact` /
`--artifact-preflight` CLI; **no code added to byte-capped `selection_learning.py`**) + 13 tests. Per
leg: `cleanliness` is the source-bound `core.features._cleanliness` reduced to the endpoints' bar-index
span (A1 — span-only, so inherently causal; the span is pre-`anchor_b`). A leg is **reached** iff both
anchors are ε-reconstructable by the **causal** detector at `anchor_b + k=3` (Stage-2 ε-rule, A2);
**all 365 4h legs are used — unreached are the signal, never filtered.** Snapping (A3) compares
exact-anchor vs ε-matched-detector-pivot cleanliness, **paired, reached only, no imputation**.
Bootstrap = quarter-block (detector-free, A5), 2000 resamples, seed `20260618`, degenerate resamples
skipped (`n_boot_effective` reported). Run on the **frozen** data universe (no `--refresh`; preflight
READY).

## Results — surfacing (coverage) and snapping reported separately (LOCK A2/A3)

**4h (primary, both contrasts powered):** reached = 314/365 = **0.860** (fidelity OK, band [0.75, 0.90]).

| contrast | gap | 95% CI | p(gap≤0) | n | locked per-contrast verdict |
|----------|----:|--------|---------:|---|-----------------------------|
| **surfacing** (clean reached − unreached) | **−0.0557** | [−0.1150, **−0.00095**] | 0.977 | 314 / 51 | **`inverse_surfacing`** — direction guard, *investigate* |
| **snapping** (snapped − exact, paired) | **−0.0219** | [−0.0320, −0.0102] | 1.000 | 314 pairs, 0 dropped | **`snapping_deflates`** — direction guard, *investigate* |

- mean cleanliness: reached **0.743** vs unreached **0.799** (reached legs are *less* clean).
- Both guards fire **against** the inflationary artifact; the surfacing one is **marginal** (CI upper
  −0.00095).

**Context (1M/1w/1d, k=3 — surfacing underpowered everywhere; snapping powered on 1w/1d):**

| TF | reached_frac | surfacing | snapping gap | snapping CI | snapping verdict | cell |
|----|----:|-----------|----:|--------|------------------|------|
| 1M | 1.000 (9 legs) | underpowered | — | — | underpowered | inconclusive_underpowered |
| 1w | 0.905 (19/2) | underpowered | −0.0057 | [−0.0252, +0.0076] | `no_snapping_inflation` | inconclusive_underpowered |
| 1d | 0.896 (60/7) | underpowered (7<10) | **+0.0222** | [+0.0007, +0.0492] | **`snapping_inflates_cleanliness`** | `detector_artifact_supported` |

- **The snapping effect does not replicate across TFs:** 4h `snapping_deflates` (−0.022) vs 1d
  `snapping_inflates_cleanliness` (+0.022) — **opposite sign**. A robust structural fact would hold
  sign; the flip says the effect is **TF-dependent / noisy**, which is exactly what the direction guard
  ("investigate, not a finding") is for. The 1d cell's `detector_artifact_supported` is a **context**
  reading, not the primary, and the cross-TF disagreement means **neither sign is claimed**.
- 1M/1w surfacing carry no inferential weight (0 / 2 unreached legs).

## Interpretation (honest; no positive claim)

- The Stage-2 `cleanliness` lead being a **detector-inflation** artifact would require the detector to
  **surface** cleaner human legs (reached>unreached) and/or **snapping** to **raise** cleanliness
  (snapped>exact). On the 4h primary **both go the opposite way.** So the simple "the detector inflates
  cleanliness" story gets **no support** on the powered primary cell.
- **This is not a clean win for "genuine signal."** (1) It is **not** `artifact_risk_reduced` — both CIs
  *exclude* 0 (the direction guards), not include it. (2) The reversals are **marginal** (surfacing CI
  upper −0.00095) or **non-replicating** (snapping flips sign on 1d). (3) The guards were locked
  precisely as **"investigate, not a finding"** for this reason. Mechanically plausible: the detector
  reconstructs **larger/longer** swings (more intermediate retracement → lower cleanliness), and
  snapping **extends** the span to fuller extremes (more path) — both *deflate* cleanliness, neither
  proves anything about human selection.
- **Net:** the result **weakens** the inflationary-artifact hypothesis but **claims nothing positive**;
  the crux stays **open**, now with a sharper investigate-target (why reached/snapped legs are *less*
  clean, and why snapping flips sign by TF).

## Build-time resolution (documented; not a locked decision point)

**Anchor kind** (low/high expected at each anchor) is taken from the leg `direction` when present, else
derived from the price order (`anchor_b_price ≥ anchor_a_price ⇒ a=low, b=high`) — the `direction`
sidecar field can be empty. This only affects which detector-pivot kind an anchor may ε-match; a wrong
assignment would *reduce* matches (lower reached) → conservative, cannot manufacture an artifact signal.

## Observed / Inferred / Unverified

- **Observed (verified):** the numbers above; 4h reached 0.860 (fidelity OK); surfacing gap −0.0557 CI
  [−0.1150, −0.00095]; snapping gap −0.0219 CI [−0.0320, −0.0102]; 1d snapping +0.0222 CI [+0.0007,
  +0.0492] (opposite sign); both 4h contrasts powered (314/51), 2000 effective resamples;
  cleanliness span-only/causal; 13 unit tests green; run deterministic, resume-safe.
- **Inferred (scoped to 4h / these contrasts):** the inflationary detector-artifact (surfacing/snapping
  mechanically raising cleanliness for human-matched legs) is **not supported** on the powered primary —
  both mechanisms point against it.
- **Unverified / scope limits (do not claim past these):**
  1. **Not `artifact_risk_reduced`** — both CIs exclude 0 (direction guards), not include it.
  2. **Marginal / non-replicating** — surfacing CI upper −0.00095; snapping flips sign 4h↔1d →
     TF-dependent, investigate, **no sign claimed**.
  3. A7 has **no registered combined label** for this case → **no new combined verdict**; the binding
     reading is the two per-contrast guards (`meta:` status, not a verdict).
  4. The broader "is human-leg cleanliness special vs a matched non-human swing" question is **out of
     scope** (matched-null gated, A8 — **not built**, and would need its own separate blind lock).

## Non-claims (LOCK A9 binding)

Not a reproduction of human selection. **No edge / behaviour / PnL / backtest / strategy claim.** This
result does **not** prove `cleanliness` is "human intuition"; it only **weakens one specific mechanical
explanation** (detector inflation) on one powered cell, without a clean verdict. The `cleanliness`-as-
genuine-signal question stays **OPEN**. No Genesis, no auto-fib-as-truth, no label/corpus mutation, no
1H, no ETH, no `data.fetch --refresh` (frozen-data parity — same universe as Stage-2 / W-gap / Stage-1).
**The lock was not changed.**

## Discipline honoured

Per-contrast verdict rules A7 fixed **blind** in the 2026-06-24 lock (`b533385`) before any number was
computed; applied verbatim. The A7-unregistered combined case is reported as a **descriptive `meta:`
status**, not relabelled and not invented as a new locked verdict — **the lock was not changed**.
Frozen-data parity held (no `--refresh`; preflight READY). Coverage (reached) reported separately from
both contrasts. Matched-null **not built** (gated, A8). Artifacts
(`experiments/review/fib_selection_learning/artifact/summary.json` + `…/cells/*.json`) are
**gitignored**, regenerable.

> On the 4h primary, the "detector inflates cleanliness" artifact gets **no support** — surfacing and
> snapping both point the other way — but **marginally** (surfacing) and **non-replicating** (snapping
> flips sign on 1d), so per the locked direction guards this is **"investigate, not a finding"**, **not**
> `artifact_risk_reduced`, and **no positive claim**. The crux stays open. No lock change, no
> matched-null, no edge/behaviour claim.

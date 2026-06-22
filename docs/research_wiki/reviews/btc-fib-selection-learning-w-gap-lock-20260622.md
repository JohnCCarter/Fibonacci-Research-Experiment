# BTC Fib Selection-Learning — Retrospective `W` / causal-availability-gap LOCK (2026-06-22)

**DOCS-ONLY. Authorises no code, no run, no dependency, no label/corpus change.** This freezes the
**gap metric, split parity, bootstrap/CI rule, verdict rule, compared cells/baselines, and
non-claims** for side-quest #1 (retrospective `W` model / causal-availability gap), **blind to any
output**, before any retrospective run. Builds on the frozen pins in the
[§12 addendum](btc-fib-selection-learning-addendum-20260618.md) and the
[Stage-2 / k-sweep results](btc-fib-selection-learning-results-20260618.md). Execution of the gap run
needs a **separate explicit GO** (this doc is Commit 1 only).

**Blindness attestation:** no retrospective `W` model has been built or run; **no gap value, no
retrospective AP, has ever been computed or seen.** The k-sweep produced live-equivalent APs and the
§6 lifts only. Every rule below is fixed from the addendum, the prereg, and existing code — not from
any gap result.

## L0. What is already locked upstream (reused verbatim, not re-decided)

From the [§12 addendum §A5/§A2](btc-fib-selection-learning-addendum-20260618.md):

- **`W` (4h, primary) = 180 bars** (~30-day forward bounded viewport); 1M=24, 1w=52, 1d=120.
- **`k`-sweep cells = {0, 3, 6, 12}**, **primary `k = 3`** (base-detector confirmation).
- **Live-equivalent model at `k`** = features with `k*(f) ≤ k` (column selection): `k=3` →
  `{magnitude, cleanliness, duration, prominence, structure_alignment, exclusivity}`; `recency` never
  live.
- **Retrospective `W` model** = all eight features computable within `W` (`W ≥ k*`), with `recency` in
  its **viewport-relative** form `(anchor_b.index − viewport_start) / (W + (anchor_b − anchor_a))`
  (retrospective-only).
- **Primary metric = pooled Average Precision (AP)**; ROC-AUC secondary. **ε reused** (`time_tol=3`,
  `price_tol=0.5` ATR). **Coverage ceiling** reported alongside.
- **§6 baseline family** (from results): magnitude (required) + prominence-A (summed) + prominence-B
  (max).

## L1. Gap metric (the new lock)

For each powered cell `k`:

> **gap(k) = AP(retrospective `W` model) − AP(live-equivalent model at `k`)**, both ranking the
> **identical candidate rows** of the **live-equivalent-at-`k` universe**, pooled test AP.

- **Sign convention:** gap > 0 ⇒ the bounded-retrospective view carries selection information the
  live view at `k` cannot. gap ≈ 0 ⇒ the live model already matches retrospection at `k`.
- The gap is computed **internally** within this study; it does **not** reuse the headline live APs
  (those used a different embargo — see L2).

## L2. Candidate-universe + split parity (the load-bearing resolution)

**This is the choice that makes the gap a *causal-availability* (feature-availability) gap rather than
a universe-size artifact. Locked with reason, before any run.**

- **Same rows.** Within each cell `k`, the candidate universe is the **live-equivalent-at-`k`
  universe** — re-detected on the frame truncated at `anchor_b + k`, exactly as the k-sweep built it.
  The retrospective `W` model scores **those same rows**, differing **only** in that its features are
  computed over the bounded `W` viewport (all eight, `recency` viewport-relative). *Reason:* holding
  the row set fixed isolates the effect of **what each model can compute** from the effect of **which
  legs hindsight reveals**; the latter is a different (Stage-1/detection) question, out of scope here.
  This is the only reading consistent with §A5's "gap closes as `k`→12 when `scale_confluence` is
  admitted" (a feature-admission statement).
- **Common embargo = `W`.** Both models are evaluated under **one** purged/embargoed split on
  `anchor_b` chart time with **embargo = `W` bars** (the larger forward reach, = the retrospective
  model's actual look-ahead), applied identically to both. *Reason:* an embargo of only `k` would
  leak into the retrospective model's `W`-window features; using `W` for both keeps the **test set
  identical** within the cell and leakage-safe for both. It is conservative for the live model (fewer
  test points), never anti-conservative.
- **Models held fixed.** As in the headline: trained once per cell, **no refit** during bootstrap.

## L3. Bootstrap / CI rule (reused machinery)

- **Decision-point cluster bootstrap**, identical to the headline: resample **whole `anchor_b`
  groups** with replacement, re-pool their candidates, recompute gap(k) on the **held-fixed** models
  (no refit), **2000 resamples, seed 20260618**.
- Report gap(k) **point estimate + 95% CI** and one-sided `p(gap ≤ 0)` per cell. Read as a
  **bootstrap-stability** statement (gap robust across decision-point resamples), **not** a
  permutation-null p-value.

## L4. Cells + baselines compared (locked, explicit)

- **Gap cells = `k ∈ {3, 6, 12}`.** **`k = 0` is excluded** — degenerate (empty universe,
  `reachable_fraction = 0.0`, unpowered) per the k-sweep; **not interpretable**, not a null.
- **Primary gap cell = `k = 3`** (matches the headline buffer).
- **Power floor (§8):** a cell is powered only with **≥ 10 test positives**. Expected powered: **4h
  only**; 1M/1w/1d reported as **`underpowered`** (context, not refuted).
- **Reference floor (parity, reported not claimed):** for each cell, also report the retrospective
  model's AP-lift vs the **§6 baseline family** (magnitude + prominence A/B) — the same floor the
  live model is measured against — so "does hindsight also beat the trivial rules?" is visible. The
  **primary locked comparison is the gap (retro − live)**, not this floor.

## L5. Verdict rule (pre-stated, falsifiable — 4h primary)

Using gap(k) point estimate + 95% CI for `k ∈ {3, 6, 12}`:

- **`no_causal_gap`** — gap(`k=3`) CI **includes 0**: the live model at the headline buffer already
  matches the bounded-retrospective model; selection (as captured by these features) needs no
  hindsight beyond `k=3`.
- **`gap_closes_with_buffer`** — gap(`k=3`) CI **excludes 0 (>0)** **and** gap(`k=12`) CI
  **includes 0**: the `k=3` cutoff was merely too tight; admitting `scale_confluence` at `k=12`
  recovers the retrospective advantage.
- **`gap_persists`** — gap(`k=12`) CI **excludes 0 (>0)**: genuine right-edge / hindsight dependence
  remains even after all live-confirmable features are admitted.
- **`inconclusive`** — powered but the CIs straddle the thresholds ambiguously; reported as such, **no
  forced label**.
- **`artifact_check_needed`** (direction guard) — any gap(k) **< 0** (live > retro): a modeling
  artifact (e.g., embargo width or viewport-relative `recency` hurting the retrospective model), **not
  a finding** — investigate before interpreting.

The gap is **secondary / sensitivity** per §A5 (the retrospective `W` model is explicitly listed as
secondary). It is **descriptive with CIs**, does **not** enter the four-TF Holm headline family, and
**adds no new positive claim**.

## L6. Non-claims (binding — what this must NOT be read as)

- **Not a reproduction.** A small or zero gap does **not** mean the human is reproduced — absolute AP
  stays low (~0.057 at `k=3`, capped by the ~0.83 coverage ceiling). The gap is about *how much
  hindsight the live view lacks*, not about agreement level.
- **No edge / behaviour / PnL / backtest / strategy claim.** A persisting gap means the *label* needs
  hindsight to reproduce — it says **nothing** about tradeable information or market reaction (the
  behaviour line is **closed NULL**).
- **`cleanliness`-as-artifact stays an open non-claim.** The gap does not resolve whether the
  cleanliness lead is a detection/anchoring artifact; that remains the open interpretive question.
- **"Any swept cell beats baseline" is not a valid claim** (the B-1 forking-paths lesson is binding).
- **No Genesis, no auto-fib-as-truth, no label/corpus mutation, no 1H, no ETH.**

## L7. Why this is NOT forking-paths

- `W`, the `k`-cells, primary `k=3`, the metric, ε, and the §6 family were pinned in the **2026-06-18
  addendum/results, blind**, and are reused verbatim.
- The **only new locks** (gap scalar L1, same-row + embargo-`W` parity L2, bootstrap reuse L3, verdict
  thresholds L5) are pinned **now, before the retrospective model exists** and **before any gap value
  has been computed** (blindness attestation above). The verdict rule is fixed **before** seeing which
  branch the data takes.

## L8. What this doc does NOT do

No code, no harness, no run, no dependency, no label/corpus mutation. Does **not** grant execution —
Commit 2 (build + run) requires a **separate explicit GO**, and must halt if any of {W-definition,
metric, split, candidate universe, non-claims} is found unclear at build time.

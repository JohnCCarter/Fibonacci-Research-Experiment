# Pre-registration — Cascade-conditioning probe (does the previous fib predict the next origin?)

**Date:** 2026-07-20 · **Line:** Fib SELECTION-LEARNING (north-star step 1) · **Status:** registered,
**run pending** (candle cache unavailable in the authoring container — Bitfinex egress blocked).
**Authorization:** owner pre-authorized autonomous execution of the 2026-07-20 audit remediation
plan ("Jag godkänner redan nu att du får fixa det som kräver mig", 2026-07-20). Verdict remains
**advisory until owner sign-off** of the results doc. This registration must not be edited after
the first run; post-run material goes to a `-results-` / `-postlock-` sibling.

## 1. Question (one sentence)

When a new human fib leg begins, is its **origin** (`anchor_a`) predicted by the **endpoint of the
most recently completed human fib** (`anchor_b` of the predecessor) — i.e., is selection
*sequentially conditioned* — significantly better than a sequence-destroying null?

## 2. Motivation (disclosed, pre-run)

- The 2026-07-20 audit measured (descriptively, on the committed corpus): 4h has **85/371 legs whose
  `anchor_a` exactly equals a prior leg's `anchor_b`** (bar-exact), 23 shared endpoints, 81/371
  time-contained legs; 1w 9/24, 1d 14/76 chain-links. These descriptives motivated this prereg and
  are therefore **not** evidence for its verdict (same-data discovery is disclosed here).
- The style doc marks cascade/trend-sequentiality **U1: top self-reported signal, untested**. Six
  decomposition probes bounded the positive selection rule as **non-geometric** (context-free axis
  exhausted: `no_pivot_signal_above_prominence`, `enriched_worse_check`, flat origin-rank nulls).
  The sequential hypothesis is the major *untested* remaining direction, and it is testable on
  existing facit — **no new labels**.

## 3. Corpus (LOCKED)

`data/labels/human_fib/MANIFEST.json` as of this registration: 1M=13, 1w=24, 1d=76, 4h=371
(total 484); sha256 per TF as committed in that file. The run MUST call
`corpus_manifest.verify_manifest()` first and abort on any drift (fail-closed). Candle cache:
`config/settings.expansion.yaml` fetch, recorded (bars, first_ts, last_ts) in the results doc.

**Primary cell: 4h** (only powered TF). Context cells: 1d, 1w, 1M (reported, never verdict-bearing).

## 4. Pair construction (frozen rules)

1. Sort a TF's legs by `anchor_a.time` (ties: `anchor_b.time`, then `fib_id`).
2. For each leg `cur`, the predecessor is the leg with the **latest `anchor_b.time` ≤
   `cur.anchor_a.time`** (equality allowed — exact chains count; ties: latest `anchor_a.time`,
   then `fib_id`).
3. Exclusions (each counted and reported): `cur` with no qualifying predecessor; **degenerate
   `cur`** (`anchor_a.time == anchor_b.time` — 7 such legs exist, flagged to the owner in
   handoff Open Questions; a degenerate leg MAY serve as predecessor); `cur` whose anchors fall
   outside the loaded candle window.

## 5. Hypotheses and scoring (frozen)

Scoring function for ANY candidate origin point `(bar, price)` vs `cur.anchor_a`: the LOCKED
origin band of `evaluation/acceptance.py` (`classify_anchor(is_origin=True)`; EXACT 1 bar/0.75%,
SNARLIKT 2/1.5%, NEAR 3/2.0%; **accept = NEAR**, `ACCEPT_AT` — locked 2026-07-02, not tuned here).
Bar positions via `evaluation.bars.bar_of_timestamp` on the loaded candle frame.

- **H1a (PRIMARY):** candidate = predecessor's `anchor_b` (bar + price). Parameter-free, causally
  clean (uses nothing about `cur` except which leg is "next").
- **N1 (PRIMARY NULL — permutation):** for each pair, replace the true predecessor's `anchor_b`
  with the `anchor_b` of a **uniformly drawn other leg of the same TF whose `anchor_b.time` ≤
  `cur.anchor_a.time`** (causality preserved; sequence destroyed; marginal price/time
  distributions preserved). Deterministic seed **20260720**; `n_perm = 2000` permutation
  replicates of the pooled hit-rate.
- **H1b (SECONDARY, descriptive only):** candidate = the most extreme same-side price extreme
  (high for a down `cur`, low for an up `cur`) strictly between predecessor `anchor_b.time` and
  `cur.anchor_a.time` (exclusive of `cur.anchor_a`'s own bar). Conditioning on `cur`'s origin
  time is **disclosed**; H1b never bears the verdict.
- **N2 (SECONDARY CONTROL, descriptive only):** candidate = most ATR-prominent pivot
  (`pivots.detect`, baseline `PivotConfig`) in the same inter-leg window — the already-falsified
  prominence rule, as calibration context.

## 6. Statistics and verdict family (frozen — pick exactly one, per cell)

Primary statistic: pooled 4h hit-rate `HR(H1a)` (fraction of included pairs where the candidate
reaches `ACCEPT_AT`) vs the permutation distribution `HR(N1)`.

- **`sequential_origin_signal`** — one-sided permutation `p < 0.05` AND the bootstrap 95% CI
  (pair-resample, B=2000, seed 20260720) of `HR(H1a) − mean HR(N1)` excludes 0 from below.
- **`no_sequential_signal`** — otherwise, with ≥ 50 included pairs.
- **`inconclusive_underpowered`** — fewer than 50 included pairs (expected only in context cells).

No other outcome may be reported as a verdict. Sensitivity (reported, never verdict-bearing):
tier distribution (EXACT/SNARLIKT/NEAR), H1a at `ACCEPT_AT=EXACT`, per-direction split
(up-origin vs down-origin `cur`).

## 7. Non-claims (binding)

No edge / behaviour / backtest / PnL / Genesis claim. No model is trained. No cascade data model
is built from this probe (that is a separate, evidence-gated decision — P3 of the audit plan).
No facit is created, edited, or promoted. No auto-fib. 1H and ETH untouched. A positive verdict
means only: *the next origin is sequentially predictable above a sequence-destroyed null on this
corpus* — it does NOT mean selection is solved.

## 8. Run protocol

`uv run python -m fibengine.research.cascade_conditioning --probe` (deterministic; summary to
stdout; per-cell JSON to `experiments/review/cascade_conditioning/` — gitignored/regenerable).
Results doc: `btc-fib-cascade-conditioning-probe-results-<date>.md`, marked **advisory pending
owner sign-off**.

## 9. Pre-run amendments (2026-07-20, leakage-validity review — **no run has occurred**)

The committed harness was reviewed by the `leakage-validity-reviewer` before any execution.
Review verdict: **H1a/N1 (the only verdict-bearing path) causally clean**; the findings below
were fixed *before the first run*, so §7's no-post-run-edit rule is not violated. §1–§8 are
otherwise unchanged.

- **A1 (blocking, fixed):** N2's pivot lookup ran `detect_pivots` on the full candle frame; the
  detector's *centered* prominence window (baseline `lookback=3`) meant a pivot near
  `cur.anchor_a` could be admitted/ranked using up to 3 bars **after** the origin — look-ahead,
  worst exactly in tight chains. Fixed: the frame is truncated at `cur.anchor_a`'s bar before
  detection (`df.iloc[:hi_bar+1]`), matching the sibling truncate-then-detect convention
  (`selection_learning*.py`). N2 stays descriptive-only.
- **A2 (disclosure completed):** H1b conditions not only on `cur`'s origin **time** (disclosed in
  §5) but also on `cur`'s eventual **direction** (high-for-down / low-for-up), which is unknowable
  at the origin. H1b is non-causal calibration context, never verdict-bearing, and must not be
  cited as a fair causal comparison to H1a.
- **A3 (enforcement):** §3's "context cells never verdict-bearing" is now enforced in code: the
  1d/1w/1M cells emit the status marker `context_only` (NOT a §6 verdict) regardless of pair
  count; the §6 verdict family applies to the 4h primary cell alone.
- **A4 (enforcement):** §4.3's third exclusion — `cur` anchors outside the loaded candle window —
  is now counted and reported (`cur_outside_candle_window`) instead of silently scoring as MISS
  (which inflated `n_pairs` against §4's included-pairs definition). The results doc must report
  this count per cell and confirm candle coverage vs the facit span (4h facit starts 2017-01).
- **A5 (bookkeeping):** per-cell `(bars, first_ts, last_ts)` are recorded in `summary.json`
  per §3.
- **A6 (infrastructure, sibling commit):** `corpus_manifest._fingerprint` now normalizes CRLF→LF
  before hashing. The committed MANIFEST was generated from an LF checkout; on a pristine Windows
  checkout (`core.autocrlf=true`) the fail-closed verifier false-positived on every TF, which
  would have blocked this probe on the labeling machine. LF-content hashes are unchanged; the
  facit corpus is untouched.

Residual, disclosed, not fixed (review "concerns, low"): §2's motivation circularity (same-corpus
descriptive counts motivated the prereg) — mitigated by H1a being parameter-free, the acceptance
band being locked independently (2026-07-02), and 4h chosen for power, not effect size (1w had
the highest raw link-rate and was *not* made primary). For the sign-off reviewer's attention.

# Pre-registration — Chain-clustering probe (is sequential chaining a *mode* or a per-leg coin flip?)

**Date:** 2026-07-21 · **Line:** Fib SELECTION-LEARNING, sequential axis (follows the SIGNED
[cascade results](btc-fib-cascade-conditioning-probe-results-20260720.md)) · **Status:** registered,
run pending. **Authorization:** owner blanket GO 2026-07-21 ("Jag godkänner redan alla planer och
implementeringar i denna session", autonomous session) — P3-adjacent sequential follow-up
explicitly unblocked. Verdict remains **advisory until owner sign-off**. This registration must
not be edited after the first run; post-run material goes to a `-results-` sibling.

## 1. Question (one sentence)

Given the signed finding that ~1 in 4 origins chains to the previous endpoint, do chained pairs
**cluster in sequence** (runs of consecutive chains beyond what the marginal rate predicts —
a "cascade mode") or is chaining serially independent?

## 2. Motivation (disclosed, pre-run)

- The signed cascade probe measured the *marginal* chain rate (4h H1a = 0.256) but said nothing
  about serial structure. The owner's self-report U1 ("nästa rena impuls i **sekvensen**")
  describes a *sustained* cascade — which predicts clustering, not independent per-leg chaining.
- Modeling consequence (pre-stated): clustering → sequential conditioning should be state-aware
  (a latent "in-cascade" regime); independence → a per-leg feature suffices. This directly shapes
  the sequential-conditioning selection feature (separate prereg).
- Motivation uses only the *signed aggregate* (0.256), not any peeking at run structure. No
  descriptive run-statistics were computed on the corpus before this registration.

## 3. Corpus and data (LOCKED)

`data/labels/human_fib/MANIFEST.json`: 1M=13, 1w=24, 1d=76, 4h=371 (484). The run MUST call
`corpus_manifest.verify_manifest()` and abort on drift. Candle cache: fresh 2026-07-21 fetch
(`config/settings.expansion.yaml`; 4h = 21 273 bars 2016-11-05 → 2026-07-21). Disclosed: this
cache has 4 more trailing bars than the signed run's; the signed probe reproduces **exactly**
on it (verified 2026-07-21 pre-registration: H1a 0.256, null 0.005, CI [0.205, 0.298], all
cells identical), so the trailing bars are inert for pair construction.

**Primary cell: 4h** (only powered TF). Context cells: 1d, 1w (reported, never verdict-bearing).
1M is dropped (12 pairs, nothing in the signed probe).

## 4. Sequence construction (frozen)

1. Pairs and exclusions exactly as the signed probe (`cascade_conditioning.build_pairs`
   unchanged: order by `anchor_a.time`; predecessor = latest `anchor_b.time ≤ cur.anchor_a.time`;
   degenerate/no-predecessor/outside-window excluded and counted).
2. Chain indicator `c_i ∈ {0,1}` per included pair `i` = the signed probe's H1a hit at the LOCKED
   band (`ACCEPT_AT = NEAR`, `classify_anchor(is_origin=True)`, unchanged).
3. The sequence `c_1 … c_N` is ordered by `cur.anchor_a.time` (ties as in pair construction).

## 5. Hypotheses and null (frozen)

- **H2a (PRIMARY — adjacency):** statistic `A = Σ 1[c_i = 1 ∧ c_{i+1} = 1]` (count of adjacent
  chained pairs). Null **N3**: uniform random permutation of the `c` sequence (marginal count
  preserved exactly; serial order destroyed). Deterministic seed **20260721**, `n_perm = 2000`.
  One-sided p = fraction of permutations with `A_perm ≥ A_obs`.
- **H2b (SECONDARY, reported with CI, not verdict-bearing):** Markov gap
  `Δ = P̂(c_{i+1}=1 | c_i=1) − P̂(c_{i+1}=1 | c_i=0)`, with the same permutation null providing
  its reference distribution and a pair-resample bootstrap (B=2000, seed 20260721) CI on Δ.
- **Descriptive (reported, never verdict-bearing):** run-length distribution of 1-runs vs the
  permutation-null expectation; longest run; direction pattern within chained pairs
  (continuation `prev.direction == cur.direction` vs reversal); inter-leg gap in bars
  (`cur.a_bar − prev.b_bar`) for chained vs unchained pairs.

## 6. Statistics and verdict family (frozen — 4h cell only)

- **`chain_clustering`** — H2a one-sided permutation `p < 0.05`.
- **`no_chain_clustering`** — otherwise, with ≥ 50 included pairs.
- **`inconclusive_underpowered`** — fewer than 50 pairs (not expected on 4h).

Context cells emit `context_only`. No other verdict may be reported.

## 7. Non-claims (binding)

No edge / behaviour / backtest / PnL / Genesis claim. No model trained. No facit created, edited,
or promoted; no auto-fib; 1H/ETH untouched. A positive verdict means only: *chained selections
cluster serially on this corpus* — it does not identify the mechanism (regime, trend state, or
labeling-session artifacts are all compatible; the labeling-session confound is disclosed:
legs drawn in one sitting may share chain style. Sensitivity: H2a recomputed excluding pairs
whose two legs have `created_at` on different labeling days is **reported**, not verdict-bearing).

## 8. Run protocol

New module `research/chain_clustering.py` (own CLI `--probe`; no code added to byte-capped
modules), reusing `cascade_conditioning`'s pair construction and hit scoring verbatim. Summary →
`experiments/review/chain_clustering/summary.json` (gitignored/regenerable). Results doc:
`btc-fib-chain-clustering-probe-results-20260721.md`, advisory pending owner sign-off.
Harness to be reviewed by `leakage-validity-reviewer` **before** the first run; any findings
become §9 pre-run amendments.

## 9. Pre-run amendments (2026-07-21, leakage-validity review — **no run has occurred**)

The harness was reviewed by the `leakage-validity-reviewer` before any execution. Review
verdict: H2a leakage-clean and prereg-faithful on statistics/seeds/verdict strings, but two
blocking findings, both fixed pre-run. §1–§8 otherwise unchanged.

- **A1 (blocking, fixed — hub-coupling confound guard):** the flat adjacency statistic does not
  require pair `i`'s `cur` to be pair `i+1`'s `prev`. The reviewer measured on the committed
  facit (structure only, no hits computed): 4h has 362 adjacent slots of which only 294 (81 %)
  are true single-file transitions, and 42 of the 68 non-single-file slots share the **same**
  `prev` leg — two consecutive pairs then test the *same* candidate anchor, which can inflate
  adjacency mechanically (an "attractive reusable origin", not a cascade mode). Fix (locked
  before run): the **positive verdict now requires BOTH** the full-array adjacency `A` **and**
  the single-file-restricted adjacency `A_sf` (slots with `pairs[i].cur is pairs[i+1].prev`;
  mask fixed under permutation — slot structure is exogenous) to reject the null at p < 0.05.
  Hub diagnostics (`n_adjacent_slots`, `n_single_file`, `n_hub_shared_prev`) are reported per
  cell. §7 non-claims extended: hub-reuse (a reusable origin serving several unrelated legs)
  is a named compatible mechanism for full-array-only excess adjacency.
- **A2 (blocking, fixed — exclusion accounting):** the in-window filter silently dropped pairs
  without counting them, diverging from §4.1's "exactly as the signed probe" (whose A4
  introduced the counted `cur_outside_candle_window` category). Fixed:
  `filter_in_window` counts the exclusion; expected 0 on the full-coverage cache (verified
  against the signed run's per-cell zeros).
- **A3 (review concern, addressed):** the statistics layer had unit tests but the
  I/O/exclusion bookkeeping had none — an integration test on synthetic legs now asserts the
  three-category exclusion accounting and the single-file mask construction.

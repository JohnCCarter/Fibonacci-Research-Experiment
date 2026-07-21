# Pre-registration — Sequential-conditioning selection feature (`chained_origin`)

**Date:** 2026-07-21 · **Line:** Fib SELECTION-LEARNING, sequential axis (follows the SIGNED
[cascade result](btc-fib-cascade-conditioning-probe-results-20260720.md) and the
[chain-clustering probe](btc-fib-chain-clustering-probe-results-20260721.md), whose locked
consequence was: *per-leg feature, no regime model*) · **Status:** registered, run pending.
**Authorization:** owner blanket GO 2026-07-21 (autonomous session). Verdict **advisory until
owner sign-off**. No edits after the first run; post-run material goes to a `-results-` sibling.

## 1. Question (one sentence)

Does a causal per-leg feature — *does this candidate leg's origin sit on the endpoint of the
most recently completed human leg?* — add out-of-sample ranking signal for reproducing human
selection at the live k=3 viewport, over the identical model without it?

## 2. Teacher-forcing disclosure (BINDING — constrains every claim from this study)

The feature conditions on the human's **own prior selections** (facit legs completed before the
candidate's origin). Facit was drawn in hindsight (2026 labeling sessions over 2016–2026
charts): the "predecessor" was not causally available to any live system — it is available in a
**teacher-forced** evaluation of *reproduction* ("given his previous fibs, is his next one more
predictable?"), which is the north-star question (selection learning), NOT a live-trading
pipeline. Every claim must carry this frame. The price-derived features (cleanliness etc.)
remain causal-from-price; `chained_origin` is causal-from-past-facit. A positive verdict says:
*sequential conditioning on prior human fibs improves reproduction of the next selection* —
nothing about live availability, edge, or behaviour.

## 3. Corpus, data, cells (LOCKED)

Manifest-verified corpus (fail-closed): 1M=13, 1w=24, 1d=76, 4h=371 (484). Candle cache:
frozen 2026-07-21 fetch (`config/settings.expansion.yaml`; 4h 21 273 bars). **Primary cell:
4h k=3** (the only powered TF). Context cell: 1d (reported, never verdict-bearing). 1w/1M
skipped (nothing sequential at 1M in the signed probe; 1w N=23). **Snapshot discipline:** all
comparisons are computed within this run on this snapshot; no cross-run comparison to the
pre-growth Stage-2 headline numbers (0.0567 era) is valid or will be made.

## 4. Candidate universe and rows (frozen)

Candidate build mirrors the Stage-2 causal build **verbatim in logic** (per-endpoint truncated
re-detect at `anchor_b + k`, ≤ 12 prior opposite pivots per endpoint, ε-match labels: 3 bars /
0.5×ATR(14) both anchors + direction) — re-implemented in `research/selection_sequential.py`
solely because the byte-capped `selection_learning.py` `Candidate` does not carry the start
pivot's price/kind, which the sequential feature needs. Purged/embargoed split verbatim
(`window_of`, reach=k, train_frac=0.70). Base features: `live_feature_names(3)` =
{cleanliness, duration, magnitude, prominence, structure_alignment}.

## 5. Feature and models (frozen)

- **Predecessor of a candidate** (mirrors the signed probe's §4.2 on the bar axis): the human
  leg with the latest `anchor_b` bar position ≤ the candidate's **start** bar position
  (equality allowed — exact chains count; ties: latest `anchor_a` bar, then fib_id). Legs
  completed *after* the candidate's origin never qualify (the candidate's own matching leg is
  structurally excluded: its endpoint is the candidate's endpoint).
- **`chained_origin` (PRIMARY, binary, parameter-free):** 1 iff a predecessor exists AND the
  candidate's start anchor reaches the LOCKED acceptance origin band vs the predecessor's
  endpoint (`classify_anchor(start_price, pred_b_price, is_origin=True, pred_bar=start_pos,
  true_bar=pred_b_pos) >= ACCEPT_AT`); else 0. Band locked 2026-07-02, untouched.
- **`chain_prox` (SECONDARY variant, reported, never verdict-bearing):** `1/(1 + bar_dist)`
  where `bar_dist = |start_pos − pred_b_pos|` (0 if no predecessor).
- **Models:** ridge logistic (Stage-2 `fit_logreg`, unchanged hyperparameters, seed 20260721
  for bootstrap only — the fit is deterministic). **BASE** = live features (§4). **ENHANCED** =
  BASE + `chained_origin`. Identical rows, identical split, identical standardization pipeline.

## 6. Statistic and verdict family (frozen — 4h cell only)

Primary: OOS test AP(ENHANCED) − AP(BASE), decision-point cluster bootstrap (B=2000, seed
20260721) CI and one-sided p (lift ≤ 0). Powered gate: ≥ 10 test positives (Stage-2 §9 floor).

- **`sequential_feature_signal`** — CI95 excludes 0 from below.
- **`sequential_feature_worse`** — CI95 excludes 0 from above (the enrichment-study precedent).
- **`no_sequential_feature_signal`** — otherwise, powered.
- **`inconclusive_underpowered`** — < 10 test positives.

Sensitivities (reported, never verdict-bearing): ENHANCED with `chain_prox` instead of the
binary; `chained_origin`'s standardized model weight; AP(`chained_origin` alone) vs
AP(magnitude); chained-rate among test positives vs test negatives. Context cell 1d emits
`context_only`.

## 7. Non-claims (binding)

No edge / behaviour / backtest / PnL / Genesis claim. No live-availability claim (§2). No
facit creation/edit/promotion; no auto-fib; no cascade data model; 1H/ETH untouched. A
positive verdict does NOT mean selection is solved — the signed cascade bound is ~26 % chained
origins; this tests whether that component converts into *incremental ranking signal* on top
of the geometric features, under teacher forcing.

## 8. Run protocol

New module `research/selection_sequential.py` (own CLI `--sequential`; no bytes into capped
modules). Deterministic; needs cached candles, never fetches; manifest-verified fail-closed.
Summary → `experiments/review/selection_sequential/summary.json` (gitignored/regenerable).
Expected runtime hours (per-endpoint truncated re-detect, Stage-2 cost class; run in
background with progress logging). Results doc `btc-fib-sequential-feature-results-<date>.md`,
advisory pending owner sign-off. Harness reviewed by `leakage-validity-reviewer` **before**
the first run; findings become §9 pre-run amendments.

## 9. Pre-run amendments (2026-07-21, leakage-validity review — **no run has occurred**)

The harness was reviewed by the `leakage-validity-reviewer` (two passes) before any execution.
Blocking findings fixed pre-run; §1–§8 otherwise unchanged.

- **A1 (blocking, fixed — self-leg leakage at the short-leg edge):** §5's claim that the
  candidate's own matching leg is "structurally excluded" is FALSE at the ε edge: `_matches_human`
  tolerates `|end.index − b_pos| ≤ 3`, so a short human leg's endpoint can sit at/before the
  candidate's start while still being its label match — the feature would then be computed
  against the label's own endpoint. **Locked label-blind rule:** a leg qualifies as predecessor
  only if `b_pos ≤ start_pos` **AND** `b_pos < anchor_b_pos − eps_time_bars`. Label-blind
  (candidate geometry only) so positives and negatives get identically defined features; a leg
  able to ε-match the candidate's endpoint can never be its predecessor. Disclosed cost:
  genuinely-chained candidates of total length ≤ ε bars lose their predecessor (rare); the count
  of candidates whose nearest unrestricted predecessor was banned is reported
  (`predecessor_rule_exclusions`).
- **A2 (blocking, disclosure lock — test-window teacher-forcing):** test-period features
  condition on **all** facit legs completed before the candidate's origin — *including
  test-period legs* (an earlier test-window selection feeding a later test candidate). This is
  the deliberate teacher-forced autoregressive design; it is NOT a "clean OOS" claim in the
  naive sense, and every verdict string must be read under §2 + this amendment.
- **A3 (blocking, fixed — owner-classified misclick legs excluded):** the 7 same-candle
  degenerate fibs (owner sign-off 2026-07-21: **misclicks**, home-GUI fix pending; 6 on 4h,
  1 on 1d) are excluded from THIS STUDY entirely (`nondegenerate_legs`): they may neither
  serve as label-match targets nor as predecessors (a known-erroneous endpoint must not act
  as "the human's previous selection"). Study-level exclusion, disclosed count
  (`n_degenerate_legs_excluded`); no facit mutation; note this diverges deliberately from the
  signed cascade probe (which allowed degenerates as predecessors — it predates the owner's
  misclick classification).
- **A4:** `prom_max` from the mirrored build is deliberately omitted (prominence-family
  baselines are not part of §6) — commented in code so the diff is not read as drift.
- **A5 (multiplicity disclosure):** this is the **third** sequential-axis test on the same
  484-fib snapshot (after the signed cascade probe and the chain-clustering probe). Each has
  its own locked prereg and distinct question; the results doc must carry this disclosure.
- **A6:** `inference=None` (degenerate bootstrap) on a powered cell reports
  `no_sequential_feature_signal` plus an explicit `meta:` note — never silently.
- **A7 (tie-break clarification):** duplicate predecessor `b_pos` ties resolve to the largest
  `(a_pos, load-order key)` in the sorted pool — i.e. latest `anchor_a`, then latest load
  order (§5's "then fib_id" made concrete).

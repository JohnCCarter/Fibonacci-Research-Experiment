# 2026-06-05 Fib Fingerprint × Outcome Research Checkpoint

Checkpoint after building the fib research stack (#22 + #23 + join + triage) and a
data-expansion run. This is a status snapshot, not a conclusion about edge.

## Checkpoint

- **#22 implemented** — `fib_candidate_outcomes`: forward outcome metrics per
  event × horizon from human-fib `*_events.json`.
- **#23 implemented** — `fib_level_fingerprints`: deterministic pre/at/post
  interaction features per human-fib event.
- **Join implemented** — `fib_fingerprint_outcomes`: #22 + #23 merged on `event_id`.
- **Triage implemented** — `fib_toplist`: candidate summary, fingerprint↔outcome
  hints, `--compare-to` multi-run inventory/stability.
- **Expanded run completed** — `fp_outcomes_20260605T115819Z`: **51 → 1148 events**
  (4592 rows) via `config/settings.expansion.yaml` (window from 2016-11-05), same
  method/thresholds.
- **No stable fingerprint/outcome relationship found yet** — with 22× more data,
  every baseline fingerprint↔mfe co-occurrence WEAKENED or sign-flipped.
- **Previous small-N watch signals were likely artifacts** — e.g. `post_retest_count`
  (watch at n≤3) dropped to weak; `post_bars_on_break_side` rho 0.67 → 0.14 with flip.

## Proven (mechanics work)

- Pipeline runs end-to-end (events → candles → fingerprints + outcomes).
- Join works (1148 events, 4592 rows, 0 unmatched).
- Fingerprint layer works (pre/at/post features extracted, 0 skipped on expanded run).
- Toplist / compare work (ranked buckets, sample inventory, stability deltas).
- Candidate / fingerprint / outcome separation holds (layers stay distinct per row;
  human fib remains facit, `*_candidate` is never promoted).

## Not proven (no claims)

- **No edge** — nothing here demonstrates a tradeable advantage.
- **No stable candidate signal** — outcome distributions per candidate not shown to
  be consistent.
- **No stable fingerprint yet** — no fingerprint field survived the data expansion.
- **No trading logic** — and none intended in this track.

## Recommended next research step

1. Analyze the **80 buckets that reached n≥20** in the expanded run
   (`sample_inventory.csv`, filter `reached_20=True`).
2. Check whether *anything* is consistent across **candidate × level × timeframe ×
   horizon** (currently single timeframe `1d`, so cross-TF is pending more data).
3. If nothing stable emerges, **mark this track `working pipeline, no evidence yet`**
   and stop adding analysis until more events exist (BTC pre-2016 + SOL pre-2022 1d
   need a network refetch before they can join).

## Artifacts

- Expanded run: `experiments/runs/fib_fingerprint_outcomes/2026-06-05/fp_outcomes_20260605T115819Z/`
  - `MULTIRUN_NOTES.md`, `sample_inventory.csv`, `toplist.csv`, `TOPLIST_NOTES.md`
- Baseline run: `…/fp_outcomes_20260605T114206Z/`
- Docs: [FIB_FINGERPRINT_OUTCOMES.md](../../FIB_FINGERPRINT_OUTCOMES.md),
  [FIB_CANDIDATE_OUTCOMES.md](../../FIB_CANDIDATE_OUTCOMES.md),
  [FIB_LEVEL_FINGERPRINTS.md](../../FIB_LEVEL_FINGERPRINTS.md)

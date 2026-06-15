# Wiki reviews (superseded)

Descriptive review pages from the **pre-BTC-monthly** research track were archived
on 2026-06-08. They are **not** current evidence.

**Location:** [archive/research_superseded/2026-06-08_pre_btc_monthly_reset/wiki_reviews/](../../../archive/research_superseded/2026-06-08_pre_btc_monthly_reset/wiki_reviews/)

| File | Theme |
|------|--------|
| `2026-06-05-fib-n20-bucket-review.md` | 1D-only n≥20 buckets |
| `2026-06-05-fib-fingerprint-outcome-checkpoint.md` | Fingerprint × outcome |
| `2026-06-05-mtf-fib-projection-checkpoint.md` | MTF 1W→1D/4H |
| `2026-06-05-mtf-clean-forward-n20-review.md` | Clean-forward 4H cohort |
| `2026-06-05-eth-1d-human-fib-smoke.md` | ETH smoke (#15) |

**Active protocol:** [BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md](../../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)

## Active BTC/USD Review Pages

| File | Description |
|------|-------------|
| [btc-1m-reaction-review-cycle-20260611.md](btc-1m-reaction-review-cycle-20260611.md) | All 9 BTC/USD 1M source fibs — 1D + 4H reaction review, approved 2026-06-11 |
| [fib-tooling-ecosystem-scan-20260615.md](fib-tooling-ecosystem-scan-20260615.md) | Issue #32 tooling/ecosystem scan — inventory-only; top-3 ROI: HTML gallery, review ledger, overlap detector |
| [ledgers/README.md](ledgers/README.md) | Source-quality review ledgers (machine-trackable verdicts) — Issue #32 top-ROI #2 |
| [btc-4h-overlap-candidates-20260615.md](btc-4h-overlap-candidates-20260615.md) | 4H overlap/near-duplicate candidates (report-only) — Issue #32 top-ROI #3 |
| [btc-4h-fib-20171228-correction-20260615.md](btc-4h-fib-20171228-correction-20260615.md) | 20171228 anchor_a correction (preview-first flow) — candidate_1 applied |
| [chart-regression-strategy-20260615.md](chart-regression-strategy-20260615.md) | Chart regression strategy spike (#32 evaluate-later) — structural-first, defer pixel |
| [btc-4h-fib-20250506-dedup-20260615.md](btc-4h-fib-20250506-dedup-20260615.md) | 20250506 dedup — fib A superseded, fib B retained (active 4H 366→365) |
| [btc-source-fib-next-research-plan-20260615.md](btc-source-fib-next-research-plan-20260615.md) | Next research-pass design (read-only) — recommends corpus integrity report (#2) now, MTF confluence atlas (#1) next |
| [btc-source-fib-corpus-integrity-20260615.md](btc-source-fib-corpus-integrity-20260615.md) | Corpus integrity capstone (read-only) — counts 9/21/67/365, conventions, source-quality state, known caveats; corpus declared clean. Next: MTF confluence atlas |
| [btc-mtf-confluence-table-20260615.md](btc-mtf-confluence-table-20260615.md) | MTF confluence atlas CP1 (read-only) — 222 cross-TF level clusters at epsilon_log=0.005 (2×4-TF); GO to CP2 sensitivity. `research/mtf_confluence.py` (stdlib) + CSV |
| [btc-mtf-confluence-sensitivity-20260615.md](btc-mtf-confluence-sensitivity-20260615.md) | MTF confluence CP2 (read-only) — epsilon sensitivity (0.0025/0.005/0.01) + fixed-band vs single-linkage. c001 robust 4-TF; c002 chaining-dependent; chaining 14%→26%. Conditional GO to CP3 visual atlas. Summary CSV |
| [btc-mtf-confluence-atlas-cp3-c001-20260615.md](btc-mtf-confluence-atlas-cp3-c001-20260615.md) | MTF confluence atlas CP3 slice 1 — c001 card (fixed-band, ε=0.005, 1d backdrop). **Human-approved 2026-06-15** (title dedup + member table polish). `research/mtf_confluence_atlas.py` (stdlib + mpl); signature-resolved, fail-closed; PNGs gitignored |
| [btc-mtf-confluence-atlas-cp3-c002-20260615.md](btc-mtf-confluence-atlas-cp3-c002-20260615.md) | MTF confluence atlas CP3 slice 2 — c002 **contrast** card (single-linkage, ε=0.005, span 0.00627 > ε → chaining-dependent; dissolves under fixed-band). Never labelled tight 4-TF. Member-reconstruction tolerance fix (c001 unchanged). **Human-approved 2026-06-15.** |
| [btc-mtf-confluence-atlas-cp3-zero-span-20260615.md](btc-mtf-confluence-atlas-cp3-zero-span-20260615.md) | MTF confluence atlas CP3 slice 3 — **zero-span** 3-TF cards c004/c006/c007 (fixed-band, span=0, exact-price at ~\$64829/\$13764/\$9085). CP2 labels → shifting positional ids (c002/c003/c004); signature-resolved. out_dir keyed on stable label. **Human-approved 2026-06-15.** |
| [btc-mtf-confluence-atlas-cp3-20260615.md](btc-mtf-confluence-atlas-cp3-20260615.md) | MTF confluence atlas CP3 **capstone** — first visual-atlas pack closed. 5 cards across 3 archetypes (c001 robust fixed-band 4-TF; c002 chaining-dependent single-linkage contrast; c004/c006/c007 zero-span exact-price 3-TF), **all human-approved 2026-06-15**. Caveats (positional ids, signature selection, geometry-not-edge); next decision = stop here or later expand fixed-band only. No PNGs committed. |
| [btc-mtf-confluence-interpretation-decision-20260615.md](btc-mtf-confluence-interpretation-decision-20260615.md) | MTF confluence **interpretation & decision note** — synthesis of CP1–CP3 (Observed/Inferred/Unverified) + 5 decision options. Finding: MTF confluence exists as geometry, not edge proof. **Recommendation: stop the MTF track here**; don't expand cards or start a behaviour study yet; next active decision = pause Fib or open a new track with one falsifiable question. Docs-only. |
| [btc-fib-to-genesis-v2-phase0-prereg-20260615.md](btc-fib-to-genesis-v2-phase0-prereg-20260615.md) | **Phase 0 pre-registration** (docs-only) for a possible Fib → causal-features → Genesis V2 track. Registers one falsifiable behaviour question (price reaction at causal confluence zones vs naïve/placebo levels, OOS), causal-feature rules, leakage manifest, ≥3 baselines (placebo + causal swing = primary), time-split/embargo holdout, neutral success metrics, stop/go. Authorises nothing beyond itself. |

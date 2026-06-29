# BTC Fib Selection-Learning — model-ENRICHMENT RESULTS (leg-completeness) (2026-06-25)

Blind Commit-2 execution of the [enrichment LOCK
(2026-06-24)](btc-fib-selection-learning-enrichment-lock-20260624.md). One pre-specified feature
(`exclusivity` / leg-completeness, E1), one nested comparison vs the current Stage-2 model (E2), one
blind verdict (E4). **No edge / behaviour / PnL / backtest claim** (E7). Harness:
[`selection_learning_enrich.py`](../../../src/fibengine/research/selection_learning_enrich.py)
(commit `c80acb0`); seed `20260618`; frozen-data parity (no `--refresh`); preflight READY before run.

> **Verdict (blind, 4h primary k=3): `enriched_worse_check`.** The enriched model is *significantly
> worse* than current Stage-2 (AP-lift 95% CI entirely below 0). The lock's direction-guard checks
> (parity, no look-ahead, bootstrap unit, power) all pass → **not a bug**. For the north-star this is
> a negative shot: the locked per-leg `exclusivity` feature does **not** add human-like leg-selection
> signal over the model we already have. The per-leg-feature modeling line is **closed**.

## Observed (measured — 4h primary, powered: 65 test positives)

| quantity | value |
|---|---|
| AP baseline (current Stage-2, nested) | **0.056737** |
| AP enriched (Stage-2 + `exclusivity`) | **0.038744** |
| AP-lift (point) | **−0.017993** |
| AP-lift bootstrap mean | −0.023651 |
| **AP-lift 95% CI** | **[−0.070026, −0.001895]** (excludes 0, below) |
| p(lift ≤ 0), one-sided | 0.994 |
| bootstrap | decision-point cluster by `anchor_b`, 2000 resamples, 2071 groups |
| ROC-AUC enriched (secondary) | 0.9252 |
| `corr(exclusivity, cleanliness)` (train) | **0.804** |
| `exclusivity` standardized weight | +0.1142 (`cleanliness` +0.1502 still leads) |
| n_candidates / n_train / n_test | 86244 / 61368 / 24852 |
| rows excluded (endpoint beyond data / not reconstructible) | 0 / 0 |
| `exclusivity` dist | mean 0.275, std 0.345, frac@0 0.497, frac@1 0.093 |

**Parity gate (proves the nested baseline IS the current model):** `ap_baseline_stage2` =
**0.056737** = the Stage-2 headline **0.0567**; `n_test_positives` = **65**, matching Stage-2.
*Spec-reconciliation:* the pre-run note "n_candidates ≈ 24852" was a label mix-up — **24852 = n_test**;
the full candidate universe is **86244** (= Stage-2's universe). Substantive parity holds.
`rows_excluded = 0` confirms every row reconstructs causally (no look-ahead, no endpoint dropped).

**Context cells (underpowered, never refuted — E3 power floor ≥10 positives):**

| TF | test pos | AP base | AP enr | lift | note |
|---|---|---|---|---|---|
| 1M | 5 | 0.2636 | 0.2789 | +0.0153 | underpowered; corr 0.878 |
| 1w | 0 | — | — | — | no positives |
| 1d | 7 | 0.1617 | 0.1599 | −0.0018 | underpowered; corr 0.808 |

Context is reported for completeness only; the verdict rests solely on the 4h powered cell (E3/E4).

## Inferred (interpretation — not measured)

- **The locked `exclusivity` definition does not enrich the current model.** A negative powered lift
  with CI excluding 0 means the 6th feature does not help and, as fit, costs net OOS ranking power.
- **Most likely mechanism (reported per E1, *not* a reason to discount the verdict): collinearity.**
  `corr(exclusivity, cleanliness) = 0.804` on train — `exclusivity` is largely a `cleanliness` proxy.
  Adding a near-collinear, noisier regressor on only 65 test positives plausibly inflates variance and
  drags pooled test AP down. This is a *mechanism*, not grounds to soften the blind result.
- **North-star read:** this closes the per-leg-feature line cleanly. The locked honest prior was low
  (four per-leg features already ~0 at k=3; only `cleanliness` stuck); the shot confirms the per-leg
  approach has hit its ceiling on this corpus. The binding constraint is now **data, not features**.
- **Lock-routing nuance:** E8 pre-committed `no_enrichment_signal → grow the facit`. The realized
  branch is `enriched_worse_check`, whose *substantive* north-star implication is the same (per-leg
  features do not beat Stage-2 → grow the facit), but the **direction choice is not pre-committed** for
  this branch — it is surfaced to the user (see handoff Next Step).

## Unverified (open — would need a NEW lock)

- Whether a **decorrelated / residualized** exclusivity (orthogonalized vs `cleanliness`) carries any
  orthogonal signal. This is a **different feature needing its own Commit-1 lock**, not a continuation
  of this one — and the prior is **low** (if the 0.80-collinear version's residual hurt here, the
  orthogonal component is small). Not a free natural next step; reopening a closed line.
- The `cleanliness`-as-genuine-signal crux stays **OPEN** (E7) — this shot does not resolve it.
- Absolute reproduction of human selection remains capped by the ~0.83 coverage ceiling (E7); no
  edge / behaviour / PnL / Genesis / auto-fib-as-truth / label-mutation claim is made or implied.

## Artifacts

- Summary JSON: `experiments/review/fib_selection_learning/enrich/summary.json` (**gitignored**).
- Per-cell checkpoints: `experiments/review/fib_selection_learning/enrich/cells/*.json` (**gitignored**).
- Harness + tests: `selection_learning_enrich.py`,
  `tests/research/test_selection_learning_enrich.py` (commit `c80acb0`; gates green — 601 pass, 74% cov).

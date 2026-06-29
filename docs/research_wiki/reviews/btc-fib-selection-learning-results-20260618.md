# BTC Fib Selection-Learning — Stage 2 Headline RUN (2026-06-18)

**Lean Fib Research. Research-only. Selection learning — NOT a behaviour/edge claim, no
backtest/PnL, no Genesis, no auto-fib-as-truth, no label mutation.** This reports the **first run**
of the pre-registered **Stage 2 headline cell** (live-equivalent viewport, primary `k = 3`), built
per the [prereg](btc-fib-selection-learning-prereg-20260617.md) +
[§12 addendum](btc-fib-selection-learning-addendum-20260618.md) (metric pinned A5.1, blind).

> **STATUS (updated 2026-06-18, prominence-sensitivity + k-sweep done): a MODEST, largely
> single-feature (`cleanliness`) lead on the one powered cell (4h) that SURVIVES the §6 prominence
> family AND is STABLE across the confirmation-buffer sweep `k ∈ {0,3,6,12}` — but is NOT a
> reproduction of human selection, and no edge/behaviour claim.** The 4h AP-lift is robustly
> positive out-of-sample vs **all three** §6 baselines — magnitude (CI `[0.023, 0.120]`), summed
> prominence A (`[0.018, 0.104]`), and max prominence B (`[0.021, 0.116]`); every CI excludes 0,
> 0/2000 resamples ≤ 0. Pre-committed verdict: **`survives_prominence_family`**. The k-sweep cross-k
> verdict is **`k_stable_live_selection_signal`** (k=3/6/12 all powered and survive the locked
> baseline family; k=0 is degenerate/uninterpretable, excluded). The interpretable weights (§10) are
> essentially unchanged across k — the lift is carried **almost entirely by `cleanliness`**
> (standardized 0.20); at `k=12` `scale_confluence` enters as a **secondary hint** (0.13) once it is
> causally available, but does not displace `cleanliness`. Human-marked legs are *cleaner/more
> efficient*, a single coherent correlate, **not** a multi-feature reproduction. Absolute AP
> 0.057–0.066 against a 0.83 coverage ceiling = low agreement; **the human is not "reproduced".**
> 1M/1w/1d are **underpowered, not refuted**.

## What was built + run

`src/fibengine/research/selection_learning.py` (+ 15 tests). Stage 2 only: candidate legs from
`detect_pivots` + opposite-pivot pairing; **causal** features computed on a frame **truncated at
`anchor_b + k`** with the live `k*≤3` whitelist (`{magnitude, cleanliness, duration, prominence,
structure_alignment}`); the candidate universe re-detected on the truncated frame; ε-matching to
human legs (`time_tol=3` bars, `price_tol=0.5` ATR, A4); purged/embargoed split on `anchor_b` chart
time (embargo = forward reach `k`); interpretable ridge logistic regression (numpy, deterministic,
zero new deps); **baseline parity** = same test set/viewport, ranked by `magnitude` alone (§6).
Primary metric = pooled test **Average Precision** (A5.1); ROC-AUC secondary.

Run: `--timeframes 1M,1w,1d,4h --config config/settings.expansion.yaml`, seed 20260618.

## Results (point estimates)

| TF | human legs | coverage | n_test cands | test pos | AP model | AP base | AP lift | AUC (2nd) | powered (≥10) |
|----|-----------:|---------:|-------------:|---------:|---------:|--------:|--------:|----------:|:-------------:|
| 1M | 9 | 1.00 | 132 | 5 | 0.264 | 0.047 | +0.216 | 0.883 | no |
| 1w | 21 | 0.857 | 768 | 0 | — | — | — | — | no |
| 1d | 67 | 0.896 | 4 140 | 7 | 0.162 | 0.003 | +0.159 | 0.908 | no |
| **4h** | **365** | **0.830** | **24 852** | **65** | **0.057** | **0.005** | **+0.052** | **0.914** | **yes** |

- **Only 4h is powered** (65 test positives; 1M/1d thin, 1w has 0 test positives after the
  purged split — mirrors B-1, where only 4h/1d cleared the power floor).
- On 4h the positive base rate is ≈ `65 / 24 852 ≈ 0.0026`. Baseline AP `0.0051` ≈ 2× base rate
  (magnitude alone is weak); model AP `0.057` ≈ **22× base rate, ≈ 11× baseline**.
- **Secondary AUC ≈ 0.88–0.91 on every TF with positives** — the most consistent signal: the
  ranking separates human-matched legs from the rest far above chance (0.5) across 1M/1d/4h.

## AP-lift inference (4h, done 2026-06-18)

**Method (pre-declared in the prior commit before computing the p):** decision-point cluster
bootstrap — resample whole `anchor_b` groups with replacement (2071 groups), re-pool their
candidates, recompute `AP(model) − AP(magnitude)` on the **held-fixed** trained model (no refit; this
measures the OOS test-estimate's sampling variability), 2000 resamples, seed 20260618. Row-level
bootstrap would understate variance because candidates cluster by decision point.

- **Lift (test point estimate) = +0.0516**; bootstrap mean +0.0592.
- **95% CI = [0.0234, 0.1197] — excludes 0**; `p_one_sided(lift ≤ 0) = 0/2000`.
- **Read this as a bootstrap-stability statement** (the lift is robustly > 0 across decision-point
  resamples), **not** a permutation-null p-value (it is not "p<0.0005 under H₀ of no association").

### Learned weights (§10 interpretability — read before claiming)

Standardized logistic weights (4h): `cleanliness 0.203`, `prominence 0.071`, `duration −0.040`,
`magnitude 0.013`, `structure_alignment −0.002`. **`cleanliness` dominates (~3× the next term);
`structure_alignment` ≈ 0.** So the lift over magnitude is a **single coherent correlate** — human
legs are *cleaner / more efficient* (net move ÷ path) than magnitude alone predicts — **not** a
multi-feature "reproduction of human selection."

## Prominence-baseline sensitivity (4h, done 2026-06-18)

§6 lists the trivial-leg baseline as "largest-magnitude / **most-prominent**". The headline pinned
**magnitude**; this sensitivity tests whether the lift survives the stronger **prominence** family.
**Both instantiations + the verdict rule were locked before the run** (not chosen after): **A** =
summed endpoint prominence (= the `prominence` feature column, rank-equivalent to the raw sum);
**B** = max endpoint prominence. Same candidate universe / viewport / `k=3` / ε / purged split /
held-fixed model — only the baseline ranking rule differs.

| §6 baseline | AP | model AP-lift | bootstrap 95% CI | excludes 0? |
|-------------|---:|--------------:|------------------|:-----------:|
| magnitude | 0.0051 | +0.0516 | [0.023, 0.120] | yes |
| **prominence A (summed)** | 0.0138 | **+0.0430** | **[0.018, 0.104]** | **yes** |
| **prominence B (max)** | 0.0079 | **+0.0488** | **[0.021, 0.116]** | **yes** |

- **Sanity:** both prominence baselines (A 0.0138, B 0.0079) beat the magnitude baseline (0.0051) —
  prominence *is* the stronger trivial rule, as expected. The model still beats both.
- Bootstrap stability: `0/2000` resamples ≤ 0 for A and B.
- **Pre-committed verdict = `survives_prominence_family`** (lift > 0 with CI excluding 0 vs **both**
  A and B). The earlier cleanliness lift is **not** a magnitude-baseline artifact, and **not** a
  prominence artifact either.
- Weights unchanged (model held fixed): `cleanliness` still carries the lift (0.20).

## k-sweep sensitivity (4h, done 2026-06-18)

The addendum (§A5) mandates a confirmation-buffer sweep so the headline `k=3` is not a forking-paths
artifact. Live-only sensitivity over `k ∈ {0,3,6,12}`; **verdict rule locked before the run** — a `k`
cell *survives* only if it is **powered AND** its model AP-lift CI excludes 0 vs **every** causally
allowed §6 baseline (the locked prominence-FAMILY criterion, magnitude required). Cross-k verdict:
`k_stable_live_selection_signal` if ≥2 cells survive.

| k | active features | n_test (pos) | powered | AP model | AP-lift vs mag | survives family | verdict |
|--:|-----------------|-------------:|:-------:|---------:|---------------:|:---------------:|---------|
| 0 | mag/clean/dur | 0 (0) | no | — | — | — | degenerate (0 candidates, reachable 0.0) |
| 3 | +prom/struct | 24 852 (65) | yes | 0.0567 | +0.0516 | **yes** | survives_prominence_family |
| 6 | +prom/struct | 24 912 (63) | yes | 0.0582 | +0.0531 | **yes** | survives_prominence_family |
| 12 | +prom/struct/**scale_confl** | 24 888 (63) | yes | 0.0665 | +0.0614 | **yes** | survives_prominence_family |

- **k=0 is degenerate, not a null:** with zero confirmation buffer no bars exist after `anchor_b`, so
  the candidate universe is empty (`reachable_fraction = 0.0`, unpowered). Expected; excluded from the
  verdict — **not interpretable as a result.**
- **k=3/6/12 all survive** the locked family (CI excludes 0 vs magnitude *and* both prominence
  baselines; `p_one_sided(lift≤0) = 0/2000` throughout). Lowest CI floor across all cells/baselines:
  `k=12` vs prominence-sum `ci95_low = 0.025`; `k=3` vs prominence-sum `ci95_low = 0.018`.
- **Cross-k verdict = `k_stable_live_selection_signal`** (3 of 3 powered cells survive; ≥2 required).
  The lead is **not** an artifact of one narrow confirmation buffer.
- **Modest framing (unchanged):** `cleanliness` still dominates the weights at every powered k (~0.20).
  At `k=12` `scale_confluence` becomes causally available and enters at ~0.13 — a **secondary hint**,
  not a second pillar; `cleanliness` still carries the lift. AP rises only modestly (0.057 → 0.066)
  and stays far under the 0.83 coverage ceiling: **still a single-feature lead, still not a
  reproduction, still no edge/behaviour claim.**

## Observed / Inferred / Unverified

- **Observed (verified):** the numbers above; the 4h AP-lift is robustly positive vs **all three**
  §6 baselines (magnitude + prominence A + prominence B; every CI excludes 0); `cleanliness` carries
  the lift; pipeline causal; 19 unit tests green.
- **Inferred:** beyond leg size *and* leg prominence, the human's leg choice on 4h tracks **leg
  cleanliness/efficiency** out-of-sample. 4h is the only adequately powered cell.
- **Unverified / scope limits (do not claim past these):**
  1. **Largely a single feature** (`cleanliness`) → a robust lead, not a structural confirmation;
     could still be a mechanical correlate of how clean legs are detected/anchored.
  2. **Low absolute agreement** (AP 0.057, capped by the 0.83 coverage ceiling) — the human is
     **not** reproduced.
  3. 1M/1w/1d are **underpowered, not refuted.**
  4. No edge/behaviour/PnL meaning — this is selection imitation only.

## Next steps (NONE started; each needs a separate explicit GO)

- `k`-sweep {0,3,6,12} — **DONE** (above) → `k_stable_live_selection_signal`.
- **Retrospective `W` / causal-availability gap (4h)** — compare the live-equivalent viewport against
  a bounded retrospective viewport to measure the right-edge/context gap. **Candidate track, not
  started.**
- **Stage-1 per-pivot diagnostic** — whether endpoint/pivot selection is itself learnable.
  **Candidate track, not started.**
- Set-level **exclusivity** output diagnostic; optional probe of whether the `cleanliness` lead is a
  detection/anchoring artifact (the open interpretive question).
- **No W/gap, no Stage 1, no new sensitivity, and no Genesis may be started automatically — each
  requires a separate explicit GO.**

## Discipline honoured

No edge/behaviour claim, no backtest/PnL, no Genesis, no 1H, no auto-fib-as-truth, no label/corpus
mutation, no tuning on test (all knobs frozen pre-run in the addendum). Artifacts
(`experiments/review/fib_selection_learning/summary.json` + `…/k_sweep/summary.json`) are
**gitignored**, regenerable. Code + tests committed `ea6c2ea` (gates green: ruff/format/bounds/544
pytest, cov 75.52%).

> A modest, largely single-feature (cleanliness) lead on one powered cell — statistically robust
> vs the magnitude AND prominence (A/B) baselines, but not a reproduction of human selection and no
> edge/behaviour claim.

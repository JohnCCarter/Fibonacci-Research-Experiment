# BTC Fib Selection-Learning — Stage-1 per-pivot diagnostic RESULTS (2026-06-24)

**Lean Fib Research. Research-only. Selection learning — NOT a behaviour/edge claim, no
backtest/PnL, no Genesis, no auto-fib-as-truth, no label mutation.** First (and only) run of the
**Stage-1 per-pivot diagnostic floor**, executed exactly per the
[Stage-1 LOCK](btc-fib-selection-learning-stage1-lock-20260624.md) (label a/b-pooled S1,
decision-point + `k*`-gating S2/S3, per-pivot feature subset S4, prominence baseline S5,
structural-chunk bootstrap S6, **verdict rule S7 fixed blind before any per-pivot value existed**).
Builds on the closed [W-gap study](btc-fib-selection-learning-w-gap-results-20260623.md)
(`no_causal_gap`) and the [Stage-2 / k-sweep results](btc-fib-selection-learning-results-20260618.md).

> **STATUS — VERDICT `no_pivot_signal_above_prominence` (4h primary, `k = 3`).** Stage-1 decomposes
> the Stage-2 agreement ceiling into its two halves, and they answer differently:
> **(1) DETECTION/COVERAGE is NOT the bottleneck** — detection-recall **= 0.902** at the 4h headline
> cell (90 % of human anchors, a/b pooled, sit within ε of a detected pivot). **(2) RANKING/SELECTION
> adds nothing significant beyond raw prominence** — per-pivot ranking lift **= +0.0228, 95 % CI
> [−0.0354, +0.0790] includes 0** (one-sided `p(lift ≤ 0) = 0.22`). Powered (117 test positives ≥ 10),
> `R = 0.902 ≥ 0.50`, CI includes 0 → per S7 this is **`no_pivot_signal_above_prominence`**: given the
> detector's universe, the **lone pivot** carries no OOS ranking signal over prominence at the live
> `k=3` buffer. **Sensitivity (honest, not buried):** at `k = 12` — where `scale_confluence` (a
> wider-frame, `k*=12` feature) is admitted — the lift rises to **+0.0690, CI [+0.0029, +0.1335]
> excludes 0** (`p = 0.0205`). That is **not** the locked primary (k=3 is) and does **not** change the
> verdict; it says higher-degree confluence helps rank anchors *at a 12-bar buffer*, consistent with
> W-gap's "right-edge feature" attribution. **No reproduction, no edge/behaviour claim** (S8 binding).

## What was built + run

**New module** `src/fibengine/research/selection_learning_stage1.py` (own `--stage1` /
`--stage1-preflight` CLI; **no code added to the byte-capped `selection_learning.py`**, per S9) +
`tests/research/test_selection_learning_stage1.py` (12 tests). Per cell `k`: the **live universe** is
**re-detected per pivot on the frame truncated at `pivot_index + max(k, fractal_n)`** (`fractal_n = 1`
frozen), so a pivot's *existence* is never look-ahead; features are **`k*`-gated** (a feature enters
only when `k*(f) ≤ k`). The per-pivot feature subset is the definitional reduction of the frozen eight:
`{prominence (k*=3), structure_alignment (k*=3), scale_confluence (k*=12)}` as live inputs,
`round_number` interaction-only, `recency` dropped — **the four leg/set-level features
(`magnitude`, `cleanliness`, `duration`, `exclusivity`) are structurally undefined on a single pivot
and EXCLUDED by construction.** Label = pivot within ε (3 bars / 0.5 causal-ATR) of **any** human
anchor (`anchor_a` **or** `anchor_b`, role pooled). Baseline = detector `prominence` ranking on the
same truncated viewport. Bootstrap = 2000-resample **structural-chunk cluster** (consecutive runs of
`structure_window = 6` base pivots — the A3 segmentation, **not** row-level), seed `20260618`.

Run: `--stage1 --config config/settings.expansion.yaml`, on the **frozen** data universe (no
`data.fetch --refresh`; `--stage1-preflight` READY confirmed before the run). Per-cell checkpointed,
deterministic, resume-safe.

## Results — coverage (detection-recall) reported SEPARATELY from ranking (lift), per S6

**4h (primary, powered ≥ 10 test positives):**

| k | live feats | n_test (pos) | **recall `R`** (COVERAGE) | AP model | AP prom | **lift** (RANKING) | 95 % CI | p(lift≤0) |
|--:|-----------|-------------:|:---------:|--------:|--------:|--------:|--------|---------:|
| 0 | — | — | — | — | — | **DEGENERATE** (empty usable feature/baseline set; excluded from verdict, S3) | — | — |
| **3** | prom, struct | 2071 (117) | **0.902** | 0.2301 | 0.2073 | **+0.0228** | **[−0.0354, +0.0790]** | 0.217 |
| 6 | prom, struct | 2076 (116) | 0.900 | 0.2306 | 0.2080 | +0.0227 | [−0.0356, +0.0858] | 0.220 |
| 12 | + **scale_confl** | 2074 (116) | 0.900 | 0.2770 | 0.2080 | **+0.0690** | **[+0.0029, +0.1335]** | 0.0205 |

**Context (1M/1w/1d, k=3 — coverage strong throughout; ranking context only, NOT refuted, S6/S8):**

| TF | n_test (pos) | recall `R` | AP model | AP prom | lift | 95 % CI | powered |
|----|-------------:|:---------:|--------:|--------:|-----:|---------|:-------:|
| 1M | 11 (9) | 1.000 | 0.989 | 0.963 | +0.026 | — | no (9 < 10) |
| 1w | 64 (1) | 0.941 | 0.063 | 0.250 | −0.188 | — | no (1 < 10) |
| 1d | 345 (12) | 0.926 | 0.120 | 0.282 | −0.162 | [−0.494, +0.031] | yes |

- **Detection-recall is high at EVERY cell** (0.90–1.00) — the detector's pivot universe **does**
  contain ~90 %+ of the human anchors at every TF. **Coverage is not the bottleneck** (`R ≥ 0.50`
  comfortably; the `detector_coverage_limited` guard does **not** fire).
- **Ranking lift is null-or-negative wherever powered at `k=3`:** 4h CI includes 0 (+0.0228); the 1d
  context cell is *also* powered (12 test pos) and its lift point estimate is **negative** (−0.162, CI
  [−0.494, +0.031] still includes 0) — i.e. the lone-pivot model does **not** beat prominence on 1d
  either. Both powered `k=3` cells agree: **no per-pivot ranking signal above prominence.** (1d is a
  context TF, not the locked primary — reported as reinforcing context, not as a second headline.)
- 1M/1w carry **no inferential weight** (9 / 1 test positives < 10); reported for completeness.

## Coverage vs ranking — the diagnostic decomposition (the point of Stage-1)

Stage-1 was built to split the Stage-2 ceiling (AP ~0.057 against a ~0.83 leg-reachability ceiling)
into **detection** vs **selection**. The split is unambiguous:

- **Detection / coverage half:** `R = 0.902` on 4h. The human's chosen extremes are **overwhelmingly
  present** in the detector's pivot universe. The Stage-2 ceiling is **not** a raw-detection failure at
  the anchor level. *(Note the unit difference — S-resolution #2 below — this 0.90 is per-anchor /
  a-b-pooled / single-pivot, structurally easier than Stage-2's ~0.83 per-leg two-endpoint
  reconstruction, so the two ceilings are not the same number and are not meant to be.)*
- **Ranking / selection half:** lift CI includes 0 at `k=3`. **Given** the anchors are in the universe,
  the per-pivot features available live (`prominence`, `structure_alignment`) do **not** distinguish
  human anchors from other prominent pivots beyond what raw prominence already does.
- **Therefore (Inferred, scoped):** the Stage-2 agreement ceiling is a **selection / gestalt** problem,
  **not** a coverage problem. The signal the human uses to pick *which* prominent extreme to anchor
  does **not** live in the lone pivot's per-pivot features at the live buffer — consistent with the
  Stage-2 finding that the lead came from the **leg-level** `cleanliness`, which is **structurally
  absent** from Stage-1 (S4). A null ranking result here is the *expected, publishable* outcome the lock
  pre-stated, not a surprise.

## S7 verdict (pre-stated, falsifiable — applied verbatim)

Primary = 4h `k = 3`: powered (117 ≥ 10) ✓, `R = 0.902 ≥ 0.50` ✓, lift 95 % CI **[−0.0354, +0.0790]
includes 0** → **`no_pivot_signal_above_prominence`** (matches `summary.json` `stage1_verdict`).

- `inconclusive_underpowered` — does not fire (4h powered).
- `detector_coverage_limited` — does **not** fire (`R = 0.902 ≫ 0.50`).
- `pivot_selection_learnable` — does **not** fire at k=3 (CI does not exclude 0 above).
- `artifact_check_needed` (direction guard) — does **not** fire (CI upper +0.0790 ≥ 0; prominence does
  not *significantly* beat the model).
- **k=12 sensitivity** (CI excludes 0 above) is **not** the locked primary and does **not** override the
  k=3 verdict; it is reported as a buffer-dependent, wider-frame note (see below), not a `learnable`
  finding.

## k=12 sensitivity (honest scope note, not buried)

At `k = 12` the `scale_confluence` feature (`k*=12`) becomes live and the lift jumps to **+0.0690, CI
[+0.0029, +0.1335]** (`p = 0.0205`; standardized weight `scale_confluence = 0.365`, second only to
`prominence = 0.534`). Read carefully: this is a **12-bar confirmation buffer**, well past the `k=3`
headline, and `scale_confluence` is precisely the **wider-frame / right-edge** feature the
[W-gap study](btc-fib-selection-learning-w-gap-results-20260623.md) flagged as borderline at k=12. So
the Stage-1 k=12 lift and the W-gap k=12 caveat are the **same phenomenon from two angles**: higher-
degree confluence does carry some anchor-ranking information, but only at a buffer that the live
headline (`k=3`) does not grant. It sharpens — does **not** contradict — the `no_pivot_signal_above_
prominence` headline: *at the live buffer the lone pivot adds nothing; only a wider confirmation window
lets a multi-scale feature help.*

## Two build-time resolutions (documented per the lock's "halt-and-report" discipline)

Neither touched a locked decision point (label, k*-gating, feature subset, baseline, bootstrap unit,
coverage-vs-ranking split, non-claims), so the run proceeded; both are recorded for honesty:

1. **`structure_alignment` direction mapping.** The frozen `structure_alignment(pivots, index, window,
   direction)` needs a direction; per pivot we map `direction = "up"` for a `high` pivot and `"down"`
   for a `low` (the pivot *is* the extreme of its own kind). This is the **conservative** choice: a
   wrong mapping would inject **noise** into the feature → bias the lift **toward the null**, never
   toward a false `learnable`. It cannot manufacture signal.
2. **Detection-recall is per-anchor / full-frame**, a **different unit** from Stage-2's ~0.83 per-leg
   leg-reachability (called out above). Stage-1 recall counts a human anchor as covered if *any*
   detected pivot lands within ε of it (a/b pooled); Stage-2 needed *both* endpoints to reconstruct a
   leg. The higher Stage-1 number (~0.90) is therefore expected and is **not** a re-measurement of the
   Stage-2 ceiling — it is the coverage half of the decomposition, reported on its own axis (S6).

## Observed / Inferred / Unverified

- **Observed (verified):** the numbers above; 4h `k=3` recall = 0.902, lift = +0.0228, CI [−0.0354,
  +0.0790], p = 0.217; both powered `k=3` cells (4h, 1d) have lift CI including 0; `k=12` lift CI
  excludes 0 above (+0.0029); detection-recall ≥ 0.90 at every cell; pipeline causal (per-pivot
  re-detect on truncated frame, `k*`-gating, train-only standardization, purged split, structural-chunk
  bootstrap); 12 new unit tests green; run deterministic and resume-safe; `k=0` degenerate as locked.
- **Inferred (scoped to 4h / these features):** the Stage-2 agreement ceiling is a **selection /
  gestalt** limitation, **not** a detection-coverage one — human anchors are in the detector's universe
  (~90 %), but the **lone pivot's** live per-pivot features carry no OOS ranking advantage over raw
  prominence. The human's "which extreme" signal lives at the **leg level** (the structurally-absent
  `cleanliness`), not the single pivot.
- **Unverified / scope limits (do not claim past these):**
  1. **Only 4h is the locked powered primary**; 1d is incidentally powered (reinforcing context), 1M/1w
     underpowered (9 / 1 positives) — **context, not refuted.**
  2. **A null ranking lift is NOT reproduction** (S8): absolute AP stays ~0.23 model / ~0.21 prominence,
     and the coverage ceiling (R ≈ 0.90) caps interpretation, not 1.0.
  3. **k=12 is a buffer-dependent sensitivity**, not the headline; `scale_confluence` helps only at a
     12-bar confirmation window the live k=3 view does not grant.
  4. Stage-1 **cannot** resolve the `cleanliness`-as-artifact question — that feature is structurally
     absent here. It stays an **open** non-claim (S8).

## Non-claims (S8 binding — what this must NOT be read as)

Not a reproduction of human selection (a learnable/non-learnable *pivot* ≠ a reproduced *leg* — the
gestalt is Stage-2). **No edge / behaviour / PnL / backtest / strategy claim.** "Beats / does not beat
prominence" is only the narrow OOS per-pivot ranking statement. The `cleanliness`-as-artifact /
detection-anchoring question stays **OPEN** — Stage-1 does not test it. Underpowered TFs are context,
not refuted. No Genesis, no auto-fib-as-truth, no label/corpus mutation, no 1H, no ETH, no tuning on
test, no `data.fetch --refresh` (frozen-data parity — same universe as Stage-2 / W-gap).

## Discipline honoured

Verdict rule S7 fixed **blind** in the 2026-06-24 lock (commit `00a97d7`) before any per-pivot value
was computed; applied verbatim. All knobs frozen pre-run (ε, k-sweep, features, baseline, bootstrap,
seed). Frozen-data parity held (no `--refresh`; preflight READY). Coverage reported **separately** from
ranking throughout (S6). Two build-time resolutions documented, neither on a locked decision point.
Artifacts (`experiments/review/fib_selection_learning/stage1/summary.json` + `…/cells/*.json`) are
**gitignored**, regenerable.

> Stage-1 splits the Stage-2 ceiling cleanly: **detection is not the problem** (recall ≈ 0.90), but the
> **lone pivot carries no ranking signal over prominence** at the live `k=3` buffer (lift CI includes
> 0) → **`no_pivot_signal_above_prominence`**. The human's selection signal lives in the leg gestalt,
> not the single pivot. Only a wider `k=12` confirmation window lets a multi-scale feature help — a
> sensitivity note, not the headline. Not a reproduction; no edge/behaviour claim.

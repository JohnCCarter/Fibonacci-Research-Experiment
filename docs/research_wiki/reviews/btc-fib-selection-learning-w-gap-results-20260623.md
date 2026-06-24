# BTC Fib Selection-Learning — Retrospective `W` / causal-availability-gap RESULTS (2026-06-23)

**Lean Fib Research. Research-only. Selection learning — NOT a behaviour/edge claim, no
backtest/PnL, no Genesis, no auto-fib-as-truth, no label mutation.** First (and only) run of
side-quest #1, executed exactly per the
[W-gap LOCK](btc-fib-selection-learning-w-gap-lock-20260622.md) (gap metric L1, same-row +
embargo-`W` parity L2, bootstrap L3, cells L4, **verdict rule L5 fixed blind before any gap value
existed**). Builds on the [Stage-2 / k-sweep results](btc-fib-selection-learning-results-20260618.md).

> **STATUS — VERDICT `no_causal_gap` (4h primary).** On the one powered cell (4h), the
> bounded-retrospective `W` model does **not** beat the live-equivalent model at the headline buffer
> `k = 3`: **gap(k=3) = −0.0045, 95% CI [−0.070, +0.031] includes 0** (one-sided `p(gap ≤ 0) =
> 0.61`). The point estimate is **negative at every `k`** (live ≥ retro): k=6 = −0.0041
> `[−0.064, +0.032]`, k=12 = −0.0131 `[−0.036, +0.0004]`. No gap CI excludes 0 **above** anywhere, so
> there is **no evidence the live view at `k=3` lacks hindsight** the features could exploit. Per L5
> this is `no_causal_gap`. **Caveat (honest, scope-limit):** the k=12 CI upper bound sits a whisker
> above 0 (+0.0004; `p(gap ≤ 0) = 0.97`), i.e. live *nearly significantly* beats retro there — driven
> by `gap_from_wider_frame = −0.0092` (recomputing shared features on the wider `W` frame slightly
> **hurts** the retro model), exactly the modeling-artifact direction the L5 guard names. It does
> **not** cross into `artifact_check_needed` (no CI upper bound < 0) and does **not** change the
> primary `k=3` verdict, but it is reported as a sensitivity note, not buried. **No reproduction, no
> edge/behaviour claim** (L6 binding).

## What was built + run

`src/fibengine/research/selection_learning_gap.py` (gap study) + `selection_learning.py` (`--w-gap`
CLI). Per cell `k`: the **live-equivalent-at-`k` universe** is re-detected on the frame truncated at
`anchor_b + k` (identical to the k-sweep); the **retrospective `W` model** scores **those same rows**,
differing only in features computed over the bounded `W` viewport (all eight, `recency` in its locked
viewport-relative form `leg / (W + leg)`, L9). **Common embargo = `W` bars** applied to **both** models
(L2). Models trained once per cell, **held fixed** through a 2000-resample decision-point cluster
bootstrap, seed `20260618` (L3). Rows where a live-`k` candidate cannot be reconstructed on `df_W`
(endpoint `anchor_b + W` past the data) are **excluded from BOTH** models — no imputation (L9).

Run: `--w-gap --config config/settings.expansion.yaml`, seed `20260618`, on the **frozen** k-sweep
data universe (no `data.fetch --refresh`; `--w-gap-preflight` READY confirmed before the run). Full
run ≈ 3.5 h, per-cell checkpointed; deterministic (`gap(k=3) = −0.00448` reproduces exactly).

## Results — gap(k) = AP(retro `W`) − AP(live-`k`), identical rows (point estimates)

**4h (primary, powered ≥ 10 test positives):**

| k | active live feats | n_test (pos) | AP live | AP retro | **gap** | 95% CI | p(gap≤0) | excl rows/pos |
|--:|-------------------|-------------:|--------:|---------:|--------:|--------|---------:|--------------:|
| **3** | +prom/struct | 24 168 (61) | 0.0600 | 0.0555 | **−0.0045** | **[−0.070, +0.031]** | 0.61 | 684 / 4 |
| 6 | +prom/struct | 24 252 (61) | 0.0596 | 0.0554 | −0.0041 | [−0.064, +0.032] | 0.59 | 660 / 2 |
| 12 | +prom/struct/**scale_confl** | 24 252 (61) | 0.0685 | 0.0554 | −0.0131 | [−0.036, +0.0004] | 0.97 | 636 / 2 |

**Context (1M/1w/1d, k=3 — UNDERPOWERED, < 10 test positives → context only, NOT refuted, L4):**

| TF | n_test (pos) | AP live | AP retro | gap | powered |
|----|-------------:|--------:|---------:|----:|:-------:|
| 1M | 48 (2) | 0.583 | 0.643 | +0.060 | no |
| 1w | 528 (0) | — | — | — | no |
| 1d | 3 672 (7) | 0.163 | 0.080 | −0.084 | no |

- **Only 4h is powered** (61 test positives each cell; mirrors the k-sweep — 1M/1d thin, 1w has 0
  test positives after the purged split). The context rows carry **no inferential weight**: 1M gap
  rests on 2 positives, 1d on 7; reported for completeness, not interpreted.
- **Row exclusions are trivial** (684/86 244 ≈ **0.8 %** of live rows at k=3; ≤ 4 positives per cell).
  Per L9 this is a non-issue, **not** a scope-limiting artifact — well below any "non-trivial" bar.

## Per-feature gap attribution (descriptive, fixed pre-output per L9 — no new claim)

| k | gap_from_wider_frame | gap_from_right_edge | right-edge-only feats |
|--:|---------------------:|--------------------:|-----------------------|
| 3 | 0.000 | −0.0045 | recency, scale_confluence |
| 6 | 0.000 | −0.0041 | recency, scale_confluence |
| 12 | **−0.0092** | −0.0038 | recency |

- At **k=3/6** the entire (small, negative) gap is from the **right-edge-only** features — admitting
  `recency` + `scale_confluence` on the `W` frame **slightly hurts** the retro model rather than
  helping it. There is no hidden hindsight advantage waiting to be unlocked.
- At **k=12** `scale_confluence` is already causally live, so right-edge-only = `recency` alone; the
  larger (still negative) gap comes mostly from **recomputing shared features on the wider `W` frame**
  (`−0.0092`). This is the "viewport-relative `recency` / wider frame hurting the retrospective model"
  the L5 direction guard anticipates — consistent with `no_causal_gap`, not against it.
- **Retro standardized weights** (k=3): `cleanliness 0.166`, `scale_confluence 0.130`, `recency
  −0.120`, `prominence 0.057`, `magnitude 0.024`. `recency` enters **negative** — the bounded-`W`
  retrospective view gives the human-leg signal **no** net lift over the live view. `cleanliness`
  still dominates, unchanged from the headline.

## L5 verdict (pre-stated, falsifiable — applied verbatim)

- gap(k=3) 95% CI **[−0.070, +0.031] includes 0** → **`no_causal_gap`**. The live model at the
  headline buffer `k=3` already matches the bounded-retrospective model; selection (as captured by
  these features) needs **no hindsight beyond `k=3`**.
- Direction guard (`artifact_check_needed`): triggers only if a gap CI **upper bound < 0** (live
  *significantly* > retro). k=3/6/12 upper bounds are +0.031 / +0.032 / **+0.0004** — all ≥ 0, so the
  guard does **not** fire. k=12 is borderline (reported above as a sensitivity caveat).
- `gap_closes_with_buffer` / `gap_persists` both require gap(k=3) CI to **exclude 0 above** — it does
  not, so neither applies. Verdict locked: **`no_causal_gap`** (matches `summary.json` `gap_verdict`).

## Observed / Inferred / Unverified

- **Observed (verified):** the numbers above; on 4h every gap point estimate is ≤ 0 and every 95% CI
  includes 0 (none excludes 0 above); `gap(k=3) = −0.0045`, CI [−0.070, +0.031], p=0.61; pipeline
  causal (embargo=`W` both sides, identical rows, models held fixed); 557 unit tests green incl. new
  gap/checkpoint tests; run deterministic and resume-safe.
- **Inferred:** at the 4h scale, the **right-edge / look-ahead information gap is not material** — the
  live-equivalent view at `k=3` captures as much of the human's leg-selection signal (via these
  features) as a bounded 180-bar retrospective view does. The cleanliness lead from the headline is a
  **live-available** correlate, not a hindsight artifact.
- **Unverified / scope limits (do not claim past these):**
  1. **4h only is powered**; 1M/1w/1d are **underpowered, not refuted** (2/0/7 test positives).
  2. **k=12 is borderline** (CI upper +0.0004, p=0.97 that live ≥ retro) — a hair from the direction
     guard; attributed to the wider-frame recompute, reported not interpreted.
  3. A zero gap is **not** reproduction (L6): absolute AP stays ~0.057, capped by the ~0.83 coverage
     ceiling — low agreement throughout.
  4. The internal live AP here (0.060 at k=3) is recomputed under **embargo=`W`** and differs from the
     headline's embargo=`k` AP (0.057) **by design** (L1/L2) — the two are not meant to be identical.

## Non-claims (L6 binding — what this must NOT be read as)

Not a reproduction of human selection. **No edge / behaviour / PnL / backtest / strategy claim** — a
zero gap says only that the *label* needs no hindsight beyond `k=3` to be modeled this well; it says
**nothing** about tradeable information (the behaviour line is closed NULL). `cleanliness`-as-artifact
stays an open non-claim. "Any swept cell beats baseline" is not a valid claim (B-1 forking-paths).
No Genesis, no auto-fib-as-truth, no label/corpus mutation, no 1H, no ETH.

## Discipline honoured

Verdict rule L5 fixed **blind** in the 2026-06-22 lock before any gap value was computed; applied
verbatim. No tuning on test (all knobs frozen pre-run). Frozen-data parity held (no `--refresh`;
preflight READY). Artifacts (`experiments/review/fib_selection_learning/w_gap/summary.json` +
`…/cells/*.json`) are **gitignored**, regenerable. Gates green: ruff + ruff-format + 557 pytest
(cov 74.83 %) + repo-bounds.

> On the only powered cell (4h), a bounded 180-bar retrospective view buys **no** selection
> information the live view at `k=3` lacks — gap(k=3) = −0.0045, CI includes 0, verdict
> **`no_causal_gap`**. Not a reproduction; no edge/behaviour claim.

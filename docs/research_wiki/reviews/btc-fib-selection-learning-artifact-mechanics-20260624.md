# BTC Fib Selection-Learning — artifact-probe MECHANICS NOTE (2026-06-24)

**Lean Fib Research. Research-only. DESCRIPTIVE-ONLY — NO verdict, NO claim, no edge/behaviour/PnL/
backtest/Genesis/auto-fib/1H/ETH/label-mutation.** Executed per the blind
[mechanics PLAN](btc-fib-selection-learning-artifact-mechanics-plan-20260624.md) (`70174df`) on the
**same frozen data / locked detection** as the
[artifact-probe](btc-fib-selection-learning-artifact-results-20260624.md) (no refresh, no new
universe, no matched-null). It explains the *mechanics* behind the three artifact-probe observations;
**it issues no verdict, changes no lock, and the artifact-probe reading is unchanged.** A clean
mechanical explanation of a gap is **not** evidence for or against "genuine human signal" — the crux
stays OPEN.

> **STATUS — descriptive mechanics, no verdict.** (1) The 4H "reached legs less clean than unreached"
> gap is **fully accounted for by leg span (duration)**: cleanliness falls steeply with span
> (Spearman **−0.69**), reached legs are longer (median 5 vs 3 bars), and the −0.056 gap **vanishes
> when conditioning on span** (short-span gap +0.003, long-span gap −0.017). It is a **composition /
> Simpson-flavoured** effect, not a property of "being reached". (2) 4H snapping **lowers** cleanliness
> because detector pivots mostly sit **outside** the human anchors → snapping **extends** the span
> (extend 33% vs shrink 1.6%) → more path. (3) The **1D sign flip** is the genuine cross-TF asymmetry:
> 1D snaps shrink far more often (10% vs 1.6%) **and** the span-delta→cleanliness relationship itself
> **flips sign** (Spearman 4H −0.19 vs 1D +0.18) — so the flip is **not** purely arithmetic; the deeper
> "why the local relationship reverses by TF" stays an **open investigate-target**, claimed as nothing.

## What was built + run

A small descriptive pass: `src/fibengine/research/selection_learning_artifact_mechanics.py` (own
`--artifact-mechanics` CLI) records three per-leg quantities on the artifact-probe rows —
`span_bars = |pos_b − pos_a|`, `magnitude_atr` (net close-move ÷ causal ATR at `anchor_b`),
`snap_span_delta = |snapped span| − |exact span|` — and the PLAN-P3 summaries (median/IQR, a single
Spearman, a single median split). **Numpy-only, deterministic, no bootstrap, no verdict.** Three new
descriptive fields were added to `ArtifactRow` (used by no contrast/verdict). Run on the frozen
universe (preflight READY; no `--refresh`).

## M1 — 4H "reached less clean" is a span (duration) confound

| quantity | reached (n=314) | unreached (n=51) |
|----------|----------------:|-----------------:|
| `span_bars` median (IQR) | 5.0 (2–11) | 3.0 (2–6) |
| `magnitude_atr` median (IQR) | — see summary.json — | — |
| Spearman(`cleanliness`, `span_bars`), all legs | **−0.686** | |
| Spearman(`cleanliness`, `magnitude_atr`), all legs | −0.322 | |

**Attenuation (single median split on `span_bars`):**

| span half | n reached / unreached | mean clean reached | mean clean unreached | **gap** |
|-----------|----------------------:|-------------------:|---------------------:|--------:|
| short-span | 170 / 38 | 0.864 | 0.861 | **+0.003** |
| long-span | 144 / 13 | 0.600 | 0.617 | **−0.017** |

- Cleanliness falls **steeply with span** (−0.69). Unreached legs cluster in the **short-span** bucket
  (38/51 ≈ 75%) where cleanliness is high (~0.86); reached legs spread into the **long-span** bucket
  (~46%) where it is low (~0.60). The overall −0.056 surfacing gap is that **composition** — **within
  each span half the gap is ≈0** (+0.003 / −0.017). So "reached legs are less clean" is **"reached legs
  are longer"**, not a detector preference for clean legs.
- This matches the artifact-probe's `inverse_surfacing` direction and its **marginal** magnitude (CI
  upper −0.00095): there is no real surfacing-by-cleanliness effect to explain — just the span confound.

## M3 — the 4H↔1D snapping sign flip (cross-TF asymmetry; the headline object)

| TF | `snap_span_delta`: extend (>0) | no change (=0) | shrink (<0) | Spearman(`snap_span_delta`, `snapped−exact`) † |
|----|----:|----:|----:|----:|
| **4H** | **0.328** | 0.656 | **0.016** | **−0.193** |
| 1D | 0.233 | 0.667 | **0.100** | **+0.180** |
| 1w | 0.211 | 0.737 | 0.053 | −0.057 |
| 1M | 0.667 | 0.333 | 0.000 | +0.165 |

† the bare span-delta↔cleanliness Spearman is **partly arithmetic** (changing the span changes
`net/path` mechanically) — shown for completeness, **not** the finding.

- **4H is extension-dominated** (extend 33% vs shrink **1.6%**, ≈20:1): detector pivots sit at the
  fuller swing extremes, the human anchors **inside** them, so snapping extends the span → more path →
  cleanliness **down** (consistent with the locked `snapping_deflates`).
- **1D has far more shrinking** (10% vs 1.6%) **and** the span-delta→cleanliness relationship **flips
  sign** (+0.18 vs −0.19). That sign flip is the genuinely non-trivial fact (not pure arithmetic): on
  1D, where detector pivots land relative to the local price path differs — **detector granularity vs
  human-anchoring precision differs by TF**. This is enough to explain *that* the artifact-probe's
  snapping contrast flips sign on 1D (it inflates there), **without** claiming a mechanism for the
  reversal — *why* the local relationship reverses stays an **open investigate-target**.

## Population guard (binding — carried from the PLAN)

M1 explains the **reached-vs-unreached** contrast (detector-reached vs detector-missed **human** legs).
This is a **different population** from the Stage-2 cleanliness lead (human-matched vs **non-human**
candidates, both *inside* the detector universe). **"Span explains the reached/unreached gap" does NOT
mean "span explains/dissolves the Stage-2 lead"** — different populations, different (un-made) claim.

## Observed / Inferred / Unverified

- **Observed (verified):** the numbers above; Spearman(clean, span)=−0.686 on 4H; reached span median
  5 vs 3; the surfacing gap collapses within span halves (+0.003 / −0.017); 4H extend:shrink ≈ 33:1.6;
  1D 23:10 with span-delta↔clean Spearman flipping −0.19→+0.18; deterministic; new tests green.
- **Inferred (descriptive, scoped):** the 4H reached-less-clean gap is a **span/duration composition
  confound**; the 4H snapping deflation is **span extension** (pivots outside human anchors); the 1D
  flip is a **TF-dependent geometry** (more shrinking + reversed local relationship).
- **Unverified / scope limits:**
  1. **No verdict, no claim, no lock change** — the artifact-probe reading is unchanged; the crux
     stays OPEN.
  2. **Why the span-delta↔cleanliness relationship reverses by TF** is **not** explained — an open
     investigate-target, claimed as nothing.
  3. M1 does **not** touch the Stage-2 lead (population guard).
  4. 1M/1w surfacing carry no weight (0 / 2 unreached); context only.

## Non-claims (binding)

Descriptive consolidation only. **No verdict, no positive claim, no lock change, no reproduction, no
edge/behaviour/PnL/backtest/strategy claim.** Explaining the mechanics of the artifact-probe gaps is
**not** evidence that `cleanliness` is or is not "human intuition" — the crux is unchanged and OPEN. No
matched-null, no new candidate universe, no new model feature, no Genesis, no auto-fib-as-truth, no 1H,
no ETH, no label/corpus mutation, no `data.fetch --refresh`.

> The 4H "reached less clean" gap is **span (duration), not detector cleanliness-preference** — it
> vanishes at equal span. 4H snapping deflates because pivots sit **outside** the human anchors
> (span extends); the 1D flip is a **TF-dependent geometry** (more shrinking + a sign-reversed local
> relationship) whose deeper cause stays an open investigate-target. Descriptive only — no verdict, no
> claim, crux unchanged.

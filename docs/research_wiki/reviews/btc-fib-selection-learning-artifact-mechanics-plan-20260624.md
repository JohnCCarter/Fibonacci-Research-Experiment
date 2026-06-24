# BTC Fib Selection-Learning — artifact-probe MECHANICS investigation PLAN (2026-06-24)

**Lean Fib Research. Research-only. DESCRIPTIVE-ONLY — produces NO verdict, NO claim, no
edge/behaviour/PnL/backtest/Genesis/auto-fib. Docs-only plan (no code/run authorised here).** This is
the small, low-risk **investigate** plan named as door (i) in the
[campaign checkpoint](btc-fib-selection-learning-checkpoint-20260624.md), to explain the *mechanics*
behind the [artifact-probe result](btc-fib-selection-learning-artifact-results-20260624.md)
(`1573b56`). It does **not** test the crux, change any lock, or add any positive claim. Execution
needs a **separate explicit GO**.

## P0. Question (mechanical, descriptive — three observations to explain)

On the artifact-probe's existing frozen data (no refresh):

1. **4H — reached legs are *less* clean than unreached** (0.743 vs 0.799; gap −0.0557).
2. **4H — snapping anchors to detector pivots *lowers* cleanliness** (snapped − exact = −0.0219).
3. **1D — snapping *flips* to inflation** (+0.0222), opposite sign to 4H.

These are already locked as **"investigate, not a finding"** (artifact LOCK A7). This plan asks only
**WHY, mechanically** — it issues **no verdict** and the artifact-probe's reading is unchanged.

## P1. Can it be tested cleanly on existing data? (feasibility — YES, with one caveat)

- **YES, methodically clean.** Every quantity needed is a **deterministic function of the already-frozen
  data + the locked detection** (`anchor_b + k=3`, frozen config) — no new candidate universe, no
  matched-null, no arbitrary frame, no new model feature. It is a **descriptive decomposition** of
  per-leg quantities the artifact-probe already computes internally.
- **Caveat:** it **cannot** be answered from the *existing artifacts* (summary.json holds only
  aggregates — `clean_reached`, `clean_unreached`, the snap gaps). The per-leg quantities (span length,
  magnitude, snapped-vs-exact span) are not persisted. So execution needs a **small descriptive pass**
  that records them — a build+run on the **same frozen data**, low-risk, no new arbitrary choice.

## P2. Mechanical hypotheses (pre-stated — to keep the decomposition honest)

- **M1 (reached less clean = a size/length confound):** the detector reconstructs **larger / longer**
  swings (it needs fractal structure + `min_prominence_atr=0.5`); longer swings carry more intermediate
  retracement → lower `cleanliness`. Unreached legs (detector misses) are shorter/smaller → straighter →
  higher `cleanliness`. Prediction: reached legs have **longer span / larger magnitude**, and the
  (**marginal** — surfacing CI upper was −0.00095) cleanliness gap **attenuates** when conditioning on
  span. *M1 explains a marginal gap; the note must not retroactively harden the surfacing result.*
- **M2 (4H snapping lowers cleanliness):** detector pivots sit at the **fuller** swing extremes; the
  human anchors **inside** them, so snapping **extends** the bar-index span and `cleanliness = net/path`
  drops. **Important — the bare correlation `snap_span_delta ~ (snapped − exact)` is partly arithmetic
  by construction (changing the span changes net/path mechanically), so it is NOT the descriptive
  object.** The genuinely informative, non-trivial fact is **M3's cross-TF asymmetry** below.
- **M3 (the real descriptive object — cross-TF asymmetry in `snap_span_delta`):** on **4H** detector
  pivots systematically sit **outside** the human anchors (`snap_span_delta > 0`, extension lands in
  retracement → cleanliness down); on **1D** they do **not** (`snap_span_delta ≤ 0` → cleanliness up).
  That asymmetry — **detector granularity vs human-anchoring precision differing by TF** — is the real
  content explaining the sign flip, reported as the headline, **not** "span extension lowers
  cleanliness" dressed as a discovery.

## P3. Pre-locked statistics (anti-forking-paths — fixed BEFORE any number)

- **Per-leg quantities (descriptive):** `span_bars = |pos_b − pos_a|`, `magnitude_atr` (net move ÷
  causal ATR at `anchor_b`), `snap_span_delta` (bars), all on the frozen data / locked detection.
- **Reported as:** distributions (median + IQR) for reached vs unreached (M1); a **single Spearman
  correlation** `cleanliness ~ span_bars` and a **single median split** on `span_bars` (M1 attenuation);
  and — the headline — the **per-TF sign + distribution of `snap_span_delta`** to expose the 4H↔1D
  **asymmetry** (M3). The bare `snap_span_delta ~ (snapped − exact)` correlation may be shown for
  completeness but is flagged **partly arithmetic, not the finding**. **Fixed confound set =
  {span_bars, magnitude_atr}** — no tuned bins, no cherry-picked controls.
- **NO bootstrap verdict, NO CI-based decision, NO new locked verdict** — purely descriptive. The output
  is a **mechanics note**, not a result with a verdict.

## P4. Discipline / non-claims (binding)

- **Descriptive-only.** Issues **no verdict**, adds **no positive claim**, and does **not** change the
  artifact-probe reading (still "investigate, not a finding") or any lock.
- Does **not** resolve the cleanliness crux (stays OPEN); a clean mechanical explanation of the gap is
  **not** evidence either for or against "genuine human signal."
- **Population guard (binding):** M1's reached-vs-unreached contrast is detector-**reached** vs
  detector-**missed** human legs — a **different population** from the Stage-2 cleanliness lead
  (human-matched vs non-human candidates, both *inside* the detector universe). "Span explains the
  reached/unreached gap" must **NOT** bleed into "span explains/dissolves the Stage-2 lead" — different
  populations, different (un-made) claim.
- **No matched-null, no new candidate universe, no new model feature, no Genesis, no auto-fib-as-truth,
  no 1H, no ETH, no label/corpus mutation, no `data.fetch --refresh`** (frozen-data parity).

## P5. Execution sketch (Commit 2 — NOT executed here; needs a separate GO)

- A small **descriptive pass** recording per-leg `{span_bars, magnitude_atr, snap_span_delta}` +
  the P3 summaries — either a `--artifact-mechanics` descriptive mode on
  `selection_learning_artifact.py` or a tiny sibling; **no code into byte-capped
  `selection_learning.py`**. Reuses the existing rows / detection / ε / frozen data.
- Tests for the new descriptive quantities; a **mechanics note**
  (`btc-fib-selection-learning-artifact-mechanics-20260624.md`, descriptive, no verdict). Artifacts
  under `experiments/review/fib_selection_learning/artifact/` (**gitignored**).

## P6. What this plan does NOT do

No code, no run, no build, no verdict, no claim, no lock change, no matched-null, no new universe, no
push beyond this plan doc. Execution requires a **separate explicit GO**; **halt and report** if, at
build time, any pre-locked statistic (P3) or the descriptive-only discipline (P4) is found unclear.

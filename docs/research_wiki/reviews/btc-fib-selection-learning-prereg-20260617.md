# BTC Fib Selection-Learning — Pre-registration (2026-06-17)

**Lean Fib Research. DOCS-ONLY — authorises no code, no run, no dependency, no label/corpus change.**
Freezes the *rules* of a new research line before any result. A **separate explicit go** is required
to execute, and the concrete feature list + parameter values are frozen in a **dated addendum
(blind to output) before any build** (§12).

## 0. What this is — and what it is NOT

This is **selection learning**: can a model reproduce **how the human selects significant
swings/ranges** (the fib annotation), from candles? The fib corpus was drawn as **facit for that
selection**, not as an edge claim.

It is **NOT** a behaviour / reaction / backtest study. Whether fib (or generic) levels *repel*
price is a **separate, closed, NULL** question
([behaviour](btc-fib-behaviour-event-study-results-20260616.md),
[B-1 horizontal structure](btc-horizontal-structure-event-study-results-20260617.md)). Those nulls
**do not bear on this question** and this study **makes no edge claim**: a positive result means
"the engine can imitate the human's structural choices," nothing more. **No Genesis, no PnL/backtest,
no strategy sanity-check, no auto-fib-as-truth, no 1H, no ML-hype.**

## 1. Question

> Can an **interpretable** selection model, on candle/structure features, reproduce the human's fib
> selection **out-of-sample better than a structural baseline** — and how large is the **causal
> availability gap** between a *live-equivalent* model and a *bounded retrospective* model?

Null: no lift over the baseline (the human's selection is just the trivial baseline, or is
idiosyncratic/unlearnable). Null is an acceptable, publishable outcome.

## 2. Target and diagnostic unit

A fib is deterministic given `anchor_a`, `anchor_b` (the levels follow). The learnable object is the
**choice of the two swing extremes / the leg between them**.

- **Stage 2 (TARGET): the leg/range gestalt** — the A→B move as a whole. This is the human-correct
  goal: reproduce *which range* the human marked.
- **Stage 1 (diagnostic floor): per-pivot** — "is this swing extreme one the human anchors on?"
  Necessary but **not sufficient**: Stage-2 agreement is upper-bounded by Stage-1 recall (miss an
  endpoint → miss the leg). Report Stage 1 as the diagnostic, **Stage 2 as the headline.**

## 3. Gestalt decomposition (Stage 2) — five components

The leg selection decomposes into measurable sub-choices, **structure first, levels second**:

1. **Scale / significance** — magnitude / level in the structure hierarchy.
2. **Pairing** — which low pairs with which high.
3. **Direction** — up / down (anchor order).
4. **Exclusivity / parsimony** — one leg per structure, not all candidate legs. (Set-level, not
   per-candidate; its exact operationalization — what segments "a structure" — is the soft spot,
   nailed in the §12 addendum.)
5. **Context / HTF structure** — is the move meaningful in larger structure (HTF range, prior
   highs/lows, fractal/nested position, impulse vs noisy sub-leg).

Round numbers / fib ratios are **never primary** — at most **interaction features** that matter only
when they coincide with structure (consistent with the closed ROUND-null).

## 4. Two viewports and the causal-availability gap

The labeling viewport / right-edge is **not recorded** in the corpus (`created_at` exists; no
viewport field). So it is **unknown — measured, not assumed.** Two operationally-defined viewports:

- **Live-equivalent (causal):** features from candles **up to `anchor_b + k`** bars only (the moment
  the leg is confirmable live). `k` = confirmation buffer.
- **Bounded retrospective:** features over a **defined finite window `anchor_b + W`** bars —
  **NOT** to the dataset end, **not omniscient.** This models a *realistic labeling viewport*, not
  infinite hindsight. `W` finite, per-TF, pre-registered.

**Causal-availability gap** = difference in agreement between the two models, **attributed per
feature-group** and **swept over `k` (and `W`)**. A persistent gap at reasonable `k` = genuine
right-edge dependence; a gap that closes as `k`/`W` move = the live cutoff was merely too tight
(see §8). This is the falsifiable operationalisation of the human claim *"I draw historical fibs the
same way I would draw live when the same structure is visible."*

## 5. Feature-provenance rule (binding, structural)

- Every feature carries a tag ∈ {`left-available`, `right-edge-sensitive`}.
- **Fail-closed default:** uncertain availability → `right-edge-sensitive` until proven otherwise.
- **Structural enforcement:** the live-equivalent model is *built from `left-available` features
  only* — gap-candidates are mechanically excluded from its input, not merely "avoided". The
  retrospective model may use all (within its window `W`).
- **Pre-declared provenance table** (feature → tag → rationale) is **frozen in the §12 addendum
  before any build**; no post-hoc re-tagging.

## 6. Baseline (the thing to beat)

- **Stage 1:** the existing fractal-swing detector's **prominence** ranking (default params).
- **Stage 2:** the trivial leg rule (e.g., largest-magnitude / most-prominent low→high in window).
- **Null = the human's selection does not rank above this baseline OOS.**

## 7. Match tolerance ε

A model pivot/leg counts as a hit if within `ε_time` bars and `ε_price` (in ATR units) of the human
anchor(s). ε **absorbs the wick-vs-body anchor-placement convention** (a convention parameter, not a
selection dimension). Pre-specified per TF.

## 8. Parameters swept (pre-registered, before any run)

`k` (confirmation buffer) and `W` (retrospective window) per TF, plus ε. The **`k`-sweep is
mandatory**: it disambiguates *genuine right-edge influence* (gap persists) from *too-tight live
cutoff* (gap closes with small `k`↑), so the human claim is never falsely "convicted" by an
arbitrary cutoff.

**Primary configuration (forking-paths defence — the B-1 lesson).** Exactly **one headline test**
is pre-registered: **Stage 2 + one primary `(k, W, ε)` per TF**, live-equivalent viewport, vs the
§6 baseline. **All other cells** (Stage 1, other `k`/`W`/ε, retrospective) are **secondary /
sensitivity**, or a pre-registered multiplicity correction applies. The primary `(k, W, ε)` values
are fixed in the §12 addendum, blind to output. "Does *any* swept cell beat baseline?" is **not** a
valid claim.

## 9. Out-of-sample + metric

- Split on the leg's **anchor / chart time** (the historical bar time), time-ordered,
  **purged/embargoed** so no leg's feature window straddles the split (López de Prado, *Advances in
  Financial ML* 2018, Ch. 12). **Not** on `created_at` (every label was drawn June 2026 → a
  `created_at` split is meaningless).
- **Primary metric:** OOS agreement — AUC / average-precision (ranking) and/or precision-recall-F1
  (matching), pre-registered as the single primary before running. Report with CIs.
- **Candidate-coverage ceiling (the B-1 power-honesty parallel).** Stage-1's universe is the
  detector's pivots, so any human anchor the detector never surfaces is an automatic miss for model
  **and** baseline — the lift comparison stays valid but **absolute** agreement is capped. Report
  the fraction of human anchors within ε of any candidate; **interpret agreement against that
  ceiling, not 1.0.**

## 10. Model class

**Interpretable only** — logistic regression / the repo's existing `swing_score` with learned
weights. **No deep nets, no Optuna/tuning-on-test.** The point is a transparent, auditable mapping,
not a black box.

## 11. Outputs (when executed)

Selection-learning harness (reads labels + candles), feature-provenance table, agreement numbers per
stage × viewport × `k`/`W`, the causal-availability gap per feature-group. Results report
(`btc-fib-selection-learning-results-YYYYMMDD.md`, Observed / Inferred / Unverified). **No trading
claim. Artifacts gitignored.**

## 12. Execution gate (docs-only; two-step)

1. This prereg freezes the **design, rules, metric, baseline, viewports, provenance discipline,
   guardrails**.
2. A **dated addendum (blind to any output)** freezes the **concrete feature list + provenance tags
   + `k`/`W`/ε values** — **drafted 2026-06-18**:
   [§12 addendum](btc-fib-selection-learning-addendum-20260618.md) (feature `k*`-buffer provenance,
   exclusivity #4 operationalization, `k`/`W`/ε per TF + single primary cell at `k=3`).
3. Execution then requires a **separate explicit go**. Building or running before steps 2–3 is
   unauthorised by this doc.

## 13. Non-goals honoured

Selection learning only. No reaction/behaviour test, no backtest/PnL, no Genesis touch/import/export,
no strategy sanity-check, no 1H, no ML-hype, no parameter tuning on test, no auto-fib promoted to
facit, no label/corpus mutation. Labels are treated as **valid facit, not suspect.** BTC-first.

---

### Evidence discipline

- **Observed:** the corpus stores `anchor_a/b`, `levels`, `created_by`, `created_at`, **no viewport
  field** (verified); the behaviour/B-1 lines closed NULL; a fractal-swing detector + `swing_score`
  exist in the repo.
- **Inferred:** that selection-learning is a distinct question the prior nulls do not close; that the
  five-component gestalt + two-viewport gap operationalise the human claim falsifiably.
- **Unverified / out of scope here:** whether the human's selection is in fact learnable, and how
  large the causal-availability gap is — *that is the study*, gated on §12 and a separate go.

> Docs-only. Authorises no code, no dependency, no run, no source-label change.

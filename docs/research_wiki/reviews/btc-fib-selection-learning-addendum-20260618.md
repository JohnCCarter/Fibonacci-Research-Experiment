# BTC Fib Selection-Learning — §12 Addendum (2026-06-18)

**DOCS-ONLY. Authorises no code, no run, no dependency, no label/corpus change.** This is the dated
**step-2 addendum** required by
[the prereg §12](btc-fib-selection-learning-prereg-20260617.md#12-execution-gate-docs-only-two-step):
it freezes the **concrete feature list + provenance tags + `k`/`W`/ε values** **blind to any
output**, before any build. Execution still needs a **separate explicit go** (§12.3).

**Blindness attestation:** no selection-learning harness exists; no agreement number, AUC, gap, or
sweep result has been produced or seen. Every value below is fixed from the prereg rules, the
existing engine code, and pinned config — **not** from any result.

## A1. Frozen detector / config pins (the universe these features live in)

Pinned to [`config/settings.expansion.yaml`](../../../config/settings.expansion.yaml) (the active
BTC research config), read 2026-06-18:

| Param | Value | Role here |
|-------|-------|-----------|
| `pivots.mode` | `fractal` | endpoint detection mode |
| `pivots.fractal_n` | `1` | strict Williams bars each side |
| `pivots.lookback` | `3` | prominence opposite-extreme window (`[i-lb, i+lb]`) |
| `pivots.atr_period` | `14` | ATR scale (trailing Wilder) |
| `pivots.min_prominence_atr` | `0.5` | candidate floor |
| `scoring.structure_window` | `6` | base-pivot window for structure / exclusivity |
| `scoring.confluence_degrees` | `[5, 12]` | larger fractal degrees for `scale_confluence` |
| `scoring.confluence_tol_bars` | `3` | endpoint↔degree match tolerance |
| `evaluation.time_tol_bars` | `3` | reused as ε_time (see A4) |
| `evaluation.price_tol_atr` | `0.5` | reused as ε_price, ATR units (see A4) |

No tuning of these is authorised by this addendum; the study **reuses** them as-is.

## A2. Feature list + provenance table (refines prereg §5)

The study reuses the engine's **eight existing interpretable features**
([`core/features.py:compute_features`](../../../src/fibengine/core/features.py)) — no new features
invented. Each carries the prereg §5 binary tag (fail-closed) **plus** a finer **minimum
confirmation buffer `k*`** = the number of bars after `anchor_b` required to *compute* the feature
under the A1 pins.

> **Why `k*`, not a bare binary (the load-bearing refinement).** A pure
> `{left-available, right-edge-sensitive}` split with mechanical exclusion (§5) would freeze the
> live model's input at **every** `k`, making the mandatory `k`-sweep (§8) vacuous: nothing on the
> live side could move as `k` grows, so the causal-availability gap would be a **tagging artifact,
> not an empirical finding** — the exact forking-paths failure the prereg guards against. Tagging
> each feature with `k*` keeps §5's binary (`k*=0` ⇔ `left-available`; `k*>0` ⇔
> `right-edge-sensitive`, fail-closed) **and** makes the sweep admit features as the buffer grows.
> The fail-closed default is preserved: any feature whose availability is uncertain is assigned the
> **larger** buffer (up to ∞), never the smaller.

| Feature | §5 tag | `k*` (bars after `anchor_b`) | Rationale (from code) |
|---------|--------|------------------------------|-----------------------|
| `magnitude` | left-available | **0** | `price_range / end_atr`; both endpoints + trailing ATR known at `anchor_b`. |
| `cleanliness` | left-available | **0** | net/path over closes in `[anchor_a, anchor_b]` only. |
| `duration` | left-available | **0** | `|bars − target|`; bar count of the leg, fully internal. |
| `round_number` | left-available | **0** | pure price proximity; **interaction-only** per §3 (never primary). |
| `prominence` | right-edge-sensitive | **3** | endpoint prominence uses the forward window `[i, i+lookback]` (`lb=3`); fractal confirm `fractal_n=1 ⊂ 3`. |
| `structure_alignment` | right-edge-sensitive | **3** | `_recent` filters to `index ≤ end_index`, but edge pivots need their own forward bars (~`lb`) to be detectable. |
| `scale_confluence` | right-edge-sensitive | **12** | endpoint must be a fractal at `max(confluence_degrees)=12` → needs ≥12 bars after the endpoint. |
| `recency` | right-edge-sensitive | **∞** | `end.index / (n−1)` references the **dataset end**, not `anchor_b+k` → omniscient as coded. |

### A2.1 `recency` disposition (explicit, no hand-waving)

`recency` is **dropped from the live-equivalent model at every `k`** (`k*=∞`). It is **not** silently
redefined. The **retrospective** model (window `W`) may use a **viewport-relative recency**
= `(anchor_b.index − viewport_start) / (W + (anchor_b − anchor_a))`, computed against the *bounded*
viewport edge, never the dataset end. Note this viewport-relative form is ≈constant for legs that
end at the viewport edge, so it is informative only across legs at differing depths inside `W`; it is
reported as a retrospective-only feature, never as a live feature.

### A2.2 Structural enforcement (operationalizes §5)

The **live-equivalent model at buffer `k`** is built **only** from features with `k*(f) ≤ k` —
mechanically, by column selection on the feature matrix, not by "avoidance." Thus:

- `k = 0` → `{magnitude, cleanliness, duration}` (+`round_number` as interaction only)
- `k = 3` → above **+** `{prominence, structure_alignment}`
- `k ≥ 12` → above **+** `{scale_confluence}`
- `recency` → never in any live model.

The **retrospective model** may use all features computable within its window `W` (so all eight,
provided `W ≥ k*`, with `recency` in its viewport-relative form).

## A3. Exclusivity / parsimony (#4) — operationalization (the prereg's flagged soft spot)

Per prereg §3.4, exclusivity is **set-level**, not per-candidate, and must not grow into its own
study. Frozen rule:

- **Segmentation = the detector's base-degree pivot sequence**
  ([`detect_pivots`](../../../src/fibengine/pivots/detect.py) at the A1 pins), chunked into
  consecutive runs of `structure_window = 6` base pivots. A "structure" is one such chunk. **No
  parent-/larger-degree boundaries** are used to segment in the live model (those would be `k*=12`,
  smuggling future bars into segment edges).
- **Exclusivity score** = (human-marked legs whose endpoints fall in the chunk) ÷ (candidate legs
  enumerated by [`enumerate_swings`](../../../src/fibengine/core/features.py) in the chunk). A
  parsimonious selector marks ≪ all candidates per chunk.
- **Provenance tag:** `right-edge-sensitive`, **`k* = 3`** — it inherits base-pivot confirmation
  (no degree-12 dependence). It therefore enters the live model only at `k ≥ 3`, alongside
  `prominence`/`structure_alignment`.
- Scope guard: exclusivity is a **single set-level feature/diagnostic**, reported with the gestalt;
  it is **not** a separate clustering/segmentation study.

## A4. Match tolerance ε (reuse, not invent — blindness defense)

ε is **reused verbatim** from the existing
[`EvaluationConfig`](../../../src/fibengine/core/config.py) — `time_tol_bars = 3`,
`price_tol_atr = 0.5` — across **all TFs**. These were set **blind to this study** (they predate it)
and `price_tol_atr` is already in **ATR units**, matching prereg §7's "ε_price in ATR units". Reusing
the pre-existing convention is the strongest available blindness defense; no per-TF ε tuning is
authorised. ε absorbs the wick-vs-body anchor-placement convention (§7), not a selection dimension.

## A5. `k` / `W` per TF + the single primary cell (forking-paths defence, §8)

Detector buffers (`k*`) are bar-based and TF-independent. `W` is the **bounded** realistic labeling
viewport (§4: finite, *not* dataset end) and is pinned per TF below. TFs in scope: **1M, 1w, 1d, 4h**
(no 1H, §13).

| TF | `k`-sweep (bars) | **Primary `k`** | `W` (bars) | `W` rationale (finite, ≫ `k`, ≪ dataset) |
|----|------------------|-----------------|------------|-------------------------------------------|
| 1M | {0, 3, 6, 12} | **3** | **24** | ~2 yr structure view; covers `k*=12` w/ margin, ≪ ~115-bar history. |
| 1w | {0, 3, 6, 12} | **3** | **52** | ~1 yr forward view. |
| 1d | {0, 3, 6, 12} | **3** | **120** | matches the existing 1D reaction-review ~90-day window scale, with margin. |
| 4h | {0, 3, 6, 12} | **3** | **180** | ~30 days forward view. |

**Single pre-registered headline test (exactly one):** **Stage 2 (leg gestalt)**, **live-equivalent
viewport at primary `k = 3`**, vs the §6 baseline, primary metric (§9), one per TF.

- **Why `k = 3`:** it is the **base detector's own confirmation buffer** (the moment the leg's
  endpoints are confirmable as base-degree pivots = the minimal *live-confirmable leg*). At `k = 3`
  the live model sees `{magnitude, cleanliness, duration, prominence, structure_alignment,
  exclusivity}` and **excludes** `scale_confluence` (`k*=12`) and `recency` (`k*=∞`). Chosen from
  first principles (detector confirmation), **not** from any result.
- **Everything else is secondary / sensitivity:** Stage 1 (per-pivot diagnostic), all non-primary
  `k` (0, 6, 12), the retrospective `W` model, and per-feature gap attribution. The
  causal-availability gap is read **across** the `k`-sweep: a gap that **closes** as `k`→12 (when
  `scale_confluence` is admitted) = the live cutoff was merely too tight; a gap that **persists** at
  large `k` = genuine right-edge dependence. "Does *any* swept cell beat baseline?" is **not** a
  valid claim (the B-1 forking-paths lesson is binding).
- Multiplicity: the four per-TF headline tests carry an e-Holm / Holm correction (the
  [anytime-valid e-value machinery](../concepts/anytime-valid-evalues.md) if re-looks occur;
  ordinary Holm for a single look), pre-declared here.

## A6. What this addendum does NOT do

- No code, no harness, no run, no dependency, no label/corpus mutation (still docs-only).
- No detector/config tuning; no new features; no auto-fib-as-truth; no PnL/backtest; no 1H; no
  Genesis touch; no ML-hype. Honours prereg §13 in full.
- Does **not** grant execution: §12.3 still requires a **separate explicit go**.

---

### Evidence discipline

- **Observed (verified from code/config 2026-06-18):** the eight features and their formulas
  (`core/features.py`); `detect_pivots` forward window `[i-lb, i+lb]` + fractal confirm
  (`pivots/detect.py`); `scale_confluence` uses `confluence_degrees=[5,12]` (`core/scale.py`);
  `recency = end.index/(n-1)` references dataset end; the pinned `settings.expansion.yaml` values;
  `EvaluationConfig` ε defaults.
- **Inferred:** the `k*` values (minimum buffers) follow logically from those forward-looking
  constructions; `k=3` is the minimal live-confirmable-leg cutoff; the chosen `W` values are
  realistic bounded viewports.
- **Unverified / out of scope here:** whether the human selection is learnable, the size/sign of the
  causal-availability gap, and whether any cell beats baseline — *that is the study*, gated on §12.3.

> Docs-only. Authorises no code, no dependency, no run, no source-label change.

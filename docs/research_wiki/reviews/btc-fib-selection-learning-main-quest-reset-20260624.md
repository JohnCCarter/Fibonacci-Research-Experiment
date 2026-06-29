# BTC Fib Selection-Learning — MAIN-QUEST RESET / north-star guardrail (2026-06-24)

**Lean Fib Research. Docs-only, no code/run/claim.** A deliberate stop to the mechanics drift and a
re-anchor to the original goal. Binding for the whole selection-learning line.

> **NORTH STAR (Chamoun's original idea — binding):** *Get the machine to learn how the human selects
> meaningful fib legs/ranges and draws Fib like a human analyst, using the human facit as ground
> truth.* **NOT** explaining detector/snapping/measurement geometry detail.

## 1. What we now know that DIRECTLY helps the main quest

- **The human's leg choice is partly learnable (4H).** Human-marked legs are measurably **cleaner /
  more efficient**, and a model out-ranks the trivial baselines out-of-sample (Stage-2 lift **+0.052**,
  CI excludes 0). → there **is** a real learnable selection signal.
- **It is live-available** (`no_causal_gap`) — a human-like selector would not need hindsight.
- **It is not a detection problem** (Stage-1 recall ~0.90): the human's anchors are already in the
  candidate universe; the gap is in **ranking/selecting among candidates** — exactly what a model can
  improve.
- **The signal lives in the leg/range gestalt**, not the lone pivot (Stage-1 null) — a human-like
  selector must model **legs/ranges**, not individual pivots.
- **But agreement is LOW and thin:** AP ~0.057 vs the ~0.83 reachability ceiling, carried almost
  entirely by **one feature** (cleanliness). The model does **not** yet draw like the human — it needs
  a **richer representation of "meaningful."** *(This is the gap that defines the real next step.)*

## 2. What was only control / mechanics (rigor, not new capability)

- Prominence-family sensitivity + k-sweep (robustness), W-gap (hindsight control), the cleanliness
  artifact-probe (is the lead a detector artifact?), and the mechanics + snapping-flip notes
  (detector/snapping geometry). **All were necessary rigor or interesting mechanism — none added model
  capability to pick better legs.** The mechanics/flip work is precisely the drift this reset stops.

## 3. Sidetracks to PARK now

- **Artifact / snapping / net-path mechanics** — PARK (questions answered descriptively; does not help
  the model pick human-like legs).
- **Matched-null / detector-independent universe** — PARK (gated, its A8 gate was **not** met, high
  methodological risk; an artifact-question tool, not a capability-builder).
- **Set-level `exclusivity`** loose end — revisit **only** if it demonstrably improves leg selection.
- **Further detector-geometry explanation** — PARK.

## 4. Next step IF the goal is better human-like leg/range selection

- The **only** directly-aligned move: **enrich the selection model toward the human's actual "meaningful
  leg/range" criteria and measure agreement against the facit** (AP toward the 0.83 ceiling). Concretely
  — go beyond "cleanest leg" to the multi-component gestalt the prereg already named (scale, pairing,
  direction, exclusivity, HTF/context) and test whether **facit-agreement rises** — behind a **blind
  design lock** (forking-paths discipline; same two-commit gate as every prior step).
- **Precondition:** a concrete feature/representation hypothesis that *plausibly* raises agreement, AND
  enough facit to fit/validate without overfitting (BTC-only, **365** 4h legs, one analyst, ~0.83
  ceiling). If that precondition can't be met honestly, see §5.

## 5. If the next step does NOT directly help the model pick better → stop/park

- If we **cannot** specify a richer-feature hypothesis that plausibly raises facit-agreement without
  forking-paths, **PARK the modeling line** and return to the **actual main quest**: the human BTC
  top-down fib labeling (`1M → 1w → 1d → 4h`,
  [protocol](../../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md)) — which **is** "draw Fib like a human" and grows
  the ground-truth corpus the model would learn from. Modeling resumes only with **more labels** or a
  **concrete capability hypothesis**, never as another control/mechanics pass.

## North-star guardrail (BINDING — no drift)

Every future selection-learning step must answer one question first:

> **"Does this improve the model's ability to select human-like fib legs/ranges, measured against the
> facit?"**

If the honest answer is **no** — it is a control, a mechanism explanation, or an artifact-geometry
detail — **do not start it; log it as parked.** Controls and mechanics are **done**. The line either
**advances selection capability** (§4, behind a blind lock) or it **pauses** (§5). No more
detector/snapping/measurement-geometry side-quests.

# Horizontal-Structure Studies — Standing Pre-registration Addendum (2026-06-17)

**Lean Fib Research.** Three standing methodology requirements for **future** level-reaction /
horizontal-structure studies in the Fib repo. This addendum is **forward-looking**: it does **not**
mutate the frozen preregs of the closed BTC/Fib behaviour line
([behaviour](btc-fib-behaviour-event-study-prereg-20260616.md),
[context-conditioned](btc-fib-context-conditioned-study-prereg-20260616.md)) — those stay frozen as
historical record. Any **new** prereg for a horizontal-structure question must satisfy NU-1..NU-3
below (or state explicitly, fail-closed, why one does not apply).

Scope guardrails unchanged: BTC-first, human fib = facit, machine output = proposal, no leakage, no
auto-fib, no trading/edge claim, null results acceptable, fail closed on ambiguity.

---

## NU-1 — Random-walk / synthetic-series control is mandatory

A future horizontal-structure study must pre-register a **synthetic random-walk control** in
addition to the existing shuffle-price placebo and causal-swing baselines.

- **Rationale (OBSERVED, literature):** support/resistance levels and chart formations emerge
  spontaneously in pure random walks with no fundamentals, news, or order flow — so a formation's
  mere existence is not evidence of a mechanism. The random-walk control sets the correct null
  prior for a level-reaction claim.
  - Primary anchor: **Lo, Mamaysky & Wang (2000), "Foundations of Technical Analysis…",
    *Journal of Finance* 55(4):1705–1765.** (Anchor on this peer-reviewed source, not on weaker
    single-author working papers.)
- **Requirement:** the control series is **deterministic and seeded** (reuse the existing
  `seed = 20260616` convention), strictly **causal** (no future information used to generate or
  place levels), and run through the **same** event/outcome/permutation machinery as FIB / PLACEBO
  / SWING so it cannot favour any source.
- **INFERRED gap:** the repo currently has only shuffle-price placebo
  (`make_placebo_levels`) and causal-swing baseline — no synthetic-series generator. Implementing
  the generator is tracked as **DELAR-1** (not authorised by this doc; docs-only here).

## NU-2 — Re-look / anytime-valid inference protocol

The repo's binding rule is *"do not re-run a closed study on the same data with tweaked parameters;
any future test must be a new prereg on fresh data or a materially different question"*
([log 2026-06-16](../log.md)). This addendum turns that **rule** into a **method** for the cases
where a re-look is genuinely warranted.

- **Problem (OBSERVED, paper):** fixed-horizon p-values and confidence intervals are **not valid**
  when the sample size or the decision to look is chosen by continuously monitoring the data
  (optional stopping / peeking). The context-conditioned study already disclosed a "second look"
  at the same OOS window (its §0) — that is exactly the exposure.
  - Primary: **Johari, Pekelis & Walsh, "Always Valid Inference: Continuous Monitoring of
    A/B Tests," arXiv:1512.04922.**
- **Requirement when a re-look is unavoidable:** use **anytime-valid inference** (always-valid
  p-values / confidence sequences via **e-values**) instead of a fresh fixed-horizon permutation
  p-value. For multiplicity, use **e-Holm** — the e-value analogue of the **Holm** correction the
  repo already applies — so Type-I control survives continuous monitoring.
- **Default remains:** prefer a **new prereg on fresh data**. Anytime-valid inference legitimises a
  re-look statistically; it does **not** license parameter-hunting on a closed null.
- **INFERRED gap:** no sequential/e-value code exists in the repo. A small, direct e-process
  implementation (not a pre-release third-party package) is tracked as **SENARE-1**, gated on
  whether re-looks actually become routine.

## NU-3 — Purged/embargoed split: name it, don't rebuild it

The existing out-of-sample split already implements the core of purged cross-validation: a
time-ordered 70/30 split with an **embargo/purge** of `max(horizon)` bars at the boundary so no
event's outcome horizon straddles the split.

- **Where (OBSERVED, code):**
  [`research/fib_behaviour_event_study.py`](../../../src/fibengine/research/fib_behaviour_event_study.py)
  — `split_positions()` / `_window_of()` (the embargo drops events whose horizon crosses the split);
  documented in the behaviour prereg §7.
- **Requirement:** future-study docs should **name** this mechanism *purged/embargoed split* and
  cite **López de Prado, *Advances in Financial Machine Learning* (2018), Ch. 12** (purging,
  embargo, combinatorial purged CV / CPCV) for vocabulary and provenance.
- **Do not over-build:** the single-split embargo already neutralises horizon-straddle leakage for
  the event studies. A full combinatorial purged-CV module (**SENARE-2**) is **gated** on a
  demonstrated need that the current single split does not cover — adopting it carelessly (bad
  label-interval assignment) can *introduce* leakage rather than prevent it.

---

## Evidence discipline

- **Observed:** Lo et al. (2000) and arXiv:1512.04922 state the claims attributed above; the
  embargo/purge logic exists in `fib_behaviour_event_study.py` as cited.
- **Inferred:** that these controls/methods map onto the Fib repo's next legitimate question
  (generic horizontal structure post-fib-null); that e-Holm composes with the existing Holm use.
- **Unverified / out of scope here:** whether the current single-split embargo already covers
  everything CPCV would (SENARE-2 gate); whether re-looks become frequent enough to justify
  building e-value infra now (SENARE-1 gate).

> This addendum is **docs-only**. It authorises no code, no dependency, and no source-label change.
> It states requirements that future preregs must meet; implementation items (DELAR-1, SENARE-1/2)
> remain unauthorised until separately requested. See plan
> `C:\Users\fa06662\.claude\plans\clever-yawning-catmull.md`.

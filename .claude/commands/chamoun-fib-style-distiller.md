---
description: Distill the human's daily fib drawing style into Observed/Inferred/Unverified rules (#38/#39).
---

# `/chamoun-fib-style-distiller`

**Purpose:** turn repeated verbal explanation of *how the human draws daily wick-pair fibs* into a
small, auditable rule set — so the style is captured once, not re-explained to every agent.
**When to use:** when reviewing daily fib examples/screenshots/facit to extract drawing rules,
before any detector build (#38) or test writing.
**Codifies:** [AGENTS.md](../../AGENTS.md) *Observed vs Assumption* + *Research easy, authority
hard* + *Lean Fib Research*. Adds **no** new research behavior — it is a note-taking discipline.

## Steps

1. **Scope-gate first:** run [`/fib-scope-check`](fib-scope-check.md). If the step is a mismatch or
   an edge/auto-fib claim is creeping in, stop and reframe before distilling.
2. Read the daily facit as ground truth: `data/labels/human_fib/bitfinex/BTC-USD/1d/fib_*.json`
   (fields `anchor_a`/`anchor_b`/`direction` — **reuse this schema; introduce no new fields**) plus
   the user's examples/notes and the [#38 prereg](../../docs/research_wiki/reviews/btc-fib-daily-wick-pair-anchor-prereg-20260629.md).
3. Extract each drawing rule and **classify** it:
   - **Observed** — directly present in the facit/examples (cite the fib_id).
   - **Inferred** — derived from a repeated pattern across ≥2 examples.
   - **Unverified** — plausible but not yet supported by enough examples; name the missing example.
4. For each rule, record: which wick/anchor **wins**, which **loses**, and **why** (the
   discriminating feature). Include **negative / no-fib** cases — avoiding bad fibs is part of the
   style.
5. Surface premise risks explicitly — e.g. the body/close-vs-wick-extreme anchor question (see the
   #38 prereg). Do not paper over a rule that the facit contradicts; the **source wins**.

## Output

- A short rule list, each tagged `Observed` / `Inferred` / `Unverified` with a cited example.
- A/B anchor explanation (winner/loser/why) + the missing examples needed to promote `Unverified`.
- Proposed label/test additions — **named only, not built** (deferred to #38 run; see Non-goals).

## Non-goals

- **No edge / PnL / continuation claim** — golden zone (0.5/0.618) is a stated hypothesis, never
  given significance (active protocol retired golden-zone bias).
- **No new label-schema fields, no test-writer/implementer skills, no `examples/` tree** until the
  #38 prereg is locked and run — keep it lean.
- **tradingview-mcp = inspect-only** — read the source if useful, integrate nothing.
- Not a governance gate; a note-taking playbook.

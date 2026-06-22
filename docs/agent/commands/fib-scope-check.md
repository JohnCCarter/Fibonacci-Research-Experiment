---
description: Verify the next step is intent-valid, not just technically valid (#35).
---

# `/fib-scope-check`

**Purpose:** verify the proposed next step is *intent-valid*, not merely *technically valid*.
**When to use:** before starting or continuing any research / implementation / audit path —
especially after repeated nulls, a plan that has run a while, or a "this isn't what I meant".
**Codifies:** [AGENTS.md](../../../AGENTS.md) *Intent alignment over plan inertia* + *Research easy,
authority hard*.

## Steps

1. State the user's **actual claim / goal** in one sentence.
2. State **what question this step answers** in one sentence.
3. Are (1) and (2) the same? If not, name the **mismatch** explicitly.
4. Flag any drift: authority/edge claim creeping into exploratory work, Genesis-v1 re-patterning,
   or unnecessary governance/rigidity.
5. Recommend: **continue** / **pause-and-ask** / **reframe** (with the reframed question stated).

## Output

- The four answers (1–4) + a one-line verdict: `aligned` / `mismatch — reframe` / `pause, ask user`.

## Non-goals

- **Never** used to chase positive results — interlocks with *Validity over convenience*. Changing
  the question after a null is valid only when the prior question is shown misaligned with the
  original claim, with the new scope/baselines/non-claims stated **before** any new run.

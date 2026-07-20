---
description: Button-driven interview to learn/refresh who the owner is and how he wants to be worked with; persists to the synced wiki.
---

# `/owner-interview`

**Purpose:** a short, button-driven interview an agent runs to learn (or refresh) *who the owner is*
and *how he wants to be worked with*, then persist the answers to the **git-synced** wiki so they
travel to every machine (work · home · iPhone).
**When to use:** a fresh machine/agent, or any time the owner says "interview me."
**Codifies:** [owner-preferences](../../docs/research_wiki/owner-preferences.md) (the synced source of
truth), the [agent-native wiki](../../docs/research_wiki/decisions/2026-06-17-wiki-is-agent-native.md)
operating model (git is the only channel between the owner's machines), and
[AGENT_RESPONSE_STYLE](../../docs/agent/AGENT_RESPONSE_STYLE.md).

## Rules (the ones that make it work)

- **Use `AskUserQuestion` (buttons), not prose questionnaires** — the owner explicitly prefers it.
- Set **`multiSelect: true`** on every question — he often picks several *and* adds free-text via
  "Other". Up to 4 questions per call; expect ~3 calls total.
- **Lead each round conclusion-first**, then shape the next round from what he just answered.
- **Don't over-explain** — short framing, then the buttons. Honour
  [owner-preferences](../../docs/research_wiki/owner-preferences.md) throughout.
- This is a **diff, not a fresh fill** — read owner-preferences first and hunt for *changes*; don't
  re-ask what is already settled.
- After the rounds, **mirror the findings back in 3–5 lines** (conclusion-first) and name the
  *concrete* ways they change how you'll work.

## The questions (the set that worked — adapt freely)

Each is `multiSelect: true`. Labels are short; descriptions carry the nuance.

**Round 1 — orientation**
1. *Role / background* — Trader/analyst · Builds-it-himself (hybrid) · Developer · Learning.
2. *Technical pull / strength* — Frontend/graph-UI · Data/wiki · Architecture/AI · Backend.
3. *How we work together* — Autonomously · Just-get-it-done · Teach-me-as-we-go · Check-in in steps.
4. *Coding level today* — Product/idea person · Beginner · Intermediate · Experienced.

**Round 2 — calibration**
5. *Explanation that lands* — Plain-language/analogies · Short summary · Show code+comments · Step-by-step.
6. *Success in a year* — Live Trader-agent · Tool he uses himself · Understands the build · Polished/shareable.
7. *Work cadence* — Short frequent sessions · Long focus sessions · Multi-machine + mobile · Irregular.
8. *Biggest friction* — Doesn't-understand-what-changed · Becoming-a-bottleneck · Too much text · Things-break.

**Round 3 — depth (frontend / backend / working style)**
9. *Frontend — what matters in the graph/UI* — Interactivity · Polished/clear · Drill-down/focus · Quick overview.
10. *Backend — how involved* — Keep-it-away · Understand-at-a-high-level · Data-quality-matters · Broker/live-data.
11. *At a check-in, what he wants* — A recommendation · Only-if-it's-important · Show-the-result · Cost/risk-visible.
12. *How to present a fork* — Recommendation-first · Use-AskUserQuestion · Visual/mockup · Cost/risk-visible.

## Persist the answers (the part that actually syncs)

1. Update [owner-preferences](../../docs/research_wiki/owner-preferences.md): sharpen the *"Who the
   owner is"* block and the working guardrails; bump `Last verified`; add an `Evidence` line
   `"owner interview <date>"`. Use markdown links `[text](path)` — this wiki does **not** use
   `[[wiki-link]]` syntax.
2. Append one `maintenance` entry to [log.md](../../docs/research_wiki/log.md)
   (`## [YYYY-MM-DD] maintenance | owner interview — what changed`).
3. Ensure owner-preferences stays linked from [index.md](../../docs/research_wiki/index.md) so
   `scripts/wiki_lint.py` does not flag it as an orphan / dead link.
4. (Optional) mirror to machine-local agent memory as a *fast-recall cache* — but the wiki page is
   the source of truth, because **only git travels between the owner's machines**.

## Non-goals

- Not a personality quiz — every captured item must change *how the agent works*.
- Do not store secrets, credentials, or anything that should not be committed to git.
- Do not let captured preferences override repo guardrails ([AGENTS.md](../../AGENTS.md)) or
  research validity — working-style preferences never relax leakage/authority rules.

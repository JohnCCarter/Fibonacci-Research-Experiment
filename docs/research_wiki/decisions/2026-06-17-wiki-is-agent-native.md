# Decision: the research wiki is agent-native warm context (2026-06-17)

## Decision

The `docs/research_wiki/` is **agent-native tooling** — the agent's **persistent warm context** for
**millisecond orientation across sessions and agents** ("as if the session never ended"). It is not
primarily human documentation or a governance apparatus.

Operating model — a deliberate, reasoned extension of the
[Karpathy LLM wiki](../sources/karpathy-llm-wiki.md) pattern:

> **The agent curates sources, the human asks questions, the agent does the rest.**

(Karpathy's gist puts the human as curator because there the human drags in articles. In this repo
the agent does the work and meets the sources — code, experiments, decisions, external literature it
pulls in — so the agent curates. The human's role is to query and to audit.)

## Why (the two deviations this corrects)

Reviewing Karpathy's gist against our wiki surfaced two genuine deviations from his idea:

1. **No accumulation loop.** His core point is a knowledge base that grows so the LLM never
   "rediscovers knowledge from scratch." Ours had **1 `sources/` page and 0 external-methodology
   concept pages** — agents re-derived methodology every session (e-values, purged/embargoed CV,
   the random-walk null were re-derived in-context on 2026-06-17 instead of read).
2. **Ceremony tax.** Hard line/byte caps forced **mid-task archiving** (done that same session on
   `log.md`) — friction on the exact agent the tool is supposed to serve. Karpathy's bookkeeping is
   meant to cost **near zero**.

## What stays non-negotiable

**Source wins.** The wiki never owns truth; it points at the layers below
([source-authority.md](../reference/source-authority.md)). This is *more* critical now, not less:
when the agent both writes and reads its own memory, "source wins" is the anti-self-deception guard,
and the human-as-querier is the oversight that surfaces gaps and contradictions.

## What changes

- **Search surface vs knowledge corpus (the key distinction we had conflated under "bounds").**
  - *Scope the search surface* (raw data, archives, dumps) so orientation stays fast — keep/sharpen
    [`.rgignore`](../../../.rgignore) and the anti-blob / required-file guards in
    [`check_repo_bounds.py`](../../../scripts/check_repo_bounds.py) (`check_boundary()`, untouched).
  - *Do not cap the knowledge corpus.* Caps that force archiving bury the knowledge the agent needs.
    The always-read **fast path** (`index.md`, `handoff.md`) stays modestly bounded so orientation
    stays cheap; depth lives in the **uncapped, sharded** corpus (`concepts/`, `reference/`,
    `reviews/`, `decisions/`, `sources/` + `log.md`), queried on demand. Enforced via the relaxed
    `RULES` table (anti-runaway ceilings only).
- **Restore the accumulation loop.** Methodology the agent reuses gets a small concept/source page
  linked from `index.md`, so the next agent **queries the wiki instead of re-deriving**. Seeded
  reuse-first (see [anytime-valid e-values](../concepts/anytime-valid-evalues.md),
  [purged/embargoed CV](../concepts/purged-embargoed-cv.md),
  [random-walk null](../concepts/random-walk-null.md),
  [methodology anchors](../sources/methodology-anchors.md),
  [closed questions](../reference/closed-questions.md)).
- **Maintenance is agent self-interest, not a chore.** Persist now so future-you orients in ms.
  "Query the wiki before re-deriving methodology" is part of the agent contract
  ([README.md](../README.md), [.cursor/rules/research-wiki-maintenance.mdc](../../../.cursor/rules/research-wiki-maintenance.mdc)).

## Supersedes

The "What We Do Not Adopt Yet" list in [sources/karpathy-llm-wiki.md](../sources/karpathy-llm-wiki.md)
(which froze out the accumulation loop) and the prior framing of the wiki as merely
"navigation/synthesis." The wiki is navigation **and** accumulated knowledge; source still wins.

## Out of scope

No `src/fibengine` behavior change; no auto-fib/edge/trading/ML. This is tooling for how agents
remember, not what they conclude. Research lines (selection-learning, etc.) are unaffected.

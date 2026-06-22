# Research Wiki Index

**Agent-native warm context** — start here to orient in milliseconds instead of
re-searching the repo or re-deriving methodology (purpose:
[decisions/2026-06-17-wiki-is-agent-native.md](decisions/2026-06-17-wiki-is-agent-native.md)).
Source evidence is the truth; wiki pages are the map and accumulated knowledge. When they
disagree, the source wins — see [source-authority.md](reference/source-authority.md).

**Before re-deriving methodology or proposing a study,** check
[Methodology](#methodology--query-before-re-deriving) and
[closed questions](reference/closed-questions.md) (do-not-re-run registry).

## Wiki Operations

- [README](README.md) — rules, page types, and maintenance loop.
- [**Source authority**](reference/source-authority.md) — which layer wins when
  evidence and wiki disagree.
- [Log](log.md) — append-only trail of ingests, decisions, reviews, questions.
- [Current handoff](handoff.md) — current working context and next action.
- [Glossary](glossary.md) — compact definitions and links.

## Schema And Concepts

- [**CONSTITUTION FOR AGENTS**](../../AGENTS.md) — duties, guardrails, source authority (canonical).
- [Module map](reference/module-map.md) — `src/fibengine` packages and roles.
- [Data conventions](reference/data-conventions.md) — label, human-fib, and
  experiment path shapes.
- [CLI commands](reference/cli-commands.md) — common commands for fetch,
  experiment, review, tests, and build.
- [Guardrails](concepts/guardrails.md) — research-only invariants and promotion
  boundaries.
- [Atomic runnable artifacts](concepts/atomic-runnable-artifacts.md) — small,
  complete research artifacts with command, input, output, and interpretation.
- [Agent handoff and log](concepts/agent-handoff-log.md) — current context plus
  append-only trail.

## Core Concepts

- [VAD / HUR](concepts/vad-hur.md) — weekly range vs daily behavior resolution.
- [Relation vs candidate](concepts/relation-vs-candidate.md) — geometry atoms vs
  behavior hypotheses.
- [Human fib ground truth](concepts/human-fib-ground-truth.md) — manual anchors,
  levels, and candidate events.

## Methodology — query before re-deriving

Accumulated external methodology so agents read instead of re-derive (see
[methodology-anchors.md](sources/methodology-anchors.md) for the papers):

- [Anytime-valid e-values + e-Holm](concepts/anytime-valid-evalues.md) — conditional 2×2 safe-test
  e-value for re-looks at a peeked window.
- [Purged / embargoed CV](concepts/purged-embargoed-cv.md) — leakage-safe OOS split (López de Prado).
- [Random-walk null](concepts/random-walk-null.md) — the control a level-reaction claim must beat.
- [**Closed questions**](reference/closed-questions.md) — do-not-re-run registry (fib behaviour,
  context-conditioned, B-1 all NULL).

## Templates

- [Atomic artifact template](templates/atomic-artifact.md) — skeleton for small
  runnable research notes.
- [Handoff entry template](templates/handoff-entry.md) — skeleton for handoff
  sections and session notes.

## Decisions

- [2026-06-22 project command playbooks](decisions/2026-06-22-project-command-playbooks.md) — the
  four repo commands (`/fib-scope-check`, `/absorb-patterns`, `/prepare-home-computer`,
  `/prepare-job-computer`) live as versioned docs under `docs/agent/commands/`, not local `.claude/`
  (#36 design).
- [2026-06-17 wiki is agent-native](decisions/2026-06-17-wiki-is-agent-native.md) — the wiki is the
  agent's persistent warm context (agent curates, human queries, source wins); search-surface vs
  knowledge-corpus split; accumulation loop restored.
- [2026-06-04 fib-aware review](decisions/2026-06-04-fib-aware-review.md) —
  current decision to improve review rendering and defer full UI replacement.

## Sources

- [Karpathy LLM wiki](sources/karpathy-llm-wiki.md) — source pattern for this
  wiki.
- [Methodology anchors](sources/methodology-anchors.md) — external papers the repo's methods rely
  on (Lo–Mamaysky–Wang, Johari–Pekelis–Walsh, Grünwald safe testing, López de Prado).

## Reviews

- [Reviews (superseded)](reviews/README.md) — pre-reset descriptive reads archived
  2026-06-08; not current evidence.

## Canonical Source Docs

- [**BTC-first top-down protocol**](../BTC_FIRST_TOP_DOWN_FIB_PROTOCOL.md) — active
  research direction (BTC/USD, 1M → 1W → 1D → 4H).
- [Research handoff](../research/RESEARCH_HANDOFF.md) — hypothesis and boundaries (update when aligned).
- [Repo tracks](../TRACKS.md) — Research, Validate, and Promotion separation.
- [Human fib annotation](../labeling/HUMAN_FIB_ANNOTATION.md) — manual fib source of truth.
- [Level events](../research/LEVEL_EVENTS.md) — candidate detector and taxonomy.
- [Level event review](../research/LEVEL_EVENT_HUMAN_REVIEW.md) — review package workflow.
- [Fib candidate outcomes](../research/FIB_CANDIDATE_OUTCOMES.md) — forward outcome backtest (#22).
- [Fib level fingerprints](../research/FIB_LEVEL_FINGERPRINTS.md) — pre/at/post interaction features (#23).
- [Fib fingerprint × outcome join](../research/FIB_FINGERPRINT_OUTCOMES.md) — #22 + #23 combined table.
- [MTF fib level projection](../research/MTF_FIB_LEVEL_PROJECTION.md) — runner design (tooling); pre-reset results archived.
- [Fib-aware tooling spike](../research/FIB_AWARE_TOOLING_SPIKE.md) — tooling direction.

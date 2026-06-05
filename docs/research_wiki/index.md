# Research Wiki Index

Start here when looking for accumulated repo context. Source docs are the truth;
wiki pages are the map and synthesis.

## Wiki Operations

- [README](README.md) — rules, page types, and maintenance loop.
- [Log](log.md) — append-only trail of ingests, decisions, reviews, questions.
- [Current handoff](handoff.md) — current working context and next action.
- [Glossary](glossary.md) — compact definitions and links.

## Architecture And Governance

- [Module map](reference/module-map.md) — `src/fibengine` packages and roles.
- [Data conventions](reference/data-conventions.md) — label, human-fib, and
  experiment path shapes.
- [CLI commands](reference/cli-commands.md) — common commands for fetch,
  experiment, review, tests, and build.
- [Model collaboration (GLM + Qwen)](../MODEL_COLLABORATION.md) — GLM-5.1 lead,
  Qwen3-Coder implement (NVIDIA NIM, not fibengine runtime).
- [NVIDIA GLM-5.1 API](reference/nvidia-glm-api.md) — lead agent (plan/review).
- [NVIDIA Qwen API](reference/nvidia-qwen-api.md) — implementation specialist.
- [Cursor workspace agent setup](../CURSOR_WORKSPACE_AGENT.md) — configure
  Cursor shell + BYOK Qwen (`/repo-agent`, rules, wiki bootstrap).
- [Repo-aware agent (short)](../REPO_AWARE_AGENT.md) — companion notes.
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

## Templates

- [Atomic artifact template](templates/atomic-artifact.md) — skeleton for small
  runnable research notes.
- [Handoff entry template](templates/handoff-entry.md) — skeleton for handoff
  sections and session notes.
- [Model handoff template](templates/model-handoff.md) — GLM plan → Qwen implement.

## Decisions

- [2026-06-04 fib-aware review](decisions/2026-06-04-fib-aware-review.md) —
  current decision to improve review rendering and defer full UI replacement.

## Sources

- [Karpathy LLM wiki](sources/karpathy-llm-wiki.md) — source pattern for this
  wiki.

## Reviews

- [2026-06-05 ETH 1d human-fib smoke](reviews/2026-06-05-eth-1d-human-fib-smoke.md) —
  issue #15 acceptance smoke; #16 tooling gate.

## Canonical Source Docs

- [Research handoff](../RESEARCH_HANDOFF.md) — current hypothesis and boundaries.
- [Repo tracks](../TRACKS.md) — Research, Validate, and Promotion separation.
- [Human fib annotation](../HUMAN_FIB_ANNOTATION.md) — manual fib source of truth.
- [Level events](../LEVEL_EVENTS.md) — candidate detector and taxonomy.
- [Level event review](../LEVEL_EVENT_HUMAN_REVIEW.md) — review package workflow.
- [Fib-aware tooling spike](../FIB_AWARE_TOOLING_SPIKE.md) — tooling direction.

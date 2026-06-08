# Research Wiki Index

Start here when looking for accumulated repo context. Source docs are the truth;
wiki pages are the map and synthesis.

## Wiki Operations

- [README](README.md) — rules, page types, and maintenance loop.
- [Log](log.md) — append-only trail of ingests, decisions, reviews, questions.
- [Current handoff](handoff.md) — current working context and next action.
- [Glossary](glossary.md) — compact definitions and links.

## Architecture And Governance

- [**CONSTITUTION FOR AGENTS AND SUBAGENTS**](../../AGENTS.md) — roles, workflow, guardrails (canonical).
- [Agent doc map](../agent/INDEX.md) — all agent/subagent MD by layer.
- [Module map](reference/module-map.md) — `src/fibengine` packages and roles.
- [Data conventions](reference/data-conventions.md) — label, human-fib, and
  experiment path shapes.
- [CLI commands](reference/cli-commands.md) — common commands for fetch,
  experiment, review, tests, and build.
- [Model collaboration (GLM + Qwen)](../agent/MODEL_COLLABORATION.md) — GLM-5.1 lead,
  Qwen3-Coder implement (NVIDIA NIM, not fibengine runtime).
- [NVIDIA GLM-5.1 API](reference/nvidia-glm-api.md) — lead agent (plan/review).
- [NVIDIA Qwen API](reference/nvidia-qwen-api.md) — implementation specialist.
- [Cursor workspace agent setup](../agent/CURSOR_WORKSPACE_AGENT.md) — configure
  Cursor shell + BYOK Qwen (`/repo-agent`, rules, wiki bootstrap).
- [VS Code Copilot NVIDIA models](../agent/VSCODE_COPILOT_NVIDIA_MODELS.md) — BYOK
  Custom Endpoint for GLM + Qwen (parity with Cursor NIM setup).
- [Repo-aware agent (short)](../agent/REPO_AWARE_AGENT.md) — companion notes.
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
- [2026-06-05 fib fingerprint × outcome checkpoint](reviews/2026-06-05-fib-fingerprint-outcome-checkpoint.md) —
  #22/#23 done, expanded run, no stable signal yet (working pipeline, no evidence).
- [2026-06-05 n≥20 bucket review](reviews/2026-06-05-fib-n20-bucket-review.md) —
  descriptive read of the 80 n≥20 buckets; only mechanical/definitional structure.
- [2026-06-05 MTF fib projection checkpoint](reviews/2026-06-05-mtf-fib-projection-checkpoint.md) —
  1W→1D slice works (42 interactions, 168 joined); all LOW SAMPLE, no claims yet.
- [2026-06-05 MTF clean-forward n≥20 review](reviews/2026-06-05-mtf-clean-forward-n20-review.md) —
  32 n≥20 buckets; horizon-consistency mechanical, BTC≠SOL; no stable evidence yet.

## Canonical Source Docs

- [Research handoff](../research/RESEARCH_HANDOFF.md) — current hypothesis and boundaries.
- [Repo tracks](../TRACKS.md) — Research, Validate, and Promotion separation.
- [Human fib annotation](../labeling/HUMAN_FIB_ANNOTATION.md) — manual fib source of truth.
- [Level events](../research/LEVEL_EVENTS.md) — candidate detector and taxonomy.
- [Level event review](../research/LEVEL_EVENT_HUMAN_REVIEW.md) — review package workflow.
- [Fib candidate outcomes](../research/FIB_CANDIDATE_OUTCOMES.md) — forward outcome backtest (#22).
- [Fib level fingerprints](../research/FIB_LEVEL_FINGERPRINTS.md) — pre/at/post interaction features (#23).
- [Fib fingerprint × outcome join](../research/FIB_FINGERPRINT_OUTCOMES.md) — #22 + #23 combined table.
- [MTF fib level projection](../research/MTF_FIB_LEVEL_PROJECTION.md) — HTF fib → LTF candle behavior (design + inspection).
- [Fib-aware tooling spike](../research/FIB_AWARE_TOOLING_SPIKE.md) — tooling direction.

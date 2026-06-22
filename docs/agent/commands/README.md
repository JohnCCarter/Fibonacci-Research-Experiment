# Project command playbooks

Repo-specific agent commands for the Fibonacci research workflow — **versioned, agent-agnostic**
(Claude Code, Cursor, any agent reads them). Design rationale + the location decision:
[decisions/2026-06-22-project-command-playbooks.md](../../research_wiki/decisions/2026-06-22-project-command-playbooks.md).

These **codify existing constitution principles** ([AGENTS.md](../../../AGENTS.md),
[CLAUDE.md](../../../CLAUDE.md)) — they add no new research behavior. Each is a short playbook, not a
governance gate (Lean Fib Research).

| Command | Purpose |
|---------|---------|
| [`/fib-scope-check`](fib-scope-check.md) | Verify the next step is intent-valid, not just technically valid. |
| [`/absorb-patterns`](absorb-patterns.md) | Scan external work for patterns that strengthen — never replace — this repo. |
| [`/prepare-home-computer`](prepare-home-computer.md) | Complete handoff for continuation at home. |
| [`/prepare-job-computer`](prepare-job-computer.md) | Pick work suited to the SONAR-sensitive job machine. |

> **Local slash-command mirror:** to get literal `/command` invocation in Claude Code, materialize
> these playbooks into `.claude/commands/` (gitignored — **local per machine, never committed**;
> the docs here stay the source of truth). One-liner, run from the repo root on any machine:
>
> ```bash
> mkdir -p .claude/commands && cp docs/agent/commands/{absorb-patterns,fib-scope-check,prepare-home-computer,prepare-job-computer}.md .claude/commands/
> ```
>
> The four commands then appear in the `/` picker (restart the session if not picked up at once).

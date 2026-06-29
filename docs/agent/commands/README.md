# Project command playbooks → moved to `.claude/commands/`

The repo-specific agent command playbooks are now **canonical and versioned** under
[`.claude/commands/`](../../../.claude/commands/) — they travel via `git pull` across machines and
are invoked literally as `/command` in Claude Code. No more local `cp` mirror step.

Design rationale + the source-of-truth flip:
[decisions/2026-06-22-project-command-playbooks.md](../../research_wiki/decisions/2026-06-22-project-command-playbooks.md)
(the original "`.claude/` is local-only" model was **superseded 2026-06-29** when `.claude/`'s shared
parts — `commands/`, `hooks/`, `settings.json` — became versioned-portable).

| Command | Purpose |
|---------|---------|
| `/fib-scope-check` | Verify the next step is intent-valid, not just technically valid. |
| `/absorb-patterns` | Scan external work for patterns that strengthen — never replace — this repo. |
| `/prepare-home-computer` | Complete handoff for continuation at home. |
| `/prepare-job-computer` | Pick work suited to the SONAR-sensitive job machine. |
| `/chamoun-fib-style-distiller` | Distill the human's daily fib drawing style into Observed/Inferred/Unverified rules (#38/#39). |

These **codify existing constitution principles** ([AGENTS.md](../../../AGENTS.md),
[CLAUDE.md](../../../CLAUDE.md)) — they add no new research behavior. Each is a short playbook, not a
governance gate (Lean Fib Research).

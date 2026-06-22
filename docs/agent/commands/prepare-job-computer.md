---
description: Pick work suited to the SONAR-sensitive job machine (read-only/docs/design).
---

# `/prepare-job-computer`

**Purpose:** select work suited to the job machine — limited permissions, SEP/SONAR sensitivity,
resource limits.
**When to use:** when picking what to do on the work computer, or scoping a session there.
**Codifies:** the SONAR / endpoint-protection discipline in [CLAUDE.md](../../../CLAUDE.md).

## Output (the work plan)

- **Prefer:** read-only review, documentation, design, audit, small deterministic checks.
- **Avoid:** heavy test bursts (unless explicitly asked), long-running jobs, expensive plotting /
  data generation, unnecessary interpreter starts.
- **SONAR discipline (binding):** use the **Bash** tool not PowerShell; **batch gates into one call**
  (`ruff && pytest && bounds`); do not re-run gates needlessly; minimize `uv run` invocations; prefer
  `uv run --no-sync`; never run tests in two sessions at once.
- Note that docs-only commits now skip the local pytest hook (gated to `^(src/|tests/).*\.py$`), so
  documentation/design work stays cheap and cool on this machine.

## Non-goals

- Does **not** trigger long-running, plotting, or data-generation work; defers heavy research runs to
  the home computer.

# Decision: project command playbooks live as versioned docs, not `.claude/` (2026-06-22)

Design for [#36](https://github.com/) — a small set of repo-specific agent commands for the
Fibonacci research workflow. **Design only**; the files themselves land in a separate PR (no
research-code behavior change).

## Decision

The four project commands are defined as **versioned playbook docs** under
[`docs/agent/commands/`](../../agent/) — one markdown file each, source-of-truth, agent-agnostic
(Claude Code, Cursor, any agent reads them) and carried in handoff.

They are **not** committed under `.claude/commands/`: `.claude/` is deliberately **local** —
gitignored ([`.gitignore`](../../../.gitignore) `.claude/`) **and** pollution-guarded
(`POLLUTION_GLOBS` in [`check_repo_bounds.py`](../../../scripts/check_repo_bounds.py)). Putting the
commands there would make them local-only and un-shared, defeating the issue's own goal (consistent
behavior across sessions and machines).

> Optional, per-operator: an agent may mirror a playbook into a local `.claude/commands/*.md` thin
> wrapper that just points at the doc, to get literal `/command` invocation in Claude Code. That
> mirror is **local convenience, never committed** (the doc stays the source of truth).

## Why this fits the repo grain

These commands are **not new behavior** — each codifies a principle already in the constitution, so
the work is packaging + discoverability, not policy:

- `/fib-scope-check` ⟶ [AGENTS.md](../../../AGENTS.md) *Intent alignment over plan inertia* (#35) +
  *Research easy, authority hard*.
- `/absorb-patterns` ⟶ the external-pattern-scan absorption discipline (absorb, never replace).
- `/prepare-job-computer` ⟶ the SONAR / endpoint-protection discipline in
  [CLAUDE.md](../../../CLAUDE.md) (minimize interpreter starts, prefer read-only).
- `/prepare-home-computer` ⟶ the established handoff pattern (branch/sync state, resume commands,
  what-not-to-start).

A versioned doc that any agent reads matches the *agent-native warm context* model
([wiki-is-agent-native](2026-06-17-wiki-is-agent-native.md)) better than a Claude-Code-only,
gitignored slash command.

## What stays non-negotiable

- **Lightweight, not governance.** Each playbook is short and points at the existing principle; it
  must not grow into a heavy gate/packet layer (Lean Fib Research).
- **Source-facit separation, no edge claims, 1H paused, observed/inferred/unverified** carry through
  every command unchanged — the playbooks restate the boundary, they do not relax it.
- **No commit/push without explicit GO**; no auto-fib; no research-code change from this issue.

## The four command contracts (spec for the implementation PR)

Each file: short YAML-ish header (purpose, when-to-use) → numbered steps → required output shape →
explicit non-goals. Keep each well under the corpus ceiling.

### `/fib-scope-check`
- **Purpose:** verify the proposed next step is intent-valid, not just technically valid.
- **Steps:** state (a) the user's actual claim/goal, (b) what question this step answers, (c) are
  they the same — if not, name the mismatch; flag any drift into authority/edge claims, Genesis-v1
  re-patterning, or unnecessary governance; recommend continue / pause-and-ask / reframe.
- **Output:** the four answers + a one-line verdict (`aligned` / `mismatch — reframe` /
  `pause, ask user`).
- **Non-goals:** never used to chase positive results (interlock with *Validity over convenience*).

### `/absorb-patterns`
- **Purpose:** scan external repos/papers/tools for patterns to **strengthen, never replace** this
  repo.
- **Steps:** identify candidates → verify what each actually does (README/code/paper) → map to a
  concrete fib-repo problem → classify ABSORB NOW / STUDY LATER / INSPIRE ONLY / REJECT.
- **Output:** per candidate — source, observed/inferred/unverified, pattern, mapped problem, risks,
  ROI, confidence, next safe step.
- **Non-goals:** no recommendation that replaces the repo, introduces leakage, turns machine labels
  into truth, or adds a heavy dependency without clear ROI.

### `/prepare-home-computer`
- **Purpose:** complete handoff for continuation at home.
- **Output:** branch + sync state, uncommitted/untracked work, current research phase, gates passed,
  known risks, exact resume commands, next safe step, **what NOT to start yet**.
- **Non-goals:** does not push or start new research.

### `/prepare-job-computer`
- **Purpose:** select work suited to the job machine (limited perms, SEP/SONAR sensitivity, resource
  limits).
- **Output:** prefer read-only review / docs / design / audit / small deterministic checks; avoid
  heavy test bursts, long jobs, expensive plotting/data-gen, unnecessary interpreter starts; batch
  gates into one call.
- **Non-goals:** does not trigger long-running or plotting work.

## Layout (implementation PR)

```
docs/agent/commands/
  absorb-patterns.md
  prepare-home-computer.md
  prepare-job-computer.md
  fib-scope-check.md
```
Link the set from [`docs/agent/AGENT_RESPONSE_STYLE.md`](../../agent/AGENT_RESPONSE_STYLE.md) (or a
short `docs/agent/README.md`) and from the wiki `index.md` so agents discover them in one hop.

## Out of scope

No `src/fibengine` behavior change; no auto-fib/edge/trading/ML; `.claude/` policy unchanged
(`.gitignore` + `POLLUTION_GLOBS` stay as-is). Selection-learning and other research lines
unaffected — this is tooling for how agents work, not what they conclude.

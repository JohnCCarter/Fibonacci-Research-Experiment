---
name: pre-compact-checkpoint
description: Preserve verified repo state before context compaction in a long session — a lightweight checkpoint (Observed/Inferred/Unverified + repo state + user constraints + next smallest safe step) so nothing important is lost across a compact/autocompact or a fresh session. Invoke when the session is getting long, when the harness warns compaction is near, or when the user says "checkpoint", "canary", "save state", or "before compact".
allowed-tools: Read, Edit, Write, Bash
---

# Pre-compact checkpoint — don't lose verified state across a compact

Long sessions get compacted (or autocompacted), and the summary can drop hard-won repo decisions,
risks, and user constraints. This skill captures the **verified frontier** *before* that happens, so
the next stretch — same session post-compact, or a fresh one — resumes without re-deriving anything.

Keep it **light**. This is the lean research repo, not a governance regime: a checkpoint is a short
snapshot, not a ceremony. Reuse what already exists — the durable home is
[`handoff.md`](../../../docs/research_wiki/handoff.md) (the editable "resume in one read" snapshot) and
[`log.md`](../../../docs/research_wiki/log.md) (the append-only trail). Distinct from
`/prepare-home-computer` (a *cross-machine* handoff): this is an *in-session, pre-compaction* snapshot.

> **Principle (owner's, verbatim):** *"Välj den enkla ändringen om den ger betydligt mer värde än den
> svåra."* A checkpoint is the simple, high-value move before a big step — but don't let it bloat into
> the hard, heavy thing it's meant to prevent. (Full guardrails:
> [`owner-preferences.md`](../../../docs/research_wiki/owner-preferences.md).)

## When to act (bands are *guidance*, not measured)
Don't claim an exact token count — the harness rarely gives one. Use the band you can infer, a
compaction warning, or the user's word. The point is the *behaviour* at each rough stage:

- **Getting long:** finish the current **atomic** step (leave the tree green, no half-edit — see
  [atomic-runnable-artifacts](../../../docs/research_wiki/concepts/atomic-runnable-artifacts.md)),
  write a checkpoint, then it's safe to compact before starting anything larger.
- **Heavy work pending:** do **not** begin a new large edit / refactor / prereg-affecting change before
  a checkpoint + compact. Small, reversible steps only until then.
- **Long:** **stop implementing.** Refresh the fresh-session resume note
  ([`handoff.md`](../../../docs/research_wiki/handoff.md)) and hand off rather than pushing a big change
  through a strained context.

## The checkpoint (six sections — keep each to a few lines)
Use the repo's honesty ladder (AGENTS.md *Facts vs assumptions*; same Observed/Inferred/Unverified
split as `/chamoun-fib-style-distiller`):

- **Observed** — what is verified true *now* (gates run, files read, command output).
- **Inferred** — reasoned conclusions not yet directly confirmed.
- **Unverified** — assumptions, open questions, anything that *sounds* certain but isn't checked.
- **Repo state** — branch · HEAD SHA · working tree (clean / what's staged) · last gate result.
- **User constraints** — active asks, scope limits, the active protocol (BTC-only, human-fib = facit,
  no auto-fib-as-truth), and the durable guardrails in
  [`owner-preferences.md`](../../../docs/research_wiki/owner-preferences.md) that bear on the work.
- **Next smallest safe step** — the single smallest reversible action that moves the work forward.

For **Repo state**, read git cheaply (git, not a python start — SONAR-safe):
```bash
git rev-parse --short HEAD && git status -sb
```

## Where it goes
1. **Emit the six sections inline** so the user sees the checkpoint.
2. **Overwrite [`handoff.md`](../../../docs/research_wiki/handoff.md)** (branch · HEAD · gates ·
   in-flight · next step · gotchas) — the snapshot a post-compact or fresh session boots from. It
   **syncs via git** to the owner's other surfaces (work · home · iPhone); machine-local memory does
   not travel (see [`owner-preferences.md`](../../../docs/research_wiki/owner-preferences.md)).
3. **Append one dated line to [`log.md`](../../../docs/research_wiki/log.md)** *only* if a durable
   decision/milestone landed (`## [YYYY-MM-DD] decision|maintenance | …`) — not for every checkpoint
   (keep the log signal, not noise).

## Gates & SONAR economy
"Leave the tree green" does **not** mean re-running gates every checkpoint. If you already have a green
[`/run-gates`](../run-gates/SKILL.md) result and have touched nothing since, reuse it — each
`python.exe` start triggers a Symantec SONAR scan (CLAUDE.md Gotchas). Re-run gates only if `*.py`
changed since the last green run, and batch them in the one `/run-gates` call.

## Done = verified state captured · `handoff.md` refreshed · tree left green · no big step taken on a strained context.

_Future option (out of scope here): a `PreCompact` hook in `.claude/settings.json` (hooks live in
[`.claude/hooks/`](../../hooks/)) could auto-suggest this skill near compaction — wire it only if the
manual trigger proves too easy to forget._

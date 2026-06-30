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

## When to act — two triggers, whichever fires first

**Capacity and thread-health are different risks.** The window can sit at 26% and the agent already be
drifting. Checkpoint on **whichever** comes first — and the first one is usually *not* the percentage.

### 1. Thread health (usually earlier — the real reason to checkpoint)
A 1M window is capacity to *read*, not a guarantee everything is *weighted equally*. The thread frays
from **noise, not size**: *lost-in-the-middle* (facts in the middle of a long context get buried),
*recency bias* (early constraints fade as later turns dominate), and *context rot* (superseded plans,
null results, and changed decisions resurface as if still live). This sets in **well before** any %
band and is **invisible in `/context`**. A focused 600k session holds the thread better than a sprawling
150k one — judge by **clutter, not %**. Checkpoint + re-anchor when you notice any of:
- several topic switches, or a long-abandoned plan still sitting in context;
- large stale tool-output dumps competing with the live state;
- you are re-deriving or re-confirming something already settled this session;
- a contradiction between an earlier decision and the current one.

The fix is the checkpoint's own job: restating the salient state **last** (so recency works *for* you)
and keeping superseded material out of the window (`archive/`, `.rgignore`, no broad reads).

### 2. Capacity — the hook pings at the sweet spot (~25%)
A `UserPromptSubmit` hook ([`pre-compact-checkpoint.sh`](../../hooks/pre-compact-checkpoint.sh)) reads
the transcript's latest usage (`input + cache_read + cache_creation` = real tokens sent — the same
figure `/context` shows) and **auto-injects one reminder when context crosses ~25% of a 1M window
(250k)** — the sweet spot to checkpoint *in time*, before drift/compaction lose detail. **When that
ping arrives, do the checkpoint.** It is a reminder only — it never invokes this skill, so you still run
it; it fires **once per session**. Tune the single `CONTEXT_THRESHOLD` constant in the script (lower it
on a smaller-window model — `/context` shows the live %); use **%**, not an absolute count, when
reasoning about it, since 250k is ~25% on 1M but the whole window on a 256k model.

**Hard stop:** near **~90%** (autocompact imminent) **stop implementing**, refresh
[`handoff.md`](../../../docs/research_wiki/handoff.md), and hand off rather than push a big change
through a strained context.

> The token figure is the **window snapshot**, not cumulative session spend — a long session reads tens
> of millions of cheap *cache* tokens while the window sits low. Pace on the window % **and** thread
> health, never on the scary cumulative total.

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

_Wired (2026-06-30): the manual trigger proved too easy to forget (a long session drifted ~7 topic
switches without a checkpoint), so a `UserPromptSubmit` hook
([`pre-compact-checkpoint.sh`](../../hooks/pre-compact-checkpoint.sh), registered in
[`.claude/settings.json`](../../settings.json)) now auto-pings once at ~25% context — the early/in-time
trigger. A hook can only **remind**, never invoke this skill, so you still run it. The late `PreCompact`
event was rejected: it fires only at compaction, too late for the sweet spot._

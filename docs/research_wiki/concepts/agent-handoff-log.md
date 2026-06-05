# Agent Handoff And Log

The handoff/log pattern makes future sessions faster. The goal is to preserve
what changed, why it matters, what remains open, and what must not be
misinterpreted.

## Two Surfaces

- [log.md](../log.md) is append-only history: ingests, decisions, reviews,
  questions, and maintenance.
- [handoff.md](../handoff.md) is current working context: recent state,
  next actions, blockers, and guardrails.

## When To Update

Update the handoff after:

- a meaningful research decision.
- a generated review pack or manual smoke review.
- a new source ingest.
- a broad refactor or architecture change.
- a new blocker or risk.

Append to `log.md` for the event trail. Edit `handoff.md` for current state.

## What To Capture

- Current focus.
- Recent changes.
- Open questions.
- Next useful action.
- Verification status.
- Known risks and guardrails.

## Guardrails

The handoff is not source of truth for behavior. It points to source docs, code,
issues, labels, and experiment artifacts.

## Template

Use [handoff-entry.md](../templates/handoff-entry.md) for handoff sections or
session notes.

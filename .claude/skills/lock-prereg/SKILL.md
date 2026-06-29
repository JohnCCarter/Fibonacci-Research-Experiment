---
name: lock-prereg
description: Lock a signed-off pre-registration — add the immutability sentinel and split post-lock material into a *-postlock.md sibling. Use ONLY after the human signs off a prereg. User-only (it changes the registration's status).
disable-model-invocation: true
allowed-tools: Read, Edit, Write, Bash
---

# Lock pre-registration

Perform the lock ritual on a prereg under `docs/research_wiki/reviews/*-prereg-*.md`, **after** the
human has signed off. The lock makes the registration immutable so a result can never be edited
against its own question/baselines/decision-rule (AGENTS.md *Research easy, authority hard*). The
companion guard `.claude/hooks/guard-locked-prereg.sh` will ask before any later edit to a locked file.

## Steps

1. **Confirm sign-off.** Do not lock without explicit human sign-off. If unclear, stop and ask. State
   which prereg file you are locking.
2. **Verify it is not already locked.** Grep the file for `prereg:locked`. If present, it is already
   locked — stop (edit the `*-postlock.md` sibling instead).
3. **Add the sentinel** at the very top of the prereg (before the first `#` heading):
   ```
   <!-- prereg:locked -->
   <!-- This file is immutable after lock. Run results / addenda go in the *-postlock.md sibling.
        A PreToolUse hook (.claude/hooks/guard-locked-prereg.sh) asks before any Edit/Write here. -->
   ```
4. **Create the postlock sibling** `<same-basename>-postlock.md` next to the prereg, with a header
   explaining it is the append-only companion to the immutable prereg.
5. **Move all post-lock material** (run results, addenda, sign-off status, unrun baselines) out of the
   prereg and into the sibling. In the prereg, replace it with a short `## Post-lock addenda` section
   that points to the sibling. The locked prereg keeps only the pre-run registration.
6. **Stamp the lock** in the prereg's status line: `LOCKED <date> (human sign-off)`.

## Guardrails

- Never edit the question, baselines, or decision rule while locking — only move post-lock content and
  add the sentinel. If the registration itself is wrong, that is a new prereg, not an edit.
- The sibling is intentionally **unguarded** (the hook skips `*-postlock.md`) so results can be appended.
- After locking, run `/run-gates` (or at least `wiki_lint.py`) so no dead links were introduced by the
  split.

## Reference

This codifies the lock applied to `btc-fib-daily-wick-pair-anchor-prereg-20260629.md` (+ its
`-postlock.md` sibling). See AGENTS.md *Research easy, authority hard* for the binding rule.

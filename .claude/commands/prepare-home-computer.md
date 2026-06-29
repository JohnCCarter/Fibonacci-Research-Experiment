---
description: Produce a complete handoff for continuation on the home computer.
---

# `/prepare-home-computer`

**Purpose:** produce a complete handoff so work continues cleanly on the home computer.
**When to use:** before switching machines, or when the user asks for a home-handoff.
**Codifies:** the established handoff pattern (what travels via `git pull`, what does not).

## Output (the handoff report)

1. **Branch + sync state** — current branch, `local == origin` or ahead/behind, unpushed commits.
2. **Uncommitted / untracked work** — `git status -sb`; flag anything not yet on origin.
3. **Current research phase** — one line, link to [handoff.md](../../docs/research_wiki/handoff.md).
4. **Gates passed** — ruff / format / bounds / wiki-lint / pytest + CI run-id & status.
5. **Known risks / blockers** (e.g. CI billing lock, deferred caches).
6. **Resume commands** (copy-pasteable):
   `git pull` · `uv sync --extra dev` · `uv run --no-sync pytest -q` ·
   `uv run --no-sync python scripts/check_repo_bounds.py`.
7. **Next safe step** and, explicitly, **what NOT to start yet** (gated tracks need separate GO).
8. **Local-only state** — note that `data/raw/`, `experiments/review/`, and `.claude/settings.local.json`
   are gitignored / regenerable and do **not** travel; say whether any must be re-fetched/regenerated
   at home. (The `/` commands, hooks, and `settings.json` under `.claude/` **do** travel via git.)
9. **`/` commands travel via git** — `.claude/commands/`, `.claude/hooks/`, and `.claude/settings.json`
   are versioned, so `git pull` brings them to the home computer; the slash commands appear in Claude
   Code's `/` picker after a session restart. No `cp` materialization step is needed anymore.

## Non-goals

- Does **not** push or start new research — it only reports state and the safe resume path.

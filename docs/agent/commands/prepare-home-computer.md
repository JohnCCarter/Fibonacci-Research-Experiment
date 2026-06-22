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
3. **Current research phase** — one line, link to [handoff.md](../../research_wiki/handoff.md).
4. **Gates passed** — ruff / format / bounds / wiki-lint / pytest + CI run-id & status.
5. **Known risks / blockers** (e.g. CI billing lock, deferred caches).
6. **Resume commands** (copy-pasteable):
   `git pull` · `uv sync --extra dev` · `uv run --no-sync pytest -q` ·
   `uv run --no-sync python scripts/check_repo_bounds.py`.
7. **Next safe step** and, explicitly, **what NOT to start yet** (gated tracks need separate GO).
8. **Local-only state** — note that `.claude/`, `data/raw/`, `experiments/review/` are gitignored /
   regenerable and do **not** travel; say whether any must be re-fetched/regenerated at home.
9. **Re-create the `/` commands** — the local slash-command mirror lives in gitignored `.claude/` and
   does not travel. On the home computer, materialize it from this versioned source in one line:
   ```bash
   mkdir -p .claude/commands && cp docs/agent/commands/{absorb-patterns,fib-scope-check,prepare-home-computer,prepare-job-computer}.md .claude/commands/
   ```
   Then `/fib-scope-check`, `/absorb-patterns`, `/prepare-home-computer`, `/prepare-job-computer`
   appear in Claude Code's `/` picker (restart the session if not picked up immediately).

## Non-goals

- Does **not** push or start new research — it only reports state and the safe resume path.

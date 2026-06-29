---
name: run-gates
description: Run the full project gate suite (ruff lint, ruff format check, repo-bounds, wiki-lint, pytest) in ONE SONAR-economical command. Use after code/doc changes, before committing, or when asked to verify the repo is green.
allowed-tools: Bash
---

# Run gates

Run **all** gates in a **single Bash call**, chained with `&&`, to minimize interpreter starts —
each `python.exe` launch triggers a Symantec SONAR scan on this machine (see CLAUDE.md Gotchas).
**Never** run the gates one-by-one in separate calls, and don't re-run them needlessly.

```bash
uv run --no-sync ruff check src tests \
  && uv run --no-sync ruff format --check src tests \
  && uv run --no-sync python scripts/check_repo_bounds.py \
  && uv run --no-sync python scripts/wiki_lint.py \
  && uv run --no-sync pytest -q
```

## Notes

- `uv run --no-sync` (not bare `uv run`) skips the `.venv` rebuild that Symantec Auto-Protect would
  otherwise scan. Run `uv sync --extra dev` once per machine first.
- **pytest is the slow gate** (~2–3 min, 600+ tests, coverage gate 60% via `pyproject.toml addopts`).
  If you only changed docs/config and no `*.py`, the first four gates suffice — pytest can be skipped
  (the pre-commit `pytest` hook is itself gated to `^(src/|tests/).*\.py$`). For a long run, launch it
  with `run_in_background`.
- `&&` short-circuits: the first failing gate stops the chain. Order is cheap→expensive on purpose, so
  a lint/bounds failure surfaces before you spend the pytest minutes.
- These mirror CI (`.github/workflows/ci.yml`) and the local pre-commit hooks; green here ≈ green in CI.

## Order rationale

ruff (fast) → format (fast) → bounds (fast) → wiki-lint (fast) → pytest (slow). Fail fast on the
cheap checks before paying for the test suite.

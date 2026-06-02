# repository-layout-policy.md

Repository layout policy for this repo. Scope: structure, naming, placement,
indexing, archiving, and maintainability. Not scope: research governance.

Goals:
- logiskt
- organiserat
- kategoriserat
- spårbart
- återfinnbart
- reproducerbart
- underhållbart

If repository reality changes, update this policy first, then move files.

---

## 1) Design principles

1. One canonical location per artifact type.
2. File paths should be predictable from purpose.
3. Active surfaces and archived surfaces must be separated.
4. Index/README files are mandatory on key surfaces.
5. Layout rules must be enforceable by tooling (`check_repo_bounds.py` + CI).

---

## 2) Repository map (canonical paths)

| Path | Purpose | Versioned |
|---|---|---|
| `src/fibengine/` | Source code: runtime, research tooling, labeling, validation | Yes |
| `tests/` | Test suite | Yes |
| `config/` | Baseline config + docs | Yes |
| `config/variants/` | Alternative config profiles | Yes |
| `data/labels/` | Active label data | Yes |
| `data/raw/` | Cached market data | No (gitignored data files) |
| `data/screenshots/` | Screenshot references | No (gitignored image files) |
| `experiments/results/` | Append-only ledgers | Yes |
| `experiments/runs/` | Per-run audit folders | Selective |
| `experiments/label_review/` | Review checkpoints | Yes |
| `docs/` | Long-lived documentation | Yes |
| `premortem/` | Premortem and reflections | Yes |
| `archive/` | Historical/legacy material | Yes |
| `tmp/` | Temporary work | Optional |

---

## 3) Root allowlist (MUST)

Versioned top-level files should be limited to:
- `README.md`
- `repository-layout-policy.md`
- `AGENTS.md`
- `pyproject.toml`
- `uv.lock`
- `.gitignore`
- `.pre-commit-config.yaml`

Top-level directories should be canonical repo surfaces from section 2.
No loose temporary artifacts at root; use `tmp/`.
Ignored local/tooling artifacts such as `.venv/`, `.pytest_cache/`, `.ruff_cache/`,
`.coverage`, and local editor folders are not canonical repo surfaces.

---

## 4) Naming and path conventions

### Code and tests
- Code files: `snake_case.py`
- Tests: `tests/**/test_<module>.py`

### Labels
- Active labels: `data/labels/{exchange}/{symbol-with-dash}/{timeframe}.json`
- Legacy or old exchange datasets should be moved to `archive/`.

### Runs and batches
- Runs: `experiments/runs/{kind}/{YYYY-MM-DD}/{run_id}/`
- Batch id: `YYYY-MM-DD_<short-description>`

---

## 5) Required repository surfaces (MUST)

### Required directories
- `data/raw/`
- `data/screenshots/`
- `experiments/runs/`
- `data/labels/`
- `experiments/label_review/`
- `config/variants/`

### Required README/INDEX files
- `data/raw/README.md`
- `data/raw/INDEX.md`
- `data/screenshots/README.md`
- `data/screenshots/INDEX.md`
- `experiments/runs/README.md`
- `experiments/runs/INDEX.md`
- `experiments/results/README.md`
- `data/labels/README.md`
- `data/labels/INDEX.md`
- `experiments/label_review/README.md`
- `experiments/label_review/INDEX.md`
- `config/variants/README.md`
- `config/variants/INDEX.md`
- `archive/README.md`
- `archive/INDEX.md`

Missing required docs should be created as lightweight stubs.
`data/raw/` and `data/screenshots/` may ignore data/image files, but their
`README.md` and `INDEX.md` files should remain versioned.

---

## 6) Size and anti-blob policy (MUST)

Enforced by `scripts/check_repo_bounds.py`.

| Pattern | Max lines | Max bytes |
|---|---:|---:|
| `premortem/reflections/*.md` | 80 | 8 KiB |
| `src/fibengine/**/*.py` | 400 | 25 KiB |
| `tests/**/*.py` | 250 | 15 KiB |
| `docs/**/*.md` | 300 | 20 KiB |
| `scripts/*.py` | 120 | 8 KiB |

Grandfathered oversized files may exist but should not grow.

---

## 7) Active vs archived data

- Active paths should represent current workflow.
- Historical or replaced data/docs belong in `archive/`.
- Archive moves must preserve context in the path (source surface, domain).
- After moving to archive, update references/indexes on active surfaces.

---

## 8) Critical path map (grounded names)

The following module names/paths are considered critical and should only be
renamed together with policy/doc updates:

- `src/fibengine/core/fib.py`
- `src/fibengine/research/level_events.py`
- `src/fibengine/labeling/tool.py`
- `src/fibengine/labeling/human_fib.py`
- `src/fibengine/labeling/human_fib_events.py`

---

## 9) Validation checklist for layout changes

When changing structure:
1. Move files with `git mv` (keep history).
2. Update affected `README.md` / `INDEX.md`.
3. Update path references in docs/scripts.
4. Run:
   - `uv run python scripts/check_repo_bounds.py`
   - `uv run pytest -q`
5. Ensure no stale references remain (e.g., `rg "<old-path>"`).

---

## 10) Change policy

This policy governs repository layout only.
Do not place research decision-making rules here; keep those in docs dedicated
to research workflow/hypotheses.
# Contributing / quality gate

Kör detta **innan commit och push** (lokalt samma som CI).

## Setup (en gång per klon)

```bash
uv sync --extra dev
uv run pre-commit install
```

## Manuell check

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest -q
```

Eller allt via pre-commit:

```bash
uv run pre-commit run --all-files
```

## CI

GitHub Actions workflow: `.github/workflows/ci.yml` (ruff + pytest på push/PR mot `main`).

## Commit-disciplin

- Logiska, små commits (en kategori i taget: docs, struktur, features, data).
- `uv run pytest` grönt innan push.
- Baseline `config/settings.yaml` ändras bara via Promotion-gate (`docs/FIB_BACKTEST_PLAN.md` fas 7).
- **Filstorlek:** `uv run python scripts/check_repo_bounds.py` (reflektioner, `src/`, `tests/`, `docs/`).
  Se `repository-layout-policy.md` §2B — inga monoliter eller blobs.

# tests

Testsvit som speglar strukturen i `src/fibengine/`.

## Struktur

- `core/` tester för `src/fibengine/core/`.
- `data/`, `pivots/`, `labeling/`, `evaluation/`, `backtest/`, `sizing/`, `viz/`
  testar respektive subpaket.
- `conftest.py` innehåller gemensamma fixtures/hjälpare.

Kör alla tester med:

```bash
uv run pytest
```

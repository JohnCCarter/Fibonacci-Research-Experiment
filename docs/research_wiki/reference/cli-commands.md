# CLI Commands

Common repo commands. Run from the repo root.

## Quality Gate

```bash
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest -q
uv build
```

Optional full local hook pass:

```bash
uv run pre-commit run --all-files
```

## Data

```bash
uv run python -m fibengine.data.fetch
uv run python -m fibengine.data.fetch --refresh
uv run python -m fibengine.data.fetch --labeling-set --refresh
```

## Experiment

```bash
uv run python -m fibengine.experiment
```

## Human Fib

```bash
uv run python -m fibengine.labeling.human_fib --show <annotation.json>
uv run python -m fibengine.labeling.human_fib_events --fib <fib_id>.json
```

## External model (optional)

```bash
# PowerShell: $env:NVIDIA_API_KEY = "nvapi-..."
uv run python scripts/nvidia_qwen_smoke.py
```

See [nvidia-qwen-api.md](nvidia-qwen-api.md).

## Review

```bash
uv run python -m fibengine.research.human_review_level_events --max-events 40 --seed 7
uv run python -m fibengine.research.human_review_level_events \
  --human-fib-events data/labels/human_fib/bitfinex/BTC-USD/1d/<fib_id>_events.json
uv run python -m fibengine.research.level_event_review_tool \
  --run-dir experiments/review/fib_level_events/<run_id>
```

## Source Links

- [Contributing](../../CONTRIBUTING.md)
- [Level event human review](../../LEVEL_EVENT_HUMAN_REVIEW.md)
- [Human fib annotation](../../HUMAN_FIB_ANNOTATION.md)

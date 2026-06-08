---
name: validation
version: "1.0.0"
description: Validation and testing workflows for the Fibonacci research engine
license: Apache-2.0
metadata:
 author: Fibonacci Research Team
 tags:
 - validation
 - testing
 - verification
---

# Validation Skill

This skill provides guidance for validating the Fibonacci research engine through testing and verification workflows.

## Before You Start

Ensure you have the proper environment set up:
- Python 3.11+
- Required packages installed via `uv sync --extra dev`

## Validation Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test suites
uv run pytest tests/core/
uv run pytest tests/backtest/
uv run pytest tests/data/
uv run pytest tests/evaluation/
uv run pytest tests/labeling/
uv run pytest tests/pivots/
uv run pytest tests/sizing/
uv run pytest tests/viz/
```

## Core Principle

Validation ensures the implementation matches the intended behavior and maintains correctness as changes are made.

## Test Structure

The test suite is organized to mirror the source code structure:
- `tests/core/` - Core domain logic tests
- `tests/backtest/` - Backtesting functionality tests  
- `tests/data/` - Data loading and processing tests
- `tests/evaluation/` - Evaluation metric tests
- `tests/labeling/` - Labeling tool tests
- `tests/pivots/` - Pivot detection tests
- `tests/sizing/` - Sizing calculation tests
- `tests/viz/` - Visualization tests

## Key Validation Patterns

### Label Validation

```python
# Check that human labels match expected format and coverage
def validate_labels():
    """
    Validate that human labels meet quality standards:
    - Sufficient coverage across markets/timeframes
    - Proper annotation according to guidelines
    - Consistent with agreement metrics
    """
    pass
```

### Machine Label Validation

The system validates that machine-generated candidates are properly reviewed before being used in evaluation:

```python
# Machine labels are excluded from recall/agreement metrics to prevent circular evaluation
# They are only used as candidates for human review, not as facit
```

## Common Validation Tasks

### Checking Label Coverage

```bash
# Generate worklist to see what needs labeling
uv run python -m fibengine.labeling.worklist
```

### Validation Rules

1. **Machine labels must be reviewed**: Machine-generated candidates require human verification
2. **No automatic acceptance**: Machine labels are never automatically treated as facit
3. **Coverage targets**: Aim for 20-30 human labels per market/timeframe combination

## Reference Files

- `docs/HUMAN_FIB_ANNOTATION.md` - Human annotation guidelines
- `docs/LEVEL_EVENTS.md` - Level event definitions
- `docs/GENESIS_BITFINEX_VALIDATE.md` - Validation procedures

## External Documentation

- Testing documentation in `docs/CONTRIBUTING.md`
- Quality gates in `pyproject.toml`
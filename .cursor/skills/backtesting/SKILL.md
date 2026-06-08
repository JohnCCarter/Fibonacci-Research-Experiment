---
name: backtesting
version: "1.0.0"
description: Backtesting framework and analysis for swing detection algorithms
license: Apache-2.0
metadata:
 author: Fibonacci Research Team
 tags:
 - backtesting
 - evaluation
 - validation
---

# Backtesting Skill

This skill provides guidance for running and analyzing backtests in the Fibonacci research project.

## Before You Start

Ensure you have the proper environment set up:
- Python 3.11+
- Required packages installed via `uv sync --extra dev`

## Backtesting Workflow

### Running Basic Backtests

```bash
# Run the main experiment pipeline
uv run python -m fibengine.experiment

# Run backtesting
uv run python -m fibengine.backtest.runner

# Run backtest matrix analysis
uv run python -m fibengine.backtest.matrix
```

## Core Principle

Backtesting measures the **stability** of swing selection over time, not profitability. The goal is to ensure that the algorithm produces consistent results across different time periods.

## Key Metrics

### Stability Metrics
- `flip_rate` - Measures how often the selected swing changes
- `extension_rate` - Measures how often a swing endpoint grows incrementally
- `confirmed_rate` - Measures how often selected swings are confirmed
- `endpoint_drift` - Measures how much swing endpoints move when recalculated

### Walk-forward Analysis
The system uses causal backtesting where at each cursor position, swings are selected using only data available up to that point.

## Backtest Configuration

```yaml
backtest:
  gate_min_confirmed_rate: 0.8
  gate_max_endpoint_drift_bars: 2.0
  gate_min_direction_consistency: 0.7
```

## Running Stability Analysis

```python
# Example backtest configuration
from fibengine.config.settings import BACKTEST_SETTINGS

def run_stability_analysis():
    """
    Run a comprehensive stability analysis to evaluate how consistent 
    the swing selection algorithm is over time.
    """
    pass
```

## Analysis Patterns

### Evaluating Results

```python
# Check the ledger for results
import pandas as pd
results = pd.read_json("experiments/results/leaderboard.jsonl", lines=True)

# Key columns to analyze:
# - symbol_timeframe: Which market and timeframe was tested
# - stability_gate_passed: Whether it passed stability checks
# - mean_endpoint_drift_bars: Average movement of endpoints
# - flip_rate: How often swings change selection
# - confirmed_rate: How often swings are confirmed
```

## Troubleshooting Backtests

### Common Issues

1. **Low confirmation rates** may indicate the algorithm is selecting swings too early
2. **High endpoint drift** suggests swings are not stable over time
3. **Low direction consistency** may indicate sensitivity to recent price action

## Reference Files

- `docs/validate/FIB_BACKTEST_PLAN.md` - Backtesting methodology
- `docs/research/LEVEL_EVENTS.md` - Level event definitions  
- `experiments/results/leaderboard.jsonl` - Main results ledger
- `config/settings.yaml` - Configuration with backtest gates

## External Documentation

- Backtest documentation in `docs/validate/FIB_BACKTEST_PLAN.md`
- Stability metrics in `docs/research/LEVEL_EVENTS.md`
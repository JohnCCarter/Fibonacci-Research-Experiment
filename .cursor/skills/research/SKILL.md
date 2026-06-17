---
name: research
version: "1.0.0"
description: Research experimentation and hypothesis testing workflows
license: Apache-2.0
metadata:
 author: Fibonacci Research Team
 tags:
 - research
 - experimentation
 - hypothesis-testing
---

# Research Skill

This skill provides guidance for conducting research experiments and hypothesis testing in the Fibonacci research project.

## Before You Start

Ensure you have the proper environment set up:
- Python 3.11+
- Required packages installed via `uv sync --extra dev`

## Research Workflow

### Planning Experiments

Before running experiments, consider:
1. **Research question**: What are you trying to learn or validate?
2. **Hypothesis**: What do you expect to observe?
3. **Metrics**: How will you measure success?
4. **Controls**: What conditions should remain constant?

### Running Experiments

```bash
# Run the main experiment pipeline
uv run python -m fibengine.experiment

# Run with specific configuration
uv run python -m fibengine.experiment --config config/variants/my_experiment.yaml
```

## Core Principle

Research in this project follows an iterative approach:
1. Formulate a hypothesis about swing selection behavior
2. Implement the change
3. Test against human labels
4. Measure stability and agreement
5. Refine or reject the hypothesis

## Experiment Structure

### Configuration Files

Create experiment configurations in `config/variants/`:

```yaml
# Example: config/variants/aggressive_swing_detection.yaml
pivots:
  mode: fractal
  fractal_n: 3  # More sensitive fractal detection

scoring:
  structure_weight: 0.7
  confluence_weight: 0.3
  prominence_weight: 0.0
```

## Key Research Patterns

### A/B Testing

Compare different algorithm variants:

```python
# Run experiment with baseline configuration
baseline_results = run_experiment("config/settings.yaml")

# Run experiment with variant configuration  
variant_results = run_experiment("config/variants/my_variant.yaml")

# Compare results
compare_results(baseline_results, variant_results)
```

### Hypothesis Formation

Good research hypotheses for this project:
- "Increasing the confluence weight will improve agreement with human labels"
- "Using a longer lookback period for structure detection will reduce false positives"
- "Adding volume confirmation will improve stability"

## Documentation

All research should be documented in the research wiki:
- `docs/research_wiki/` - Main documentation
- `docs/research_wiki/log.md` - Research log entries
- `docs/research_wiki/handoff.md` - Current research focus

## Reference Files

- `docs/research_wiki/index.md` - Research wiki index
- `docs/research/MTF_DAILY_RESEARCH.md` - Multi-timeframe research approach
- `docs/validate/FIB_BACKTEST_PLAN.md` - Backtesting methodology

## External Documentation

- Research methodology in `docs/research/RESEARCH_HANDOFF.md`
- Experiment tracking in `experiments/results/`
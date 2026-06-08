---
name: optimization
version: "1.0.0"
description: Parameter optimization for swing detection algorithms using GPU-accelerated solvers
license: Apache-2.0
metadata:
 author: Fibonacci Research Team
 tags:
 - optimization
 - parameters
 - cuopt
 - gpu
 - linear-programming
 - quadratic-programming
---

# Optimization Skill

This skill provides guidance for optimizing parameters in the Fibonacci swing selection algorithms using GPU-accelerated solvers.

## Before You Start

Ensure you have the proper environment set up:
- Python 3.11+
- Required packages installed via `uv sync --extra dev`
- GPU availability for acceleration

## Choosing LP vs MILP vs QP

**Decide from the objective and variables:**

| If the objective is... | And variables are... | Use |
|---|---|---|
| Linear (sum of `c_i * x_i`) | All continuous | **LP** |
| Some integer or binary | **MILP** |
| Has squared (`x*x`) or cross (`x*y`) terms | **QP** |

## Problem Formulation for Fibonacci Algorithms

### Scoring Function Optimization (LP)

```python
# Example: Optimize weights for different scoring components
from fibengine.optimization.problem import Problem, CONTINUOUS, MAXIMIZE

problem = Problem("ScoreWeights")

# Decision variables for scoring weights
structure_weight = problem.addVariable(lb=0, ub=1, vtype=CONTINUOUS, name="structure")
confluence_weight = problem.addVariable(lb=0, ub=1, vtype=CONTINUOUS, name="confluence")
prominence_weight = problem.addVariable(lb=0, ub=1, vtype=CONTINUOUS, name="prominence")

# Constraints based on domain knowledge
problem.addConstraint(structure_weight + confluence_weight + prominence_weight == 1, 
                     name="weight_sum")
problem.addConstraint(structure_weight >= 0.2, name="min_structure")
problem.addConstraint(confluence_weight <= 0.5, name="max_confluence")

# Objective: maximize agreement with human labels
# This would be computed from backtesting results
problem.setObjective(
    0.8*structure_weight + 0.15*confluence_weight + 0.05*prominence_weight, 
    sense=MAXIMIZE
)
```

### Threshold Optimization (MILP)

```python
# Example: Optimize discrete thresholds for swing detection
from fibengine.optimization.problem import Problem, INTEGER, CONTINUOUS, MINIMIZE

problem = Problem("ThresholdOptimization")

# Binary variable for threshold selection
use_high_threshold = problem.addVariable(lb=0, ub=1, vtype=INTEGER, name="use_high")

# Continuous variables for actual threshold values
threshold_value = problem.addVariable(lb=0.01, ub=0.1, vtype=CONTINUOUS, name="threshold")

# Linking constraint: threshold depends on selection
M = 1000  # Big-M constant
problem.addConstraint(threshold_value <= 0.05 + M * use_high_threshold)

# Objective: minimize false positives and false negatives
# Based on backtesting results
```

## Quick Reference: API

### Basic LP Example

```python
from fibengine.optimization.problem import Problem, CONTINUOUS, MAXIMIZE, MINIMIZE
from fibengine.optimization.solver_settings import SolverSettings

# Create problem
problem = Problem("MyOptimization")

# Decision variables
x = problem.addVariable(lb=0, vtype=CONTINUOUS, name="x")
y = problem.addVariable(lb=0, vtype=CONTINUOUS, name="y")

# Constraints
problem.addConstraint(2*x + 3*y <= 120, name="resource_a")
problem.addConstraint(4*x + 2*y <= 100, name="resource_b")

# Objective
problem.setObjective(40*x + 30*y, sense=MAXIMIZE)

# Solve
settings = SolverSettings()
settings.set_parameter("time_limit", 60)
problem.solve(settings)

# Check status
if problem.Status.name in ["Optimal", "PrimalFeasible"]:
    print(f"Objective: {problem.ObjValue}")
    print(f"x = {x.getValue()}")
    print(f"y = {y.getValue()}")
```

## CRITICAL: Status Checking

**Status values use PascalCase, NOT ALL_CAPS:**

```python
# ✅ CORRECT
if problem.Status.name in ["Optimal", "FeasibleFound"]:
    print(problem.ObjValue)

# ❌ WRONG - will silently fail!
if problem.Status.name == "OPTIMAL":  # Never matches!
    print(problem.ObjValue)
```

## Common Modeling Patterns

### Weight Constraints
```python
# Ensure weights sum to 1
weights = [problem.addVariable(lb=0, ub=1, vtype=CONTINUOUS) for _ in range(n)]
problem.addConstraint(sum(weights) == 1)
```

### Parameter Bounds
```python
# Constrain parameters to reasonable ranges
param = problem.addVariable(lb=0.1, ub=2.0, vtype=CONTINUOUS, name="sensitivity")
```

## Solver Settings

```python
settings = SolverSettings()
settings.set_parameter("time_limit", 120)  # 2 minute limit
settings.set_parameter("relative_gap", 0.01)  # 1% optimality gap
```

## Common Issues

| Problem | Likely Cause | Fix |
|---------|--------------|-----|
| Status never "OPTIMAL" | Using wrong case | Use `"Optimal"` not `"OPTIMAL"` |
| Slow solve | Large problem | Set time limit, increase gap tolerance |
| Infeasible | Conflicting constraints | Check constraint logic |

## Reference Models

All reference models should be stored in `references/optimization/` directory.

## When to Escalate

Use troubleshooting and diagnostic guidance if:
- Infeasible and you can't determine why
- Numerical issues
- Performance problems with large constraint sets
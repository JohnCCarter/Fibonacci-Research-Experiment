---
name: data-analysis
version: "1.0.0"
description: Data processing and analysis workflows for financial time series using GPU acceleration
license: Apache-2.0
metadata:
 author: Fibonacci Research Team
 tags:
 - data-analysis
 - time-series
 - gpu
 - pandas
 - cudf
---

# Data Analysis Skill

This skill provides guidance for working with financial time series data in the Fibonacci research project. It covers data loading, preprocessing, feature engineering, and analysis workflows.

## Before You Start

Ensure you have the proper environment set up:
- Python 3.11+
- Required packages installed via `uv sync --extra dev`
- GPU availability (optional but recommended)

## Choosing the Right Data Processing Path

### Path 1: Standard pandas (CPU-based)
Use for small datasets (< 100K rows) or when GPU is not available:

```python
import pandas as pd

# Load data
df = pd.read_parquet("data/raw/btc_1w.parquet")

# Basic operations
result = df.groupby("date").agg({"close": "mean"})
```

### Path 2: cuDF GPU DataFrames (GPU-accelerated)
Use for large datasets or performance-critical operations:

```python
import cudf

# Load data directly to GPU
df = cudf.read_parquet("data/raw/btc_1w.parquet")

# GPU-accelerated operations
result = df.groupby("date").agg({"close": "mean"})
```

## Critical Rules

1. **Size gate: 100K rows minimum for GPU.** Below that, GPU transfer overhead usually beats the speedup.
2. **Keep conversions at boundaries.** Use `.to_pandas()` only at the very end for display or CPU-only libraries.
3. **Validate semantics on representative slices.** For null handling, joins, time series, or grouped logic, keep a small pandas reference path.

## Data Loading Patterns

### Loading Raw Candle Data

```python
from fibengine.data.load import load_candles

# Load candles with automatic caching
df = load_candles("BITFINEX:BTCUSD", "1w", start_date="2020-01-01")
```

### Working with Time Series Data

```python
import pandas as pd

# Load data with proper datetime handling
df = pd.read_parquet("data/raw/btc_1w.parquet")
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date").sort_index()

# Resampling for multi-timeframe analysis
daily_df = df.resample("1D").agg({
    "open": "first",
    "high": "max",
    "low": "min", 
    "close": "last",
    "volume": "sum"
})
```

## Feature Engineering

### Creating Technical Indicators

```python
# Moving averages
df["sma_20"] = df["close"].rolling(window=20).mean()
df["sma_50"] = df["close"].rolling(window=50).mean()

# RSI
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df["rsi"] = calculate_rsi(df["close"])
```

## Troubleshooting

**No speedup vs pandas:**
- Data < 100K rows? GPU overhead dominates.
- Check that cuDF operations are actually running on GPU.

**Memory Issues:**
- Use chunking for very large datasets
- Consider using `cudf.set_option("spill", True)` for GPU memory management

**Wrong Results vs Pandas:**
- Null/NaN handling differs between pandas and cuDF
- Sort stability differs (cuDF is not stable by default)
- Use validation against pandas reference for critical operations

## Reference Files

- `docs/research/LEVEL_EVENTS.md` - Level event definitions
- `docs/labeling/HUMAN_FIB_ANNOTATION.md` - Human annotation guidelines
- `docs/validate/FIB_BACKTEST_PLAN.md` - Backtesting methodology

## External Documentation

- **cuDF Documentation:** https://docs.rapids.ai/api/cudf/stable/
- **Pandas Documentation:** https://pandas.pydata.org/docs/
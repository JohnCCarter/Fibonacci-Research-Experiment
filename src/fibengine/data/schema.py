"""Pandera-schema för OHLCV-candles."""

from __future__ import annotations

import pandera as pa
import pandas as pd

_CANDLE_SCHEMA = pa.DataFrameSchema(
    columns={
        "open": pa.Column(float, nullable=False),
        "high": pa.Column(float, nullable=False),
        "low": pa.Column(float, nullable=False),
        "close": pa.Column(float, nullable=False),
        "volume": pa.Column(float, checks=pa.Check.ge(0), nullable=False),
    },
    index=pa.Index(pa.DateTime, nullable=False, coerce=True),
    checks=[
        pa.Check(
            lambda df: df.index.is_monotonic_increasing,
            error="timestamp index must be sorted ascending",
        ),
        pa.Check(
            lambda df: not df.index.has_duplicates,
            error="timestamp index must be unique",
        ),
        pa.Check(
            lambda df: (df["high"] >= df[["open", "close", "low"]].max(axis=1)).all(),
            error="high must be >= open, close, and low",
        ),
        pa.Check(
            lambda df: (df["low"] <= df[["open", "close", "high"]].min(axis=1)).all(),
            error="low must be <= open, close, and high",
        ),
    ],
    coerce=True,
    strict=False,
)


def validate_candles(df: pd.DataFrame) -> pd.DataFrame:
    """Validera standard-OHLCV innan resten av pipelinen använder dem."""
    return _CANDLE_SCHEMA.validate(df)

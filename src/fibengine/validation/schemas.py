"""OHLCV DataFrame schema and small pydantic models for provenance / review rows."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import pandera as pa
from pydantic import BaseModel, Field

OHLCV_COLUMNS = ("open", "high", "low", "close", "volume")

OHLCV_SCHEMA = pa.DataFrameSchema(
    {
        "open": pa.Column(float, checks=pa.Check.gt(0)),
        "high": pa.Column(float, checks=pa.Check.gt(0)),
        "low": pa.Column(float, checks=pa.Check.gt(0)),
        "close": pa.Column(float, checks=pa.Check.gt(0)),
        "volume": pa.Column(float, checks=pa.Check.ge(0)),
    },
    strict=False,
    coerce=True,
)


class FetchManifest(BaseModel):
    exchange: str
    symbol: str
    timeframe: str
    limit: int
    history_start: str | None = None
    fetched_at_utc: datetime
    source: str = "ccxt"
    row_count: int = Field(ge=0)
    first_ts: datetime
    last_ts: datetime
    csv_path: str
    config_hash: str | None = None


class ReviewRow(BaseModel):
    """Subset of human-review columns used for row validation."""

    review_id: str
    symbol: str
    timeframe: str
    exchange: str
    fib_level: str
    fib_price: float
    event_bar: int
    event_time: str
    auto_candidate: str
    human_label: str = ""
    human_confidence: str = ""
    human_note: str = ""


def validate_ohlcv_df(df: pd.DataFrame, *, strict: bool = True) -> pd.DataFrame:
    """Validate OHLCV columns and price invariants; fail-fast when ``strict``."""
    if not strict:
        return df
    missing = [c for c in OHLCV_COLUMNS if c not in df.columns]
    if missing:
        raise pa.errors.SchemaError(
            schema=OHLCV_SCHEMA,
            data=df,
            message=f"Missing OHLCV columns: {missing}",
        )
    subset = df[list(OHLCV_COLUMNS)]
    OHLCV_SCHEMA.validate(subset, lazy=False)
    if (subset["high"] < subset["low"]).any():
        bad = subset.index[subset["high"] < subset["low"]]
        raise pa.errors.SchemaError(
            schema=OHLCV_SCHEMA,
            data=df,
            message=f"high < low on rows: {list(bad[:5])}",
        )
    return df


def manifest_path_for_csv(csv_path: Path) -> Path:
    return csv_path.with_name("manifest.json")

"""OHLCV DataFrame schema and small pydantic models for provenance / review rows."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pandera.pandas as pa
from pydantic import BaseModel, ConfigDict, Field, ValidationError

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


class _PointModel(BaseModel):
    """Validation gate for a swing-label point (fail-closed on malformed JSON)."""

    model_config = ConfigDict(extra="forbid")
    timestamp: str
    price: float


class _LegLabelModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
    high: _PointModel
    low: _PointModel
    id: str = ""
    role: str = ""
    note: str = ""
    same_candle_mtf_resolution: dict | None = None


class SwingLabelModel(BaseModel):
    """Schema contract for a swing-label JSON payload.

    Mirrors ``labeling.store.SwingLabel`` field-for-field; used only to *validate*
    raw JSON at the load boundary, not to replace the dataclass. ``extra="forbid"``
    so unknown keys fail closed rather than being silently dropped.
    """

    model_config = ConfigDict(extra="forbid")
    exchange: str
    symbol: str
    timeframe: str
    high: _PointModel
    low: _PointModel
    note: str = ""
    created_at: str = ""
    source: str = "human"
    same_candle_mtf_resolution: dict | None = None
    legs: list[_LegLabelModel] | None = None


def validate_label_payload(data: Any, *, source_path: object = None) -> dict:
    """Fail-closed validation of a swing-label JSON payload.

    Raises ``ValueError`` (with the offending path, when given) on malformed data;
    returns the input dict unchanged on success so callers keep their existing
    dataclass construction.
    """
    try:
        SwingLabelModel.model_validate(data)
    except ValidationError as exc:
        where = f" in {source_path}" if source_path is not None else ""
        raise ValueError(f"Invalid swing-label JSON{where}: {exc}") from exc
    return data


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

"""Ladda cachade candles till en pandas DataFrame och beräkna ATR."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from fibengine.core.config import DataConfig
from fibengine.data.fetch import (
    cache_path,
    fetch_and_cache,
    legacy_cache_path,
    trim_to_history_start,
)
from fibengine.validation.schemas import validate_ohlcv_df


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range (Wilder). Egen implementation — inga extra beroenden."""
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    true_range = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    return true_range.ewm(alpha=1 / period, adjust=False).mean()


def load_candles(
    cfg: DataConfig,
    fetch_if_missing: bool = True,
    *,
    strict: bool = True,
) -> pd.DataFrame:
    """Ladda candles från cache; hämta från börsen om de saknas."""
    path = cache_path(cfg)
    if not path.exists():
        legacy = legacy_cache_path(cfg)
        if legacy.exists():
            path = legacy
    if not path.exists():
        if not fetch_if_missing:
            raise FileNotFoundError(f"Ingen cache: {path}. Kör fetch först.")
        path = fetch_and_cache(cfg)
    df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")
    df.index = pd.to_datetime(df.index, utc=True)
    df = trim_to_history_start(df, cfg)
    return validate_ohlcv_df(df, strict=strict)


def load_candles_from_path(path: str | Path, *, strict: bool = True) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")
    df.index = pd.to_datetime(df.index, utc=True)
    return validate_ohlcv_df(df, strict=strict)

"""Hämta OHLCV-candles via CCXT och cacha lokalt som CSV."""

from __future__ import annotations

from pathlib import Path

import ccxt
import pandas as pd

from fibengine.core.config import REPO_ROOT, DataConfig, load_settings

RAW_DIR = REPO_ROOT / "data" / "raw"
OHLCV_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]


def cache_path(cfg: DataConfig) -> Path:
    symbol = cfg.symbol.replace("/", "-")
    limit = cfg.effective_limit()
    return RAW_DIR / cfg.exchange.lower() / symbol / cfg.timeframe / f"limit_{limit}.csv"


def legacy_cache_path(cfg: DataConfig) -> Path:
    symbol = cfg.symbol.replace("/", "-")
    return RAW_DIR / f"{cfg.exchange}_{symbol}_{cfg.timeframe}_{cfg.effective_limit()}.csv"


def fetch_ohlcv(cfg: DataConfig) -> pd.DataFrame:
    """Hämta candles från börsen och returnera en DataFrame indexerad på tid."""
    exchange = getattr(ccxt, cfg.exchange)({"enableRateLimit": True})
    rows = exchange.fetch_ohlcv(cfg.symbol, timeframe=cfg.timeframe, limit=cfg.effective_limit())
    df = pd.DataFrame(rows, columns=OHLCV_COLUMNS)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    return df.set_index("timestamp")


def fetch_and_cache(cfg: DataConfig) -> Path:
    df = fetch_ohlcv(cfg)
    path = cache_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path)
    return path


def main():
    settings = load_settings()
    path = fetch_and_cache(settings.data)
    df = pd.read_csv(path)
    print(f"Cachade {len(df)} candles -> {path}")
    print(df.tail())


if __name__ == "__main__":
    main()

"""Hämta OHLCV-candles via CCXT och cacha lokalt som CSV."""

from __future__ import annotations

import argparse
from collections.abc import Iterable
from pathlib import Path

import ccxt
import pandas as pd

from fibengine.core.config import REPO_ROOT, DataConfig, Settings, load_settings

RAW_DIR = REPO_ROOT / "data" / "raw"
OHLCV_COLUMNS = ["timestamp", "open", "high", "low", "close", "volume"]

LABELING_SYMBOLS = ("BTC/USD", "ETH/USD", "SOL/USD")
LABELING_TIMEFRAMES = ("1w", "1d")


def cache_path(cfg: DataConfig) -> Path:
    symbol = cfg.symbol.replace("/", "-")
    limit = cfg.effective_limit()
    return RAW_DIR / cfg.exchange.lower() / symbol / cfg.timeframe / f"limit_{limit}.csv"


def legacy_cache_path(cfg: DataConfig) -> Path:
    symbol = cfg.symbol.replace("/", "-")
    return RAW_DIR / f"{cfg.exchange}_{symbol}_{cfg.timeframe}_{cfg.effective_limit()}.csv"


def _dedupe_tail_rows(rows: list[list], want: int) -> list[list]:
    by_ts = {row[0]: row for row in rows}
    return [by_ts[ts] for ts in sorted(by_ts)][-want:]


def fetch_ohlcv(cfg: DataConfig) -> pd.DataFrame:
    """Hämta de senaste `limit` candles (paginerat från `since`).

    Bitfinex (och vissa börser) returnerar annars de *äldsta* N bars vid ett enda anrop.
    """
    exchange = getattr(ccxt, cfg.exchange)({"enableRateLimit": True})
    symbol = cfg.symbol
    timeframe = cfg.timeframe
    want = cfg.effective_limit()
    tf_ms = int(exchange.parse_timeframe(timeframe) * 1000)
    now = exchange.milliseconds()
    since_ms = max(0, now - want * tf_ms)

    by_ts: dict[int, list] = {}
    cursor = since_ms
    for _ in range(max(3, (want // 500) + 2)):
        batch = exchange.fetch_ohlcv(symbol, timeframe, since=cursor, limit=1000)
        if not batch:
            break
        for row in batch:
            by_ts[row[0]] = row
        next_cursor = batch[-1][0] + 1
        if next_cursor <= cursor:
            break
        cursor = next_cursor
        if batch[-1][0] >= now - tf_ms:
            break

    rows = [by_ts[ts] for ts in sorted(by_ts)]
    if len(rows) < want:
        fallback = exchange.fetch_ohlcv(symbol, timeframe, limit=want)
        rows = _dedupe_tail_rows(rows + (fallback or []), want)
    else:
        rows = rows[-want:]

    df = pd.DataFrame(rows, columns=OHLCV_COLUMNS)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    return df.set_index("timestamp")


def fetch_and_cache(cfg: DataConfig) -> Path:
    df = fetch_ohlcv(cfg)
    path = cache_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path)
    return path


def cache_exists(cfg: DataConfig) -> bool:
    return cache_path(cfg).exists() or legacy_cache_path(cfg).exists()


def data_config_from_settings(
    settings: Settings,
    *,
    exchange: str | None = None,
    symbol: str | None = None,
    timeframe: str | None = None,
) -> DataConfig:
    base = settings.data
    return base.model_copy(
        update={
            key: value
            for key, value in {
                "exchange": exchange,
                "symbol": symbol,
                "timeframe": timeframe,
            }.items()
            if value is not None
        }
    )


def iter_labeling_data_configs(
    settings: Settings,
    exchange: str | None = None,
) -> Iterable[DataConfig]:
    ex = exchange or settings.data.exchange
    for symbol in LABELING_SYMBOLS:
        for timeframe in LABELING_TIMEFRAMES:
            yield data_config_from_settings(
                settings,
                exchange=ex,
                symbol=symbol,
                timeframe=timeframe,
            )


def _split_csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def iter_fetch_targets(settings: Settings, args: argparse.Namespace) -> Iterable[DataConfig]:
    if args.labeling_set:
        yield from iter_labeling_data_configs(settings, exchange=args.exchange)
        return

    symbols = _split_csv(args.symbols) if args.symbols else [settings.data.symbol]
    timeframes = _split_csv(args.timeframes) if args.timeframes else [settings.data.timeframe]

    if len(symbols) == 1 and len(timeframes) == 1 and not args.exchange:
        yield data_config_from_settings(
            settings,
            symbol=symbols[0] if args.symbols else None,
            timeframe=timeframes[0] if args.timeframes else None,
        )
        return

    ex = args.exchange or settings.data.exchange
    for symbol in symbols:
        for timeframe in timeframes:
            yield data_config_from_settings(
                settings,
                exchange=ex,
                symbol=symbol,
                timeframe=timeframe,
            )


def run_fetch(cfg: DataConfig, *, refresh: bool = False) -> Path:
    if not refresh and cache_exists(cfg):
        return cache_path(cfg) if cache_path(cfg).exists() else legacy_cache_path(cfg)
    return fetch_and_cache(cfg)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch OHLCV via CCXT and cache under data/raw/.")
    parser.add_argument(
        "--config",
        type=str,
        default="",
        help="Settings file (default: config/settings.yaml).",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Hämta från börsen även om cache finns (skriver om CSV).",
    )
    parser.add_argument("--exchange", help="Override exchange (default: from settings).")
    parser.add_argument(
        "--symbols",
        help="Comma-separated symbols, e.g. BTC/USD,ETH/USD (default: settings symbol).",
    )
    parser.add_argument(
        "--timeframes",
        help="Comma-separated timeframes, e.g. 1w,1d (default: settings timeframe).",
    )
    parser.add_argument(
        "--labeling-set",
        action="store_true",
        help=f"Fetch {LABELING_SYMBOLS} × {LABELING_TIMEFRAMES} on exchange (Bitfinex default).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    settings = load_settings(args.config or None)
    targets = list(iter_fetch_targets(settings, args))
    if not targets:
        print("Inga fetch-mål.")
        return

    for cfg in targets:
        had_cache = cache_exists(cfg)
        path = run_fetch(cfg, refresh=args.refresh)
        df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")
        df.index = pd.to_datetime(df.index, utc=True)
        action = "Uppdaterade" if args.refresh or not had_cache else "Cache (oförändrad)"
        print(
            f"{action} {cfg.exchange} {cfg.symbol} {cfg.timeframe}: "
            f"{len(df)} bars, {df.index[0]} .. {df.index[-1]} -> {path}"
        )


if __name__ == "__main__":
    main()

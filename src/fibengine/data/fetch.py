"""Hämta OHLCV-candles via CCXT och cacha lokalt som CSV."""

from __future__ import annotations

import argparse
import math
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path

import ccxt
import pandas as pd

from fibengine.core.config import REPO_ROOT, DataConfig, Settings, load_settings
from fibengine.validation.schemas import FetchManifest, manifest_path_for_csv

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


def history_start_ts(cfg: DataConfig) -> pd.Timestamp | None:
    if not cfg.history_start:
        return None
    return pd.to_datetime(cfg.history_start, utc=True)


def bars_needed_since_history_start(cfg: DataConfig, *, now_ms: int, tf_ms: int) -> int | None:
    """Bars from ``history_start`` through ``now`` (inclusive), or None if unset."""
    start = history_start_ts(cfg)
    if start is None:
        return None
    start_ms = int(start.timestamp() * 1000)
    if now_ms <= start_ms:
        return 1
    return math.ceil((now_ms - start_ms) / tf_ms) + 1


def trim_to_history_start(df: pd.DataFrame, cfg: DataConfig) -> pd.DataFrame:
    start = history_start_ts(cfg)
    if start is None or df.empty:
        return df
    return df[df.index >= start]


def fetch_ohlcv(cfg: DataConfig) -> pd.DataFrame:
    """Hämta candles (paginerat från ``since``).

    Med ``history_start`` hämtas från det datumet till idag; annars senaste
    ``effective_limit()`` bars. Bitfinex returnerar annars ofta de äldsta N bars
    vid ett enda anrop utan pagination.
    """
    exchange = getattr(ccxt, cfg.exchange)({"enableRateLimit": True})
    symbol = cfg.symbol
    timeframe = cfg.timeframe
    want = cfg.effective_limit()
    tf_ms = int(exchange.parse_timeframe(timeframe) * 1000)
    now = exchange.milliseconds()
    bars_from_start = bars_needed_since_history_start(cfg, now_ms=now, tf_ms=tf_ms)
    if bars_from_start is not None:
        want = max(want, bars_from_start)
        since_ms = int(history_start_ts(cfg).timestamp() * 1000)  # type: ignore[union-attr]
    else:
        since_ms = max(0, now - want * tf_ms)

    by_ts: dict[int, list] = {}
    cursor = since_ms
    max_iters = max(5, (want // 800) + 4)
    for _ in range(max_iters):
        batch = exchange.fetch_ohlcv(symbol, timeframe, since=cursor, limit=1000)
        if not batch:
            break
        for row in batch:
            by_ts[row[0]] = row
        next_cursor = batch[-1][0] + 1
        if next_cursor <= cursor:
            break
        cursor = next_cursor
        if len(by_ts) >= want or batch[-1][0] >= now - tf_ms:
            break

    rows = [by_ts[ts] for ts in sorted(by_ts)]
    if len(rows) < want:
        fallback = exchange.fetch_ohlcv(symbol, timeframe, limit=want)
        rows = _dedupe_tail_rows(rows + (fallback or []), want)
    else:
        rows = rows[-want:]

    df = pd.DataFrame(rows, columns=OHLCV_COLUMNS)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    return trim_to_history_start(df.set_index("timestamp"), cfg)


def _write_fetch_manifest(
    cfg: DataConfig,
    df: pd.DataFrame,
    path: Path,
    *,
    config_hash: str | None = None,
) -> None:
    now = datetime.now(UTC)
    first = pd.Timestamp(df.index[0]).to_pydatetime() if not df.empty else now
    last = pd.Timestamp(df.index[-1]).to_pydatetime() if not df.empty else now
    manifest = FetchManifest(
        exchange=cfg.exchange,
        symbol=cfg.symbol,
        timeframe=cfg.timeframe,
        limit=cfg.effective_limit(),
        history_start=cfg.history_start,
        fetched_at_utc=now,
        row_count=len(df),
        first_ts=first,
        last_ts=last,
        csv_path=str(path),
        config_hash=config_hash,
    )
    manifest_path_for_csv(path).write_text(
        manifest.model_dump_json(indent=2),
        encoding="utf-8",
    )


def fetch_and_cache(cfg: DataConfig, *, config_hash: str | None = None) -> Path:
    df = fetch_ohlcv(cfg)
    path = cache_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path)
    _write_fetch_manifest(cfg, df, path, config_hash=config_hash)
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

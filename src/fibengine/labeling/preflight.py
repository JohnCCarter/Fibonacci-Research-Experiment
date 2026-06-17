"""Preflight checks before ``fibengine.labeling.tool`` (cache-only, no surprise fetch).

Run:
    uv run python -m fibengine.labeling.preflight \\
        --symbol BTC/USD --timeframes 1M,1w,1d,4h,1h \\
        --config config/settings.expansion.yaml
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import ccxt
import pandas as pd

from fibengine.core.config import DataConfig, Settings, load_settings
from fibengine.data.fetch import cache_path, legacy_cache_path
from fibengine.labeling.htf_fib_overlay import (
    TOP_DOWN_LADDER,
    htf_timeframes_for_chart,
    list_saved_annotations,
    load_htf_overlays,
    normalize_timeframe,
)
from fibengine.labeling.tool import _csv_values, _default_timeframes

_STATUS_OK = "OK"
_STATUS_WARN = "WARN"
_STATUS_FAIL = "FAIL"


@dataclass
class CacheCheck:
    symbol: str
    timeframe: str
    status: str
    message: str
    path: Path | None = None
    bars: int = 0
    first_date: str = ""
    last_date: str = ""


def _parse_timeframes_arg(raw: str | None, primary: str) -> list[str]:
    if raw:
        return _csv_values(raw, [])
    return _default_timeframes(primary)


def _ccxt_parses_timeframe(exchange_id: str, timeframe: str) -> tuple[bool, str]:
    tf = normalize_timeframe(timeframe)
    try:
        exchange = getattr(ccxt, exchange_id)({"enableRateLimit": True})
        exchange.parse_timeframe(tf)
        return True, ""
    except Exception as exc:  # noqa: BLE001 — report any CCXT/parse failure
        return False, str(exc)


def discover_cache_path(cfg: DataConfig) -> tuple[Path | None, str]:
    """Find a local CSV for ``cfg``; report exact match, alternate limit, or missing."""
    expected = cache_path(cfg)
    if expected.exists():
        return expected, _STATUS_OK
    legacy = legacy_cache_path(cfg)
    if legacy.exists():
        return legacy, _STATUS_WARN
    parent = expected.parent
    if not parent.is_dir():
        return None, _STATUS_FAIL
    candidates = sorted(parent.glob("limit_*.csv"))
    if not candidates:
        return None, _STATUS_FAIL
    if len(candidates) == 1:
        alt = candidates[0]
        if alt.name == expected.name:
            return alt, _STATUS_OK
        return alt, _STATUS_WARN
    for alt in candidates:
        if alt.name == expected.name:
            return alt, _STATUS_OK
    return candidates[-1], _STATUS_WARN


def _read_cache_stats(path: Path) -> tuple[int, str, str]:
    df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")
    df.index = pd.to_datetime(df.index, utc=True)
    if df.empty:
        return 0, "", ""
    return len(df), str(df.index[0].date()), str(df.index[-1].date())


def check_candle_cache(
    settings: Settings,
    *,
    symbol: str,
    timeframe: str,
) -> CacheCheck:
    tf = normalize_timeframe(timeframe)
    cfg = settings.data.model_copy(update={"symbol": symbol, "timeframe": tf})
    expected = cache_path(cfg)
    path, match = discover_cache_path(cfg)
    ok_parse, parse_err = _ccxt_parses_timeframe(cfg.exchange, tf)
    if not ok_parse:
        return CacheCheck(
            symbol=symbol,
            timeframe=tf,
            status=_STATUS_FAIL,
            message=f"CCXT cannot parse timeframe {tf!r}: {parse_err}",
        )
    if path is None:
        return CacheCheck(
            symbol=symbol,
            timeframe=tf,
            status=_STATUS_FAIL,
            message=f"no cache at {expected} — run fetch (see below)",
        )
    bars, first_d, last_d = _read_cache_stats(path)
    if match == _STATUS_WARN:
        msg = (
            f"using {path.name} but config expects {expected.name} "
            f"({cfg.effective_limit()} bars) — align --config or refetch"
        )
        status = _STATUS_WARN
    else:
        msg = f"{bars} bars, {first_d} .. {last_d}"
        status = _STATUS_OK
    return CacheCheck(
        symbol=symbol,
        timeframe=tf,
        status=status,
        message=msg,
        path=path,
        bars=bars,
        first_date=first_d,
        last_date=last_d,
    )


def fetch_command(symbol: str, timeframe: str, config: str) -> str:
    cfg_flag = f' --config "{config}"' if config else ""
    return (
        f"uv run python -m fibengine.data.fetch --symbols {symbol} "
        f"--timeframes {timeframe} --refresh{cfg_flag}"
    )


def tool_command(
    symbol: str,
    timeframes: list[str],
    config: str,
    *,
    start_tf: str | None = None,
) -> str:
    tf_csv = ",".join(timeframes)
    start = normalize_timeframe(start_tf or timeframes[0])
    cfg_flag = f' --config "{config}"' if config else ""
    return (
        f"uv run python -m fibengine.labeling.tool --symbol {symbol} "
        f"--timeframe {start} --timeframes {tf_csv} --symbols {symbol}{cfg_flag}"
    )


def run_preflight(
    *,
    settings: Settings,
    symbols: list[str],
    timeframes: list[str],
    config_path: str = "",
) -> int:
    """Print report; return 0 if ready, 1 if blocking issues."""
    print("=== labeling.tool preflight (cache-only) ===")
    print(f"config: {config_path or 'config/settings.yaml (default)'}")
    print(f"symbols: {', '.join(symbols)}")
    print(f"timeframe cycle: {', '.join(timeframes)}")
    print(f"HTF ladder: {' -> '.join(TOP_DOWN_LADDER)}")
    print()

    failures = 0
    warnings = 0

    print("--- candle cache ---")
    for symbol in symbols:
        for tf in timeframes:
            chk = check_candle_cache(settings, symbol=symbol, timeframe=tf)
            print(f"[{chk.status}] {symbol} {chk.timeframe}: {chk.message}")
            if chk.path:
                print(f"       path: {chk.path}")
            if chk.status == _STATUS_FAIL:
                failures += 1
                print(f"       fix: {fetch_command(symbol, chk.timeframe, config_path)}")
            elif chk.status == _STATUS_WARN:
                warnings += 1
    print()

    print("--- human fib (saved) ---")
    for symbol in symbols:
        for tf in timeframes:
            n = len(list_saved_annotations(settings.data.exchange, symbol, tf))
            print(f"  {symbol} {tf}: {n} annotation(s)")
    print()

    if len(symbols) == 1:
        symbol = symbols[0]
        chart_tf = max(
            (normalize_timeframe(tf) for tf in timeframes),
            key=lambda t: TOP_DOWN_LADDER.index(t) if t in TOP_DOWN_LADDER else -1,
        )
        if chart_tf in TOP_DOWN_LADDER:
            overlays = load_htf_overlays(settings.data.exchange, symbol, chart_tf)
            htf_counts: dict[str, int] = {}
            for htf, _ in overlays:
                htf_counts[htf] = htf_counts.get(htf, 0) + 1
            print("--- HTF overlays (read-only on lower chart) ---")
            for htf in htf_timeframes_for_chart(chart_tf):
                print(f"  on {chart_tf} chart: {htf_counts.get(htf, 0)} fib(s) from {htf}")
            print()

    print("--- next ---")
    if failures:
        print("NOT READY: fix FAIL rows above (prefetch locally; tool will not auto-fetch).")
    else:
        print("READY: caches OK for labeling cycle.")
        if warnings:
            print(f"({warnings} WARN — review config/cache alignment)")
        print(tool_command(symbols[0], timeframes, config_path))
    print()
    return 1 if failures else 0


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Preflight for labeling.tool — verify caches before opening the GUI."
    )
    p.add_argument("--config", type=str, default="", help="Settings file (same as labeling.tool).")
    p.add_argument("--exchange", help="Override exchange (default: from settings).")
    p.add_argument("--symbol", default="BTC/USD", help="Symbol to check (default: BTC/USD).")
    p.add_argument(
        "--symbols",
        help="Comma-separated symbols (default: --symbol only).",
    )
    p.add_argument(
        "--timeframes",
        help="Comma-separated timeframe cycle (default: tool default list).",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    settings = load_settings(args.config or None)
    if args.exchange:
        settings.data = settings.data.model_copy(update={"exchange": args.exchange})
    symbols = _csv_values(args.symbols, [args.symbol])
    primary_tf = normalize_timeframe(
        _parse_timeframes_arg(args.timeframes, settings.data.timeframe)[0]
    )
    timeframes = _parse_timeframes_arg(args.timeframes, primary_tf)
    code = run_preflight(
        settings=settings,
        symbols=symbols,
        timeframes=timeframes,
        config_path=args.config,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()

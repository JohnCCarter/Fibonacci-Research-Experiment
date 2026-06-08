import argparse
from datetime import UTC

import pandas as pd

from fibengine.core.config import DataConfig, Settings
from fibengine.data.fetch import (
    _dedupe_tail_rows,
    _write_fetch_manifest,
    bars_needed_since_history_start,
    cache_path,
    iter_fetch_targets,
    iter_labeling_data_configs,
    trim_to_history_start,
)
from fibengine.validation.schemas import FetchManifest, manifest_path_for_csv


def test_dedupe_tail_rows_keeps_most_recent():
    rows = [[i, 0, 0, 0, 0, 0] for i in range(5)]
    out = _dedupe_tail_rows(rows, want=3)
    assert [r[0] for r in out] == [2, 3, 4]


def test_cache_path_includes_limit():
    base = DataConfig(exchange="bitfinex", symbol="BTC/USD", timeframe="1h", limit=100)
    longer = base.model_copy(update={"limit": 500})
    assert cache_path(base) != cache_path(longer)
    assert cache_path(base).name == "limit_100.csv"
    assert "bitfinex" in cache_path(base).as_posix()
    assert "BTC-USD/1h" in cache_path(base).as_posix()


def test_timeframe_limit_override_affects_effective_limit_and_cache_path():
    cfg = DataConfig(
        exchange="bitfinex",
        symbol="BTC/USD",
        timeframe="1d",
        limit=500,
        timeframe_limits={"1d": 1000},
    )
    assert cfg.effective_limit() == 1000
    assert cfg.model_copy(update={"timeframe": "1h"}).effective_limit() == 500
    assert cache_path(cfg).name == "limit_1000.csv"


def test_labeling_set_expands_symbols_and_timeframes():
    settings = Settings()
    configs = list(iter_labeling_data_configs(settings))
    assert len(configs) == 6
    assert {c.symbol for c in configs} == {"BTC/USD", "ETH/USD", "SOL/USD"}
    assert {c.timeframe for c in configs} == {"1w", "1d"}


def test_iter_fetch_targets_labeling_set_flag():
    settings = Settings()
    args = argparse.Namespace(
        labeling_set=True,
        symbols="",
        timeframes="",
        exchange=None,
    )
    configs = list(iter_fetch_targets(settings, args))
    assert len(configs) == 6


def test_history_start_trims_loaded_candles():
    idx = pd.date_range("2022-01-01", periods=5, freq="D", tz="UTC")
    df = pd.DataFrame(
        {"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1.0},
        index=idx,
    )
    cfg = DataConfig(history_start="2022-10-31")
    trimmed = trim_to_history_start(df, cfg)
    assert trimmed.empty

    idx2 = pd.date_range("2022-10-31", periods=3, freq="D", tz="UTC")
    df2 = pd.DataFrame(
        {"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "volume": 1.0},
        index=idx2,
    )
    trimmed2 = trim_to_history_start(df2, cfg)
    assert len(trimmed2) == 3


def test_bars_needed_since_history_start_for_1d():
    cfg = DataConfig(timeframe="1d", history_start="2022-10-31")
    # 2026-06-05 00:00 UTC
    now_ms = int(pd.Timestamp("2026-06-05", tz="UTC").timestamp() * 1000)
    tf_ms = 86_400_000
    bars = bars_needed_since_history_start(cfg, now_ms=now_ms, tf_ms=tf_ms)
    assert bars is not None
    assert 1300 <= bars <= 1320


def test_iter_fetch_targets_symbol_timeframe_grid():
    settings = Settings()
    args = argparse.Namespace(
        labeling_set=False,
        symbols="BTC/USD,ETH/USD",
        timeframes="1w,1d",
        exchange="bitfinex",
    )
    configs = list(iter_fetch_targets(settings, args))
    assert len(configs) == 4
    assert all(c.exchange == "bitfinex" for c in configs)


def test_write_fetch_manifest_creates_json_next_to_csv(tmp_path):
    cfg = DataConfig(exchange="bitfinex", symbol="BTC/USD", timeframe="1h", limit=3)
    idx = pd.date_range("2024-01-01", periods=3, freq="h", tz="UTC")
    df = pd.DataFrame(
        {
            "open": [1.0, 2.0, 3.0],
            "high": [1.1, 2.1, 3.1],
            "low": [0.9, 1.9, 2.9],
            "close": [1.0, 2.0, 3.0],
            "volume": [10.0, 20.0, 30.0],
        },
        index=idx,
    )
    csv_path = tmp_path / "limit_3.csv"
    df.to_csv(csv_path)
    _write_fetch_manifest(cfg, df, csv_path, config_hash="abc123")
    manifest_path = manifest_path_for_csv(csv_path)
    assert manifest_path.exists()
    manifest = FetchManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    assert manifest.exchange == "bitfinex"
    assert manifest.symbol == "BTC/USD"
    assert manifest.row_count == 3
    assert manifest.source == "ccxt"
    assert manifest.config_hash == "abc123"
    assert manifest.first_ts.tzinfo == UTC

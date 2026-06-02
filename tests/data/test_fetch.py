import argparse

from fibengine.core.config import DataConfig, Settings
from fibengine.data.fetch import (
    _dedupe_tail_rows,
    cache_path,
    iter_fetch_targets,
    iter_labeling_data_configs,
)


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

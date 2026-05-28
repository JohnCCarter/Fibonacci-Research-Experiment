from fibengine.core.config import DataConfig
from fibengine.data.fetch import cache_path


def test_cache_path_includes_limit():
    base = DataConfig(exchange="binance", symbol="BTC/USDT", timeframe="1h", limit=100)
    longer = base.model_copy(update={"limit": 500})
    assert cache_path(base) != cache_path(longer)
    assert cache_path(base).name == "limit_100.csv"
    assert "binance" in cache_path(base).as_posix()
    assert "BTC-USDT/1h" in cache_path(base).as_posix()


def test_timeframe_limit_override_affects_effective_limit_and_cache_path():
    cfg = DataConfig(
        exchange="binance",
        symbol="BTC/USDT",
        timeframe="1d",
        limit=500,
        timeframe_limits={"1d": 1000},
    )
    # Override gäller bara den angivna timeframen.
    assert cfg.effective_limit() == 1000
    assert cfg.model_copy(update={"timeframe": "1h"}).effective_limit() == 500
    # Cache-filnamnet ska spegla den faktiskt laddade mängden.
    assert cache_path(cfg).name == "limit_1000.csv"

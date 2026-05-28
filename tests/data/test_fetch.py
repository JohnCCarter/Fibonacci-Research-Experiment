from fibengine.core.config import DataConfig
from fibengine.data.fetch import cache_path


def test_cache_path_includes_limit():
    base = DataConfig(exchange="binance", symbol="BTC/USDT", timeframe="1h", limit=100)
    longer = base.model_copy(update={"limit": 500})
    assert cache_path(base) != cache_path(longer)
    assert cache_path(base).name == "limit_100.csv"
    assert "binance" in cache_path(base).as_posix()
    assert "BTC-USDT/1h" in cache_path(base).as_posix()

from fibengine.core.config import DataConfig, Settings
from fibengine.labeling import preflight


def test_discover_cache_path_exact(tmp_path, monkeypatch):
    cfg = DataConfig(exchange="bitfinex", symbol="BTC/USD", timeframe="1w", limit=500)
    path = tmp_path / "limit_500.csv"
    path.write_text("timestamp,open,high,low,close,volume\n", encoding="utf-8")
    monkeypatch.setattr(preflight, "cache_path", lambda c: path)
    monkeypatch.setattr(preflight, "legacy_cache_path", lambda c: path.with_suffix(".legacy"))

    found, status = preflight.discover_cache_path(cfg)
    assert found == path
    assert status == preflight._STATUS_OK


def test_discover_cache_path_alternate_limit_warns(tmp_path, monkeypatch):
    cfg = DataConfig(
        exchange="bitfinex",
        symbol="BTC/USD",
        timeframe="1w",
        limit=220,
        timeframe_limits={"1w": 220},
    )
    expected = tmp_path / "limit_220.csv"
    alt = tmp_path / "limit_1000.csv"
    tmp_path.mkdir(parents=True, exist_ok=True)
    alt.write_text("timestamp,open,high,low,close,volume\n", encoding="utf-8")
    monkeypatch.setattr(preflight, "cache_path", lambda c: expected)
    monkeypatch.setattr(preflight, "legacy_cache_path", lambda c: expected.with_suffix(".legacy"))

    found, status = preflight.discover_cache_path(cfg)
    assert found == alt
    assert status == preflight._STATUS_WARN


def test_check_candle_cache_fail_when_missing(monkeypatch):
    monkeypatch.setattr(
        preflight,
        "discover_cache_path",
        lambda _cfg: (None, preflight._STATUS_FAIL),
    )
    chk = preflight.check_candle_cache(Settings(), symbol="BTC/USD", timeframe="4h")
    assert chk.status == preflight._STATUS_FAIL
    assert "fetch" in chk.message.lower() or "no cache" in chk.message.lower()


def test_run_preflight_ready_with_cache(tmp_path, monkeypatch):
    def fake_check(_settings, *, symbol, timeframe):
        return preflight.CacheCheck(
            symbol=symbol,
            timeframe=timeframe,
            status=preflight._STATUS_OK,
            message="10 bars",
            path=tmp_path / f"{timeframe}.csv",
            bars=10,
        )

    monkeypatch.setattr(preflight, "check_candle_cache", fake_check)
    monkeypatch.setattr(preflight, "list_saved_annotations", lambda *a, **k: [])
    monkeypatch.setattr(preflight, "load_htf_overlays", lambda *a, **k: [])

    code = preflight.run_preflight(
        settings=Settings(),
        symbols=["BTC/USD"],
        timeframes=["1M", "1w"],
        config_path="config/settings.expansion.yaml",
    )
    assert code == 0


def test_run_preflight_exit_one_on_missing(monkeypatch):
    monkeypatch.setattr(
        preflight,
        "check_candle_cache",
        lambda *a, **k: preflight.CacheCheck(
            symbol="BTC/USD",
            timeframe="4h",
            status=preflight._STATUS_FAIL,
            message="no cache",
        ),
    )
    monkeypatch.setattr(preflight, "list_saved_annotations", lambda *a, **k: [])
    code = preflight.run_preflight(
        settings=Settings(),
        symbols=["BTC/USD"],
        timeframes=["4h"],
    )
    assert code == 1

from pathlib import Path

from fibengine.backtest import matrix
from fibengine.backtest.matrix import (
    MatrixCase,
    _case_settings,
    _cases_from_args,
    default_matrix,
    run_matrix,
)
from fibengine.core.config import REPO_ROOT, Settings, load_settings


def test_default_matrix_covers_symbols_and_timeframes():
    cases = default_matrix()
    assert MatrixCase("BTC/USD", "15m") in cases
    assert MatrixCase("ETH/USD", "1h") in cases
    assert MatrixCase("SOL/USD", "4h") in cases
    assert len(cases) == 9


def test_case_settings_does_not_mutate_base_settings():
    base = Settings()
    updated = _case_settings(base, MatrixCase("ETH/USD", "4h"))
    assert base.data.symbol == "BTC/USD"
    assert base.data.timeframe == "1h"
    assert updated.data.symbol == "ETH/USD"
    assert updated.data.timeframe == "4h"


def test_cases_from_args_parses_symbols_and_timeframes():
    args = type("Args", (), {"symbols": "BTC/USD,ETH/USD", "timeframes": "1h"})()
    cases = _cases_from_args(args)
    assert cases == [
        MatrixCase("BTC/USD", "1h"),
        MatrixCase("ETH/USD", "1h"),
    ]


def test_bitfinex_settings_profile_loads():
    settings = load_settings(REPO_ROOT / "config" / "settings.bitfinex.yaml")
    assert settings.data.exchange == "bitfinex"
    assert settings.data.symbol == "BTC/USD"


def test_matrix_records_case_errors(monkeypatch, tmp_path: Path):
    out = tmp_path / "matrix.jsonl"
    monkeypatch.setattr(matrix, "MATRIX_RESULTS", out)

    def boom(_cfg):
        raise RuntimeError("fetch failed")

    monkeypatch.setattr(matrix, "load_candles", boom)

    rows = run_matrix(Settings(), cases=[MatrixCase("BTC/USD", "1h")])

    assert rows[0]["status"] == "error"
    assert rows[0]["error_type"] == "RuntimeError"
    assert "fetch failed" in out.read_text()

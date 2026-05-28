from pathlib import Path

from fibengine.backtest import matrix
from fibengine.backtest.matrix import MatrixCase, _case_settings, default_matrix, run_matrix
from fibengine.config import Settings


def test_default_matrix_covers_symbols_and_timeframes():
    cases = default_matrix()
    assert MatrixCase("BTC/USDT", "15m") in cases
    assert MatrixCase("ETH/USDT", "1h") in cases
    assert MatrixCase("SOL/USDT", "4h") in cases
    assert len(cases) == 9


def test_case_settings_does_not_mutate_base_settings():
    base = Settings()
    updated = _case_settings(base, MatrixCase("ETH/USDT", "4h"))
    assert base.data.symbol == "BTC/USDT"
    assert base.data.timeframe == "1h"
    assert updated.data.symbol == "ETH/USDT"
    assert updated.data.timeframe == "4h"


def test_matrix_records_case_errors(monkeypatch, tmp_path: Path):
    out = tmp_path / "matrix.jsonl"
    monkeypatch.setattr(matrix, "MATRIX_RESULTS", out)

    def boom(_cfg):
        raise RuntimeError("fetch failed")

    monkeypatch.setattr(matrix, "load_candles", boom)

    rows = run_matrix(Settings(), cases=[MatrixCase("BTC/USDT", "1h")])

    assert rows[0]["status"] == "error"
    assert rows[0]["error_type"] == "RuntimeError"
    assert "fetch failed" in out.read_text()

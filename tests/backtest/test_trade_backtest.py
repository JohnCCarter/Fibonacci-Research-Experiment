from fibengine.backtest.matrix import MatrixCase
from fibengine.backtest.trade import _simulate_trade, run_trade_matrix, summarize_trades
from fibengine.core.config import Settings


def test_simulate_long_trade_hits_target_after_fill(synthetic_df):
    trade = _simulate_trade(
        synthetic_df,
        t=40,
        direction="up",
        entry=112.0,
        stop=104.0,
        target=120.0,
    )
    assert trade.filled is True
    assert trade.outcome == "target"
    assert trade.r_multiple == 1.0


def test_simulate_trade_uses_actual_reward_risk(synthetic_df):
    trade = _simulate_trade(
        synthetic_df,
        t=40,
        direction="up",
        entry=112.0,
        stop=108.0,
        target=120.0,
    )
    assert trade.outcome == "target"
    assert trade.r_multiple == 2.0


def test_summarize_trades_reports_fill_and_win_rates(synthetic_df):
    win = _simulate_trade(synthetic_df, 40, "up", 112.0, 104.0, 120.0)
    unfilled = _simulate_trade(synthetic_df, 40, "up", 10.0, 5.0, 20.0)

    summary = summarize_trades([win, unfilled])

    assert summary["trades"] == 2
    assert summary["filled"] == 1
    assert summary["fill_rate"] == 0.5
    assert summary["win_rate"] == 1.0


def test_trade_matrix_records_case_errors(monkeypatch, tmp_path):
    from fibengine.backtest import trade

    out = tmp_path / "trade_matrix.jsonl"
    monkeypatch.setattr(trade, "TRADE_MATRIX_RESULTS", out)
    monkeypatch.setattr(
        trade,
        "load_candles",
        lambda _cfg: (_ for _ in ()).throw(RuntimeError("no data")),
    )

    rows = run_trade_matrix(Settings(), cases=[MatrixCase("BTC/USDT", "1h")])

    assert rows[0]["status"] == "error"
    assert rows[0]["error_type"] == "RuntimeError"
    assert "no data" in out.read_text()

from fibengine.backtest.trade import _simulate_trade, summarize_trades


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


def test_summarize_trades_reports_fill_and_win_rates(synthetic_df):
    win = _simulate_trade(synthetic_df, 40, "up", 112.0, 104.0, 120.0)
    unfilled = _simulate_trade(synthetic_df, 40, "up", 10.0, 5.0, 20.0)

    summary = summarize_trades([win, unfilled])

    assert summary["trades"] == 2
    assert summary["filled"] == 1
    assert summary["fill_rate"] == 0.5
    assert summary["win_rate"] == 1.0

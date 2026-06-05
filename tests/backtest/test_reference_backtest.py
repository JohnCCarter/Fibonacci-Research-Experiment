from fibengine.backtest.reference import (
    ReferenceTradePlan,
    build_reference_trade_plans,
    run_reference_backtest,
)
from fibengine.backtest.vectorbt_future import build_vectorbt_signal_frame
from fibengine.core.config import Settings
from fibengine.core.models import Pivot, Swing


def _confirmed_down_swing(synthetic_df) -> Swing:
    return Swing(
        start=Pivot(20, synthetic_df.index[20], float(synthetic_df.iloc[20]["high"]), "high", 1.0),
        end=Pivot(40, synthetic_df.index[40], float(synthetic_df.iloc[40]["low"]), "low", 1.0),
        status="confirmed",
    )


def test_build_reference_trade_plans_maps_confirmed_swings(synthetic_df):
    settings = Settings()
    records = [{"t": 40, "swing": _confirmed_down_swing(synthetic_df)}]

    plans = build_reference_trade_plans(synthetic_df, settings, records)

    assert len(plans) == 1
    assert plans[0].direction == "down"
    assert plans[0].entry_bar > records[0]["t"]


def test_run_reference_backtest_returns_summary(synthetic_df):
    plan = ReferenceTradePlan(
        signal_bar=40,
        entry_bar=45,
        direction="down",
        entry=float(synthetic_df.iloc[45]["close"]),
        stop=float(synthetic_df.iloc[50]["close"]),
        target=float(synthetic_df.iloc[41]["close"]),
    )

    summary = run_reference_backtest(synthetic_df, [plan])

    assert summary["trades"] >= 0
    assert "equity_final" in summary


def test_build_vectorbt_signal_frame_marks_short_entries(synthetic_df):
    plan = ReferenceTradePlan(
        signal_bar=40,
        entry_bar=45,
        direction="down",
        entry=115.0,
        stop=120.0,
        target=108.0,
    )

    frame = build_vectorbt_signal_frame(synthetic_df, [plan]).to_frame()

    assert bool(frame.iloc[45]["short_entries"]) is True
    assert frame.iloc[45]["entries"] is False
    assert frame.iloc[45]["sl_stop"] > 0
    assert frame.iloc[45]["tp_stop"] > 0

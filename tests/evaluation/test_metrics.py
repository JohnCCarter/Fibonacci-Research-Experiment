import pandas as pd

from fibengine.core.config import EvaluationConfig
from fibengine.core.fib import fib_from_prices
from fibengine.core.models import Pivot, Swing
from fibengine.evaluation.metrics import evaluate
from fibengine.labeling.store import Point, SwingLabel


def _swing(df) -> Swing:
    low = Pivot(40, df.index[40], 105.0, "low", 2.0)
    high = Pivot(60, df.index[60], 130.0, "high", 2.0)
    return Swing(start=low, end=high)


def test_perfect_match_is_overall_hit(synthetic_df):
    swing = _swing(synthetic_df)
    label = SwingLabel(
        exchange="binance",
        symbol="BTC/USDT",
        timeframe="1h",
        high=Point(synthetic_df.index[60].isoformat(), 130.0),
        low=Point(synthetic_df.index[40].isoformat(), 105.0),
    )
    m = evaluate(synthetic_df, swing, label, atr_value=2.0, cfg=EvaluationConfig())
    assert m["agreement"] == 1.0
    assert m["mean_fib_err_frac"] == 0.0


def test_price_miss_lowers_agreement(synthetic_df):
    swing = _swing(synthetic_df)
    perfect = SwingLabel(
        exchange="binance",
        symbol="BTC/USDT",
        timeframe="1h",
        high=Point(synthetic_df.index[60].isoformat(), 130.0),
        low=Point(synthetic_df.index[40].isoformat(), 105.0),
    )
    missed = SwingLabel(
        exchange="binance",
        symbol="BTC/USDT",
        timeframe="1h",
        high=Point(synthetic_df.index[60].isoformat(), 150.0),  # långt fel
        low=Point(synthetic_df.index[40].isoformat(), 105.0),
    )
    m_perfect = evaluate(synthetic_df, swing, perfect, atr_value=2.0, cfg=EvaluationConfig())
    m_missed = evaluate(synthetic_df, swing, missed, atr_value=2.0, cfg=EvaluationConfig())
    assert m_missed["agreement"] < m_perfect["agreement"]
    assert 0.0 <= m_missed["agreement"] <= 1.0


def test_zero_range_label_keeps_metrics_finite(synthetic_df):
    swing = _swing(synthetic_df)
    label = SwingLabel(
        exchange="binance",
        symbol="BTC/USDT",
        timeframe="1h",
        high=Point(synthetic_df.index[60].isoformat(), 130.0),
        low=Point(synthetic_df.index[40].isoformat(), 130.0),
    )
    m = evaluate(synthetic_df, swing, label, atr_value=2.0, cfg=EvaluationConfig())
    assert m["mean_fib_err_frac"] == 0.0
    assert 0.0 <= m["agreement"] <= 1.0


def test_in_window_label_not_flagged(synthetic_df):
    swing = _swing(synthetic_df)
    label = SwingLabel(
        exchange="binance",
        symbol="BTC/USDT",
        timeframe="1h",
        high=Point(synthetic_df.index[60].isoformat(), 130.0),
        low=Point(synthetic_df.index[40].isoformat(), 105.0),
    )
    m = evaluate(synthetic_df, swing, label, atr_value=2.0, cfg=EvaluationConfig())
    assert m["out_of_window"] is False


def test_out_of_window_label_is_flagged(synthetic_df):
    # Label-tidsstämplar långt efter sista baren ska flaggas, inte tyst snäppas.
    swing = _swing(synthetic_df)
    future = (synthetic_df.index[-1] + pd.Timedelta(days=365)).isoformat()
    label = SwingLabel(
        exchange="binance",
        symbol="BTC/USDT",
        timeframe="1h",
        high=Point(future, 130.0),
        low=Point(future, 105.0),
    )
    m = evaluate(synthetic_df, swing, label, atr_value=2.0, cfg=EvaluationConfig())
    assert m["out_of_window"] is True


def test_fib_levels_monotonic_for_up_leg():
    levels = fib_from_prices(100.0, 120.0, [0.382, 0.5, 0.618])
    assert levels[0.382] > levels[0.5] > levels[0.618]

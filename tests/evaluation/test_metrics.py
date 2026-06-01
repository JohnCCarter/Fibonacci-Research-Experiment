import pandas as pd

from fibengine.core.config import EvaluationConfig, LabelingConfig, Settings
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


def test_down_leg_temporal_fib_matches_facit(synthetic_df):
    """High-before-low facit must not mirror pred fib (Codex P1)."""
    high = Pivot(40, synthetic_df.index[40], 130.0, "high", 2.0)
    low = Pivot(60, synthetic_df.index[60], 105.0, "low", 2.0)
    swing = Swing(start=high, end=low)
    label = SwingLabel(
        exchange="binance",
        symbol="BTC/USDT",
        timeframe="1h",
        high=Point(synthetic_df.index[40].isoformat(), 130.0),
        low=Point(synthetic_df.index[60].isoformat(), 105.0),
    )
    m = evaluate(
        synthetic_df,
        swing,
        label,
        atr_value=2.0,
        cfg=EvaluationConfig(),
        settings=Settings(labeling=LabelingConfig(mtf_disambiguation=False)),
    )
    assert m["mean_fib_err_frac"] == 0.0
    assert m["fib_agree"] == 1.0


def test_mtf_time_errors_use_same_timeframe(monkeypatch, synthetic_df):
    """When facit times resolve on 1d, pred bars must use 1d too (Codex P2)."""
    from fibengine.evaluation import metrics as metrics_mod
    from fibengine.labeling.mtf_disambiguation import (
        MTF_RESOLVED,
        DisambiguatedEndpoints,
    )

    high = Pivot(40, synthetic_df.index[40], 130.0, "high", 2.0)
    low = Pivot(60, synthetic_df.index[60], 105.0, "low", 2.0)
    swing = Swing(start=high, end=low)
    label = SwingLabel(
        exchange="binance",
        symbol="BTC/USDT",
        timeframe="1w",
        high=Point(synthetic_df.index[40].isoformat(), 130.0),
        low=Point(synthetic_df.index[60].isoformat(), 105.0),
    )
    hi_ts = synthetic_df.index[40].isoformat()
    lo_ts = synthetic_df.index[60].isoformat()

    def fake_disambiguate(_label, _df, _settings):
        return DisambiguatedEndpoints(
            high_price=130.0,
            low_price=105.0,
            high_timestamp=hi_ts,
            low_timestamp=lo_ts,
            mtf_status=MTF_RESOLVED,
            same_htf_candle=False,
            order="high_then_low",
            fib_start_price=130.0,
            fib_end_price=105.0,
            time_df_timeframe="1d",
            resolution_kind="test",
        )

    monkeypatch.setattr(metrics_mod, "disambiguate_label_endpoints", fake_disambiguate)
    monkeypatch.setattr(metrics_mod, "load_candles", lambda _cfg: synthetic_df)

    m = evaluate(
        synthetic_df,
        swing,
        label,
        atr_value=2.0,
        cfg=EvaluationConfig(time_tol_bars=5),
    )
    assert m["high_time_err_bars"] == 0
    assert m["low_time_err_bars"] == 0
    assert m["time_agree"] == 1.0

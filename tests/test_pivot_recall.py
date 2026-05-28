from fibengine.config import Settings
from fibengine.evaluation import pivot_recall
from fibengine.evaluation.pivot_recall import _nearest_pivot, evaluate_label_recall
from fibengine.labeling.store import Point, SwingLabel
from fibengine.models import Pivot


def test_nearest_pivot_filters_by_kind(synthetic_df):
    pivots = [
        Pivot(10, synthetic_df.index[10], 110.0, "low", 1.0),
        Pivot(12, synthetic_df.index[12], 120.0, "high", 1.0),
    ]
    pivot, dist = _nearest_pivot(pivots, target_bar=11, kind="high")
    assert pivot == pivots[1]
    assert dist == 1


def test_evaluate_label_recall_hits_near_synthetic_pivots(monkeypatch, synthetic_df):
    label = SwingLabel(
        exchange="binance",
        symbol="BTC/USDT",
        timeframe="1h",
        high=Point(synthetic_df.index[60].isoformat(), 130.0),
        low=Point(synthetic_df.index[40].isoformat(), 105.0),
    )
    pivots = [
        Pivot(40, synthetic_df.index[40], 105.0, "low", 2.0),
        Pivot(60, synthetic_df.index[60], 130.0, "high", 2.0),
    ]
    monkeypatch.setattr(pivot_recall, "load_candles", lambda _cfg: synthetic_df)
    monkeypatch.setattr(pivot_recall, "detect_pivots", lambda _df, _cfg: pivots)

    row = evaluate_label_recall(Settings(), label, tol_bars=1)

    assert row["high_hit"] is True
    assert row["low_hit"] is True
    assert row["both_hit"] is True

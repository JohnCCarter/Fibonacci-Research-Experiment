from fibengine.core.config import Settings
from fibengine.core.models import Pivot
from fibengine.evaluation import pivot_recall
from fibengine.evaluation.pivot_recall import (
    _nearest_pivot,
    evaluate_label_recall,
    summarize_recall,
)
from fibengine.labeling.store import Point, SwingLabel


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
        exchange="Bitfinex",
        symbol="BTC/USD",
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
    assert row["out_of_window"] is False


def test_out_of_window_label_does_not_count_as_recall_hit(monkeypatch, synthetic_df):
    import pandas as pd

    future = (synthetic_df.index[-1] + pd.Timedelta(days=365)).isoformat()
    label = SwingLabel(
        exchange="Bitfinex",
        symbol="BTC/USD",
        timeframe="1h",
        high=Point(future, 130.0),
        low=Point(future, 105.0),
    )
    pivots = [
        Pivot(40, synthetic_df.index[40], 105.0, "low", 2.0),
        Pivot(60, synthetic_df.index[60], 130.0, "high", 2.0),
    ]
    monkeypatch.setattr(pivot_recall, "load_candles", lambda _cfg: synthetic_df)
    monkeypatch.setattr(pivot_recall, "detect_pivots", lambda _df, _cfg: pivots)

    row = evaluate_label_recall(Settings(), label, tol_bars=1)

    assert row["out_of_window"] is True
    assert row["high_hit"] is False
    assert row["low_hit"] is False
    assert row["both_hit"] is False
    assert row["high_dist_bars"] is None
    assert row["low_dist_bars"] is None


def test_summarize_recall_makes_exclusion_explicit():
    rows = [
        {"out_of_window": False, "both_hit": True, "high_hit": True, "low_hit": True},
        {"out_of_window": False, "both_hit": False, "high_hit": True, "low_hit": False},
        {"out_of_window": True, "both_hit": False, "high_hit": False, "low_hit": False},
    ]
    summary = summarize_recall(rows)
    assert summary["n_labels"] == 3
    assert summary["n_in_window"] == 2
    assert summary["n_excluded_out_of_window"] == 1
    # Recall mÃ¤ts BARA pÃ¥ in-window-samplet, inte pÃ¥ de 3 totalt.
    assert summary["both_hit_rate"] == 0.5
    assert summary["high_hit_rate"] == 1.0
    assert summary["low_hit_rate"] == 0.5


def test_summarize_recall_splits_mtf_skipped_from_out_of_window():
    rows = [
        {"out_of_window": True, "both_hit": False, "high_hit": False, "low_hit": False},
        {
            "out_of_window": False,
            "skipped_mtf": True,
            "both_hit": False,
            "high_hit": False,
            "low_hit": False,
        },
        {"out_of_window": False, "both_hit": True, "high_hit": True, "low_hit": True},
    ]
    summary = summarize_recall(rows)
    assert summary["n_excluded_out_of_window"] == 1
    assert summary["n_excluded_mtf_unresolved"] == 1
    assert summary["n_in_window"] == 1
    assert summary["excluded_frac"] == round(2 / 3, 4)


def test_summarize_recall_handles_all_excluded():
    rows = [{"out_of_window": True, "both_hit": False, "high_hit": False, "low_hit": False}]
    summary = summarize_recall(rows)
    assert summary["n_in_window"] == 0
    assert summary["excluded_frac"] == 1.0
    assert summary["both_hit_rate"] is None


def test_run_pivot_recall_excludes_machine_labels(monkeypatch, tmp_path, synthetic_df):
    # Integritet: maskin-labels fÃ¥r inte bli ground truth (cirkulÃ¤rt).
    from fibengine.labeling import store
    from fibengine.labeling.store import Point, SwingLabel, save_label

    monkeypatch.setattr(store, "LABELS_DIR", tmp_path)
    monkeypatch.setattr(pivot_recall, "PIVOT_RECALL_RESULTS", tmp_path / "pivot_recall.jsonl")
    monkeypatch.setattr(pivot_recall, "load_candles", lambda _cfg: synthetic_df)
    monkeypatch.setattr(pivot_recall, "detect_pivots", lambda _df, _cfg: [])

    pts = {
        "high": Point(synthetic_df.index[60].isoformat(), 130.0),
        "low": Point(synthetic_df.index[40].isoformat(), 105.0),
    }
    save_label(SwingLabel(exchange="Bitfinex", symbol="BTC/USD", timeframe="1h", **pts))
    save_label(
        SwingLabel(exchange="Bitfinex", symbol="ETH/USD", timeframe="1h", source="machine", **pts)
    )

    rows = pivot_recall.run_pivot_recall(Settings())

    # Bara den mÃ¤nskliga labeln evaluerades.
    assert len(rows) == 1
    assert rows[0]["symbol"] == "BTC/USD"

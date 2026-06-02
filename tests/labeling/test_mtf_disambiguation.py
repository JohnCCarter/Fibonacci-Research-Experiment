import pandas as pd

from fibengine.core.config import LabelingConfig, Settings
from fibengine.labeling.mtf_disambiguation import (
    MTF_NOT_APPLICABLE,
    MTF_RESOLVED,
    MTF_UNRESOLVED,
    RESOLUTION_FRACTAL_ENDPOINTS,
    RESOLUTION_SAME_CANDLE_DERIVED,
    RESOLUTION_SAME_CANDLE_SAVED,
    disambiguate_label_endpoints,
)
from fibengine.labeling.store import Point, SwingLabel


def _weekly_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "open": [100.0, 105.0],
            "high": [120.0, 110.0],
            "low": [80.0, 90.0],
            "close": [110.0, 100.0],
            "volume": [1.0, 1.0],
        },
        index=pd.to_datetime(
            ["2026-03-23 00:00:00+00:00", "2026-03-30 00:00:00+00:00"],
            utc=True,
        ),
    )


def _label_same_week(*, with_mtf: bool) -> SwingLabel:
    ts = "2026-03-23T00:00:00+00:00"
    mtf = None
    if with_mtf:
        mtf = {
            "timeframe": "1w",
            "resolved_by": "lower_timeframe",
            "resolution_timeframe": "1d",
            "high_daily_timestamp": "2026-03-25T00:00:00+00:00",
            "low_daily_timestamp": "2026-03-28T00:00:00+00:00",
            "order": "high_then_low",
        }
    return SwingLabel(
        exchange="Bitfinex",
        symbol="BTC/USD",
        timeframe="1w",
        high=Point(ts, 120.0),
        low=Point(ts, 80.0),
        same_candle_mtf_resolution=mtf,
    )


def test_same_htf_off_skips_unresolved():
    settings = Settings(labeling=LabelingConfig(mtf_disambiguation=False))
    end = disambiguate_label_endpoints(_label_same_week(with_mtf=True), _weekly_df(), settings)
    assert end.mtf_status == MTF_UNRESOLVED
    assert end.skip_evaluation


def test_same_htf_on_without_metadata_derives_from_daily(monkeypatch):
    weekly = _weekly_df()
    daily = pd.DataFrame(
        {
            "open": [100.0] * 7,
            "high": [105.0, 106.0, 120.0, 108.0, 109.0, 110.0, 111.0],
            "low": [95.0, 94.0, 93.0, 92.0, 91.0, 80.0, 89.0],
            "close": [100.0] * 7,
            "volume": [1.0] * 7,
        },
        index=pd.to_datetime(
            [
                "2026-03-23 00:00:00+00:00",
                "2026-03-24 00:00:00+00:00",
                "2026-03-25 00:00:00+00:00",
                "2026-03-26 00:00:00+00:00",
                "2026-03-27 00:00:00+00:00",
                "2026-03-28 00:00:00+00:00",
                "2026-03-29 00:00:00+00:00",
            ],
            utc=True,
        ),
    )
    settings = Settings(labeling=LabelingConfig(mtf_disambiguation=True))
    monkeypatch.setattr(
        "fibengine.labeling.mtf_disambiguation.load_candles",
        lambda _cfg: daily,
    )
    end = disambiguate_label_endpoints(_label_same_week(with_mtf=False), weekly, settings)
    assert end.mtf_status == MTF_RESOLVED
    assert end.resolution_kind == RESOLUTION_SAME_CANDLE_DERIVED
    assert not end.skip_evaluation


def test_resolved_uses_htf_prices_and_ltf_order(monkeypatch):
    weekly = _weekly_df()
    daily = pd.DataFrame(
        {
            "open": [100.0] * 7,
            "high": [105.0, 106.0, 120.0, 108.0, 109.0, 110.0, 111.0],
            "low": [95.0, 94.0, 93.0, 92.0, 91.0, 80.0, 89.0],
            "close": [100.0] * 7,
            "volume": [1.0] * 7,
        },
        index=pd.to_datetime(
            [
                "2026-03-23 00:00:00+00:00",
                "2026-03-24 00:00:00+00:00",
                "2026-03-25 00:00:00+00:00",
                "2026-03-26 00:00:00+00:00",
                "2026-03-27 00:00:00+00:00",
                "2026-03-28 00:00:00+00:00",
                "2026-03-29 00:00:00+00:00",
            ],
            utc=True,
        ),
    )
    settings = Settings(labeling=LabelingConfig(mtf_disambiguation=True))
    settings.data = settings.data.model_copy(update={"timeframe": "1w"})

    monkeypatch.setattr(
        "fibengine.labeling.mtf_disambiguation.load_candles",
        lambda _cfg: daily,
    )
    end = disambiguate_label_endpoints(_label_same_week(with_mtf=True), weekly, settings)
    assert end.mtf_status == MTF_RESOLVED
    assert end.resolution_kind == RESOLUTION_SAME_CANDLE_SAVED
    assert end.high_price == 120.0
    assert end.low_price == 80.0
    assert end.fib_start_price == 120.0
    assert end.fib_end_price == 80.0
    assert end.time_df_timeframe == "1d"


def _label_distinct_weeks() -> SwingLabel:
    return SwingLabel(
        exchange="Bitfinex",
        symbol="BTC/USD",
        timeframe="1w",
        high=Point("2026-03-23T00:00:00+00:00", 120.0),
        low=Point("2026-03-30T00:00:00+00:00", 90.0),
    )


def test_non_mtf_timeframe_on_behaves_like_off():
    label = SwingLabel(
        exchange="Bitfinex",
        symbol="BTC/USD",
        timeframe="4h",
        high=Point("2026-03-23T00:00:00+00:00", 120.0),
        low=Point("2026-03-30T00:00:00+00:00", 90.0),
    )
    settings = Settings(labeling=LabelingConfig(mtf_disambiguation=True))
    end = disambiguate_label_endpoints(label, _weekly_df(), settings)
    assert end.mtf_status == MTF_NOT_APPLICABLE
    assert not end.skip_evaluation


def test_distinct_weeks_off_uses_weekly_timestamps():
    settings = Settings(labeling=LabelingConfig(mtf_disambiguation=False))
    end = disambiguate_label_endpoints(_label_distinct_weeks(), _weekly_df(), settings)
    assert end.mtf_status == MTF_NOT_APPLICABLE
    assert end.time_df_timeframe == "1w"
    assert not end.skip_evaluation


def test_distinct_weeks_on_fractal_endpoints(monkeypatch):
    weekly = _weekly_df()
    daily = pd.DataFrame(
        {
            "open": [100.0] * 10,
            "high": [105.0, 120.0, 108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 114.0, 115.0],
            "low": [95.0, 94.0, 93.0, 92.0, 91.0, 90.0, 89.0, 88.0, 70.0, 87.0],
            "close": [100.0] * 10,
            "volume": [1.0] * 10,
        },
        index=pd.to_datetime(
            [
                "2026-03-23 00:00:00+00:00",
                "2026-03-24 00:00:00+00:00",
                "2026-03-25 00:00:00+00:00",
                "2026-03-26 00:00:00+00:00",
                "2026-03-27 00:00:00+00:00",
                "2026-03-28 00:00:00+00:00",
                "2026-03-29 00:00:00+00:00",
                "2026-03-30 00:00:00+00:00",
                "2026-03-31 00:00:00+00:00",
                "2026-04-01 00:00:00+00:00",
            ],
            utc=True,
        ),
    )
    settings = Settings(labeling=LabelingConfig(mtf_disambiguation=True))
    monkeypatch.setattr(
        "fibengine.labeling.mtf_disambiguation.load_candles",
        lambda _cfg: daily,
    )
    end = disambiguate_label_endpoints(_label_distinct_weeks(), weekly, settings)
    assert end.mtf_status == MTF_RESOLVED
    assert end.resolution_kind == RESOLUTION_FRACTAL_ENDPOINTS
    assert end.high_price == 120.0
    assert end.low_price == 90.0
    assert end.high_timestamp == "2026-03-24T00:00:00+00:00"
    assert "2026-03-31" in end.low_timestamp
    assert end.time_df_timeframe == "1d"
    assert not end.skip_evaluation

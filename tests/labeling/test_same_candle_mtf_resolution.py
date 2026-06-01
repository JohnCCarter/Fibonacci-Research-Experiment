import pandas as pd

from fibengine.core.config import LabelingConfig, Settings
from fibengine.labeling.same_candle_mtf_resolution import (
    attempt_same_candle_mtf_resolution,
    build_same_candle_mtf_metadata,
    daily_candles_in_week,
)


def _weekly_and_daily_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    weekly = pd.DataFrame(
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
    daily = pd.DataFrame(
        {
            "open": [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0],
            "high": [105.0, 106.0, 120.0, 108.0, 109.0, 110.0, 111.0, 112.0],
            "low": [95.0, 94.0, 93.0, 92.0, 91.0, 80.0, 89.0, 88.0],
            "close": [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
            "volume": [1.0] * 8,
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
            ],
            utc=True,
        ),
    )
    return weekly, daily


def test_daily_candles_in_week_slices_to_week_boundaries():
    weekly, daily = _weekly_and_daily_frames()
    week = daily_candles_in_week(weekly, daily, 0)
    assert len(week) == 7
    assert week.index[0] == weekly.index[0]
    assert week.index[-1].isoformat().startswith("2026-03-29")


def test_attempt_resolution_finds_distinct_daily_high_and_low():
    weekly, daily = _weekly_and_daily_frames()
    settings = Settings(
        labeling=LabelingConfig(enable_same_candle_mtf_resolution=True),
    )
    settings.data = settings.data.model_copy(update={"timeframe": "1w"})

    def fake_load(cfg):
        assert cfg.timeframe == "1d"
        return daily

    meta, err = attempt_same_candle_mtf_resolution(settings, weekly, 0, load_candles_fn=fake_load)
    assert err is None
    assert meta is not None
    assert meta["resolution_timeframe"] == "1d"
    assert meta["resolved_by"] == "lower_timeframe"
    assert "2026-03-25" in meta["high_daily_timestamp"]
    assert "2026-03-28" in meta["low_daily_timestamp"]
    assert meta["order"] == "high_then_low"


def test_attempt_resolution_rejects_single_daily_bar():
    weekly, daily = _weekly_and_daily_frames()
    flat = daily.copy()
    flat.loc[:, "high"] = 100.0
    flat.loc[:, "low"] = 100.0
    settings = Settings(
        labeling=LabelingConfig(enable_same_candle_mtf_resolution=True),
    )
    settings.data = settings.data.model_copy(update={"timeframe": "1w"})

    meta, err = attempt_same_candle_mtf_resolution(
        settings,
        weekly,
        0,
        load_candles_fn=lambda _cfg: flat,
    )
    assert meta is None
    assert err is not None
    assert "one 1d bar" in err


def test_build_metadata_order_low_then_high():
    hi = pd.Timestamp("2026-03-28", tz="UTC")
    lo = pd.Timestamp("2026-03-23", tz="UTC")
    meta = build_same_candle_mtf_metadata("1w", "1d", hi, lo)
    assert meta["order"] == "low_then_high"

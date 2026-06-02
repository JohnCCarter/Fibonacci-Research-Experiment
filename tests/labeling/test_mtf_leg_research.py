import pandas as pd

from fibengine.core.config import LabelingConfig, Settings
from fibengine.labeling.mtf_leg_research import analyze_mtf_leg_daily_fib
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


def test_retrace_detects_618_touch(monkeypatch):
    weekly = _weekly_df()
    daily = pd.DataFrame(
        {
            "open": [100.0] * 10,
            "high": [105.0, 120.0, 108.0, 109.0, 110.0, 111.0, 112.0, 113.0, 95.0, 90.0],
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
    label = SwingLabel(
        exchange="Bitfinex",
        symbol="BTC/USD",
        timeframe="1w",
        high=Point("2026-03-23T00:00:00+00:00", 120.0),
        low=Point("2026-03-30T00:00:00+00:00", 90.0),
    )
    settings = Settings(labeling=LabelingConfig(mtf_disambiguation=False))
    monkeypatch.setattr(
        "fibengine.labeling.mtf_disambiguation.load_candles",
        lambda _cfg: daily,
    )
    monkeypatch.setattr(
        "fibengine.labeling.mtf_leg_research.load_candles",
        lambda _cfg: daily,
    )
    report = analyze_mtf_leg_daily_fib(label, weekly, settings)
    assert report.mtf_status == "resolved"
    assert report.impulse is not None and report.impulse.bar_count > 0
    assert report.retrace is not None and report.retrace.bar_count > 0

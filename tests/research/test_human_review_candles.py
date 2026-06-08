from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from fibengine.research.human_review_candles import (
    CANDLE_DOWN,
    CANDLE_UP,
    draw_mplfinance_candles,
    draw_review_candles,
    review_mpf_style,
)


def _ohlc_df(n: int = 40) -> pd.DataFrame:
    x = np.linspace(100, 110, n)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open": x,
            "high": x + 0.6,
            "low": x - 0.6,
            "close": x + np.sin(np.arange(n)) * 0.3,
            "volume": np.ones(n),
        },
        index=idx,
    )


def test_review_mpf_style_uses_shared_up_down_colors():
    light = review_mpf_style(dark_theme=False)
    dark = review_mpf_style(dark_theme=True)
    assert light["marketcolors"]["candle"]["up"] == CANDLE_UP
    assert light["marketcolors"]["candle"]["down"] == CANDLE_DOWN
    assert dark["marketcolors"]["candle"]["up"] == CANDLE_UP
    assert dark["marketcolors"]["candle"]["down"] == CANDLE_DOWN


def test_draw_mplfinance_candles_light_and_dark():
    df = _ohlc_df()
    for dark in (False, True):
        fig, ax = plt.subplots()
        draw_mplfinance_candles(ax, df, dark_theme=dark)
        assert len(ax.lines) + len(ax.collections) + len(ax.patches) > 0
        plt.close(fig)


def test_draw_review_candles_close_line_fallback():
    df = _ohlc_df()
    fig, ax = plt.subplots()
    draw_review_candles(ax, df, candlestick=False, dark_theme=True)
    assert len(ax.lines) == 1
    plt.close(fig)

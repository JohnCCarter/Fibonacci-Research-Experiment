import pandas as pd
import pytest

from fibengine.core.models import Pivot, Swing
from fibengine.viz.plot import _nearest_bar, plot_prediction


def test_nearest_bar_handles_non_exact_timestamp(synthetic_df):
    ts = synthetic_df.index[10] + pd.Timedelta(minutes=20)
    assert _nearest_bar(synthetic_df, ts.isoformat()) == 10


@pytest.mark.parametrize("candlestick", [False, True])
def test_plot_prediction_routes_through_shared_helper(synthetic_df, tmp_path, candlestick):
    """Both the close-line fallback and the mplfinance candlestick path (routed through
    the shared ``draw_review_candles`` helper) render a non-empty PNG. This checks routing +
    no-crash, not overlay alignment — x-position alignment (0..len(df)-1) is the helper's
    pre-existing contract, already exercised by labeling/tool.py and human_review_charts.py."""
    start = Pivot(index=0, timestamp=synthetic_df.index[0], price=100.0, kind="low", prominence=1.0)
    end = Pivot(
        index=20, timestamp=synthetic_df.index[20], price=120.0, kind="high", prominence=1.0
    )
    swing = Swing(start=start, end=end, status="confirmed")
    out = plot_prediction(
        synthetic_df,
        swing,
        [0.382, 0.5, 0.618],
        tmp_path / f"pred_{candlestick}.png",
        candlestick=candlestick,
    )
    assert out.exists() and out.stat().st_size > 0

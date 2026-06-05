from pathlib import Path

from fibengine.core.models import Pivot, Swing
from fibengine.viz.plot import plot_prediction


def test_plot_prediction_writes_mplfinance_chart(synthetic_df, tmp_path: Path):
    swing = Swing(
        start=Pivot(20, synthetic_df.index[20], float(synthetic_df.iloc[20]["high"]), "high", 1.0),
        end=Pivot(40, synthetic_df.index[40], float(synthetic_df.iloc[40]["low"]), "low", 1.0),
        status="confirmed",
    )

    out = plot_prediction(synthetic_df, swing, [0.382, 0.618], tmp_path / "chart.png")

    assert out.exists()
    assert out.stat().st_size > 0

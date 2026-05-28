import pandas as pd

from fibengine.viz.plot import _nearest_bar


def test_nearest_bar_handles_non_exact_timestamp(synthetic_df):
    ts = synthetic_df.index[10] + pd.Timedelta(minutes=20)
    assert _nearest_bar(synthetic_df, ts.isoformat()) == 10

import pytest
from pandera.errors import SchemaError

from fibengine.data.loader import load_candles_from_path
from fibengine.data.schema import validate_candles


def test_validate_candles_accepts_valid_ohlcv(synthetic_df):
    validated = validate_candles(synthetic_df)

    assert list(validated.columns) == ["open", "high", "low", "close", "volume"]


def test_validate_candles_rejects_inverted_range(synthetic_df):
    invalid = synthetic_df.copy()
    invalid.iloc[0, invalid.columns.get_loc("high")] = invalid.iloc[0]["low"] - 1.0

    with pytest.raises(SchemaError):
        validate_candles(invalid)


def test_load_candles_from_path_rejects_negative_volume(tmp_path, synthetic_df):
    invalid = synthetic_df.copy()
    invalid.iloc[1, invalid.columns.get_loc("volume")] = -1.0
    path = tmp_path / "candles.csv"
    invalid.reset_index(names="timestamp").to_csv(path, index=False)

    with pytest.raises(SchemaError):
        load_candles_from_path(path)

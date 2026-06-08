import pandas as pd
import pandera as pa
import pytest

from fibengine.validation.schemas import (
    OHLCV_COLUMNS,
    FetchManifest,
    ReviewRow,
    validate_ohlcv_df,
)


def test_validate_ohlcv_df_accepts_good_frame():
    idx = pd.date_range("2024-01-01", periods=3, freq="D", tz="UTC")
    df = pd.DataFrame(
        {
            "open": [100.0, 101.0, 102.0],
            "high": [101.0, 102.0, 103.0],
            "low": [99.0, 100.0, 101.0],
            "close": [100.5, 101.5, 102.5],
            "volume": [1.0, 2.0, 3.0],
        },
        index=idx,
    )
    out = validate_ohlcv_df(df)
    assert list(out.columns) == list(df.columns)


def test_validate_ohlcv_df_rejects_high_below_low():
    idx = pd.date_range("2024-01-01", periods=2, freq="D", tz="UTC")
    df = pd.DataFrame(
        {
            "open": [100.0, 100.0],
            "high": [99.0, 101.0],
            "low": [100.0, 100.0],
            "close": [100.0, 100.0],
            "volume": [1.0, 1.0],
        },
        index=idx,
    )
    with pytest.raises(pa.errors.SchemaError):
        validate_ohlcv_df(df)


def test_validate_ohlcv_df_strict_false_skips_checks():
    df = pd.DataFrame({"open": [1.0]})
    assert validate_ohlcv_df(df, strict=False) is df


def test_review_row_model():
    row = ReviewRow(
        review_id="id",
        symbol="BTC/USD",
        timeframe="1d",
        exchange="bitfinex",
        fib_level="0.5",
        fib_price=100.0,
        event_bar=10,
        event_time="2024-01-01T00:00:00+00:00",
        auto_candidate="continuation_candidate",
    )
    assert row.human_label == ""


def test_fetch_manifest_roundtrip():
    from datetime import UTC, datetime

    m = FetchManifest(
        exchange="bitfinex",
        symbol="BTC/USD",
        timeframe="1d",
        limit=500,
        fetched_at_utc=datetime.now(UTC),
        row_count=10,
        first_ts=datetime(2024, 1, 1, tzinfo=UTC),
        last_ts=datetime(2024, 1, 10, tzinfo=UTC),
        csv_path="/tmp/limit_500.csv",
    )
    parsed = FetchManifest.model_validate_json(m.model_dump_json())
    assert parsed.row_count == 10
    assert set(OHLCV_COLUMNS) == {"open", "high", "low", "close", "volume"}

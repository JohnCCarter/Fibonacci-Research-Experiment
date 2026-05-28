from argparse import Namespace

from fibengine.core.config import DataConfig, Settings
from fibengine.labeling import tool
from fibengine.labeling.tool import (
    LabelWorkspace,
    _apply_cli_overrides,
    _csv_values,
    _cycle,
    _default_timeframes,
    _fib_prices_from_picks,
    _label_warnings,
)


def test_apply_cli_data_overrides():
    settings = _apply_cli_overrides(
        Settings(),
        Namespace(exchange=None, symbol="ETH/USDT", timeframe="1w", limit=300),
    )

    assert settings.data.symbol == "ETH/USDT"
    assert settings.data.timeframe == "1w"
    assert settings.data.limit == 300


def test_cycle_wraps_values():
    assert _cycle(["15m", "1h", "1w"], "1w", 1) == "15m"
    assert _cycle(["15m", "1h", "1w"], "15m", -1) == "1w"


def test_fib_prices_from_picks_handles_up_and_down_legs():
    up = _fib_prices_from_picks(
        {"low": (1, 100.0), "high": (2, 120.0)},
        [0.5],
    )
    down = _fib_prices_from_picks(
        {"high": (1, 120.0), "low": (2, 100.0)},
        [0.5],
    )

    assert up[0.5] == 110.0
    assert down[0.5] == 110.0


def test_workspace_cycles_market_without_mutating_other_fields(monkeypatch, synthetic_df):
    seen: list[DataConfig] = []

    def fake_load_candles(cfg):
        seen.append(cfg)
        return synthetic_df

    monkeypatch.setattr(tool, "load_candles", fake_load_candles)
    monkeypatch.setattr(tool, "find_label", lambda *_args: None)
    settings = Settings()
    workspace = LabelWorkspace(
        settings=settings,
        symbols=["BTC/USDT", "ETH/USDT"],
        timeframes=["1h", "1w"],
    )

    workspace.cycle_symbol(1)
    workspace.cycle_timeframe(1)

    assert workspace.data.symbol == "ETH/USDT"
    assert workspace.data.timeframe == "1w"
    assert seen[-1].symbol == "ETH/USDT"
    assert seen[-1].timeframe == "1w"


def test_default_timeframes_include_higher_timeframes():
    assert _default_timeframes("1h") == ["15m", "30m", "1h", "4h", "1d", "1w", "1M"]
    assert _default_timeframes("5m") == ["5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"]


def test_csv_values_normalizes_higher_timeframe_aliases():
    assert _csv_values("daily,weekly,monthly", []) == ["1d", "1w", "1M"]


def test_label_warnings_reject_same_bar_and_edges(synthetic_df):
    warnings = _label_warnings(synthetic_df, high_idx=0, low_idx=0, settings=Settings())

    assert any("same candle" in warning for warning in warnings)
    assert any("left edge" in warning for warning in warnings)


def test_label_warnings_allows_distinct_interior_points(synthetic_df):
    warnings = _label_warnings(synthetic_df, high_idx=5, low_idx=7, settings=Settings())

    assert warnings == []

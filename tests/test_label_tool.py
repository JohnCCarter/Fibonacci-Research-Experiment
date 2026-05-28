from argparse import Namespace

from fibengine.config import DataConfig, Settings
from fibengine.labeling import tool
from fibengine.labeling.tool import (
    LabelWorkspace,
    _apply_cli_overrides,
    _cycle,
    _fib_prices_from_picks,
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

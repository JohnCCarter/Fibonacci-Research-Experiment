from argparse import Namespace

from fibengine.config import DataConfig
from fibengine.labeling import tool


def test_run_label_tool_applies_cli_data_overrides(monkeypatch, synthetic_df):
    seen = {}

    class DummySettings:
        data = DataConfig()

    monkeypatch.setattr(tool, "load_settings", lambda: DummySettings())
    monkeypatch.setattr(tool, "find_label", lambda *_args: None)

    def fake_load_candles(cfg):
        seen["cfg"] = cfg
        return synthetic_df

    monkeypatch.setattr(tool, "load_candles", fake_load_candles)

    class DummyCanvas:
        def mpl_connect(self, *_args):
            return None

        def draw_idle(self):
            return None

    class DummyFig:
        canvas = DummyCanvas()

    class DummyAxis:
        collections = []
        texts = []

        def plot(self, *_args, **_kwargs):
            return None

        def set_title(self, *_args, **_kwargs):
            return None

    monkeypatch.setattr(tool.plt, "subplots", lambda **_kwargs: (DummyFig(), DummyAxis()))
    monkeypatch.setattr(tool.plt, "show", lambda: None)

    tool.run_label_tool(Namespace(exchange=None, symbol="ETH/USDT", timeframe="1w", limit=300))

    assert seen["cfg"].symbol == "ETH/USDT"
    assert seen["cfg"].timeframe == "1w"
    assert seen["cfg"].limit == 300

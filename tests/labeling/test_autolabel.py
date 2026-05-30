import pandas as pd

from fibengine.core.config import Settings
from fibengine.core.models import Pivot, Swing
from fibengine.labeling import autolabel, store
from fibengine.labeling.store import Point, SwingLabel, find_label, save_label


def _swing() -> Swing:
    low = Pivot(10, pd.Timestamp("2026-01-01T00:00:00+00:00"), 100.0, "low", 1.0)
    high = Pivot(40, pd.Timestamp("2026-01-02T00:00:00+00:00"), 130.0, "high", 1.0)
    return Swing(start=low, end=high)


def test_label_from_swing_picks_high_and_low_endpoints():
    label = autolabel.label_from_swing(_swing(), "binance", "BTC/USDT", "1h")
    assert label.source == "machine"
    assert label.high.price == 130.0
    assert label.low.price == 100.0
    assert "maskin" in label.note.lower()


def test_autolabel_one_writes_machine_label(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "LABELS_DIR", tmp_path)
    monkeypatch.setattr(autolabel, "load_candles", lambda _cfg: pd.DataFrame())
    monkeypatch.setattr(autolabel, "select_swing", lambda _df, _p, _s: _swing())

    result = autolabel.autolabel_one(Settings(), "binance", "SOL/USDT", "4h")

    assert result["status"] == "written"
    saved = find_label("binance", "SOL/USDT", "4h")
    assert saved is not None
    assert saved.source == "machine"


def test_autolabel_never_overwrites_human(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "LABELS_DIR", tmp_path)
    human = SwingLabel(
        exchange="binance",
        symbol="BTC/USDT",
        timeframe="1h",
        high=Point("2026-01-02T00:00:00+00:00", 999.0),
        low=Point("2026-01-01T00:00:00+00:00", 1.0),
    )
    save_label(human)
    # Skulle skriva en helt annan swing om den inte respekterade human-skyddet.
    monkeypatch.setattr(autolabel, "load_candles", lambda _cfg: pd.DataFrame())
    monkeypatch.setattr(autolabel, "select_swing", lambda _df, _p, _s: _swing())

    result = autolabel.autolabel_one(Settings(), "binance", "BTC/USDT", "1h")

    assert result["status"] == "skipped_human"
    # Den mänskliga labeln är orörd.
    still = find_label("binance", "BTC/USDT", "1h")
    assert still.source == "human"
    assert still.high.price == 999.0

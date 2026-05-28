from fibengine.labeling import store
from fibengine.labeling.store import (
    Point,
    SwingLabel,
    delete_label,
    find_label,
    label_path,
    save_label,
)


def test_find_and_delete_label(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "LABELS_DIR", tmp_path)
    label = SwingLabel(
        exchange="binance",
        symbol="ETH/USDT",
        timeframe="1h",
        high=Point("2026-01-01T00:00:00+00:00", 100.0),
        low=Point("2026-01-01T01:00:00+00:00", 90.0),
    )

    path = save_label(label)
    found = find_label("binance", "ETH/USDT", "1h")

    assert found is not None
    assert found.high.price == 100.0
    assert path.exists()
    assert delete_label(label) is True
    assert find_label("binance", "ETH/USDT", "1h") is None
    assert delete_label(label) is False


def test_label_path_uses_categorized_layout(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "LABELS_DIR", tmp_path)
    label = SwingLabel(
        exchange="binance",
        symbol="BTC/USDT",
        timeframe="1h",
        high=Point("2026-01-01T00:00:00+00:00", 100.0),
        low=Point("2026-01-01T01:00:00+00:00", 90.0),
    )
    path = label_path(label)
    assert path == tmp_path / "binance" / "BTC-USDT" / "1h.json"
    save_label(label)
    assert path.exists()

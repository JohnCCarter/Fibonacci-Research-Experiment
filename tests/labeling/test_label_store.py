from fibengine.labeling import store
from fibengine.labeling.store import (
    Point,
    SwingLabel,
    delete_label,
    find_label,
    label_path,
    list_labels,
    save_label,
)


def _pts() -> dict:
    return {
        "high": Point("2026-01-02T00:00:00+00:00", 110.0),
        "low": Point("2026-01-01T00:00:00+00:00", 100.0),
    }


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


def test_source_defaults_to_human_and_roundtrips(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "LABELS_DIR", tmp_path)
    human = SwingLabel(exchange="binance", symbol="BTC/USDT", timeframe="1h", **_pts())
    machine = SwingLabel(
        exchange="binance", symbol="ETH/USDT", timeframe="1h", source="machine", **_pts()
    )
    save_label(human)
    save_label(machine)

    # Default är human; source läses tillbaka korrekt.
    assert find_label("binance", "BTC/USDT", "1h").source == "human"
    assert find_label("binance", "ETH/USDT", "1h").source == "machine"


def test_list_labels_filters_by_source(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "LABELS_DIR", tmp_path)
    save_label(SwingLabel(exchange="binance", symbol="BTC/USDT", timeframe="1h", **_pts()))
    save_label(
        SwingLabel(
            exchange="binance", symbol="ETH/USDT", timeframe="1h", source="machine", **_pts()
        )
    )

    assert len(list_labels()) == 2
    assert len(list_labels(source="human")) == 1
    assert len(list_labels(source="machine")) == 1
    assert list_labels(source="human")[0].symbol == "BTC/USDT"

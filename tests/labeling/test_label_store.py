import pytest

from fibengine.labeling import store
from fibengine.labeling.store import (
    LegLabel,
    Point,
    SwingLabel,
    delete_label,
    find_label,
    label_path,
    list_labels,
    load_label,
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
        exchange="Bitfinex",
        symbol="ETH/USD",
        timeframe="1h",
        high=Point("2026-01-01T00:00:00+00:00", 100.0),
        low=Point("2026-01-01T01:00:00+00:00", 90.0),
    )

    path = save_label(label)
    found = find_label("Bitfinex", "ETH/USD", "1h")

    assert found is not None
    assert found.high.price == 100.0
    assert path.exists()
    assert delete_label(label) is True
    assert find_label("Bitfinex", "ETH/USD", "1h") is None
    assert delete_label(label) is False


def test_label_path_uses_categorized_layout(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "LABELS_DIR", tmp_path)
    label = SwingLabel(
        exchange="Bitfinex",
        symbol="BTC/USD",
        timeframe="1h",
        high=Point("2026-01-01T00:00:00+00:00", 100.0),
        low=Point("2026-01-01T01:00:00+00:00", 90.0),
    )
    path = label_path(label)
    assert path == tmp_path / "bitfinex" / "BTC-USD" / "1h.json"
    save_label(label)
    assert path.exists()


def test_source_defaults_to_human_and_roundtrips(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "LABELS_DIR", tmp_path)
    human = SwingLabel(exchange="Bitfinex", symbol="BTC/USD", timeframe="1h", **_pts())
    machine = SwingLabel(
        exchange="Bitfinex", symbol="ETH/USD", timeframe="1h", source="machine", **_pts()
    )
    save_label(human)
    save_label(machine)

    # Default Ã¤r human; source lÃ¤ses tillbaka korrekt.
    assert find_label("Bitfinex", "BTC/USD", "1h").source == "human"
    assert find_label("Bitfinex", "ETH/USD", "1h").source == "machine"


def test_list_labels_filters_by_source(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "LABELS_DIR", tmp_path)
    save_label(SwingLabel(exchange="Bitfinex", symbol="BTC/USD", timeframe="1h", **_pts()))
    save_label(
        SwingLabel(
            exchange="Bitfinex", symbol="ETH/USD", timeframe="1h", source="machine", **_pts()
        )
    )

    assert len(list_labels()) == 2
    assert len(list_labels(source="human")) == 1
    assert len(list_labels(source="machine")) == 1
    assert list_labels(source="human")[0].symbol == "BTC/USD"


def test_multi_leg_save_and_load(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "LABELS_DIR", tmp_path)
    legs = [
        LegLabel(
            id="impulse_down",
            high=Point("2026-01-15T00:00:00+00:00", 97_000.0),
            low=Point("2026-01-25T00:00:00+00:00", 86_000.0),
        ),
        LegLabel(
            id="retrace_up",
            high=Point("2026-04-20T00:00:00+00:00", 81_000.0),
            low=Point("2026-02-06T00:00:00+00:00", 60_000.0),
        ),
    ]
    label = SwingLabel(
        exchange="Bitfinex",
        symbol="BTC/USD",
        timeframe="1d",
        high=legs[0].high,
        low=legs[0].low,
        legs=legs,
    )
    path = save_label(label)
    raw = path.read_text()
    assert '"legs"' in raw
    loaded = load_label(path)
    assert len(loaded.all_legs()) == 2
    assert loaded.all_legs()[1].id == "retrace_up"


def _write_label_json(tmp_path, body: str):
    path = tmp_path / "Bitfinex/BTC-USD/1d.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.strip(), encoding="utf-8")
    return path


def test_load_label_rejects_missing_required_field(tmp_path):
    # Missing "low" → fail closed.
    path = _write_label_json(
        tmp_path,
        """
{
  "exchange": "Bitfinex",
  "symbol": "BTC/USD",
  "timeframe": "1d",
  "high": {"timestamp": "2026-01-01T00:00:00+00:00", "price": 110.0}
}
""",
    )
    with pytest.raises(ValueError, match="Invalid swing-label JSON"):
        load_label(path)


def test_load_label_rejects_unknown_key(tmp_path):
    # Unknown top-level key → fail closed (extra="forbid").
    path = _write_label_json(
        tmp_path,
        """
{
  "exchange": "Bitfinex",
  "symbol": "BTC/USD",
  "timeframe": "1d",
  "high": {"timestamp": "2026-01-01T00:00:00+00:00", "price": 110.0},
  "low": {"timestamp": "2026-01-02T00:00:00+00:00", "price": 100.0},
  "bogus": true
}
""",
    )
    with pytest.raises(ValueError, match="Invalid swing-label JSON"):
        load_label(path)


def test_load_label_rejects_non_numeric_price(tmp_path):
    path = _write_label_json(
        tmp_path,
        """
{
  "exchange": "Bitfinex",
  "symbol": "BTC/USD",
  "timeframe": "1d",
  "high": {"timestamp": "2026-01-01T00:00:00+00:00", "price": "not-a-number"},
  "low": {"timestamp": "2026-01-02T00:00:00+00:00", "price": 100.0}
}
""",
    )
    with pytest.raises(ValueError, match="Invalid swing-label JSON"):
        load_label(path)


def test_saved_label_passes_validation_roundtrip(monkeypatch, tmp_path):
    # A label written by save_label must always load back (gate accepts our own output).
    monkeypatch.setattr(store, "LABELS_DIR", tmp_path)
    label = SwingLabel(exchange="Bitfinex", symbol="BTC/USD", timeframe="1h", **_pts())
    path = save_label(label)
    assert load_label(path).source == "human"


def test_multi_leg_without_ids_get_sequential_ids(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "LABELS_DIR", tmp_path)
    path = tmp_path / "Bitfinex/BTC-USD/1d.json"
    path.parent.mkdir(parents=True)
    path.write_text(
        """
{
  "exchange": "Bitfinex",
  "symbol": "BTC/USD",
  "timeframe": "1d",
  "high": {"timestamp": "2026-01-01T00:00:00+00:00", "price": 110.0},
  "low": {"timestamp": "2026-01-02T00:00:00+00:00", "price": 100.0},
  "legs": [
    {"high": {"timestamp": "2026-01-01T00:00:00+00:00", "price": 110.0},
     "low": {"timestamp": "2026-01-02T00:00:00+00:00", "price": 100.0}},
    {"high": {"timestamp": "2026-03-01T00:00:00+00:00", "price": 120.0},
     "low": {"timestamp": "2026-03-02T00:00:00+00:00", "price": 105.0}}
  ]
}
""".strip(),
        encoding="utf-8",
    )
    loaded = load_label(path)
    assert [leg.id for leg in loaded.all_legs()] == ["leg_1", "leg_2"]

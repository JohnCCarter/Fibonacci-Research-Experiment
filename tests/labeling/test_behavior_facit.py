import json

import pandas as pd

from fibengine.labeling.behavior_facit import (
    LevelEvent,
    apply_auto_candidates,
    load_behavior_facit,
    save_behavior_facit,
    scaffold_from_parent,
    validate_behavior_facit,
)
from fibengine.labeling.store import LegLabel, Point, SwingLabel, save_label


def _write_parent(tmp_path, monkeypatch):
    from fibengine.labeling import store

    monkeypatch.setattr(store, "LABELS_DIR", tmp_path)
    legs = [
        LegLabel(
            id="leg_1",
            high=Point("2026-01-15T00:00:00+00:00", 100.0),
            low=Point("2026-01-20T00:00:00+00:00", 80.0),
        ),
    ]
    label = SwingLabel(
        exchange="binance",
        symbol="BTC/USDT",
        timeframe="1d",
        high=legs[0].high,
        low=legs[0].low,
        legs=legs,
    )
    return save_label(label)


def _candles_down_leg() -> pd.DataFrame:
    idx = pd.date_range("2026-01-15", periods=8, freq="D", tz="UTC")
    return pd.DataFrame(
        {
            "open": [100, 98, 95, 92, 88, 86, 82, 80],
            "high": [100, 99, 96, 93, 89, 87, 83, 81],
            "low": [99, 96, 93, 90, 86, 84, 80, 79],
            "close": [98, 95, 92, 89, 85, 83, 80, 80],
            "volume": [1.0] * 8,
        },
        index=idx,
    )


def test_v3_events_validate(tmp_path, monkeypatch):
    parent = _write_parent(tmp_path, monkeypatch)
    facit = scaffold_from_parent(parent, leg_ids=("leg_1",))
    lv = facit.legs[0].levels["0.618"]
    lv.events = [
        LevelEvent(
            event_bar="2026-03-10T00:00:00+00:00",
            level="0.618",
            price=87.6,
            human_label="continuation",
        ),
        LevelEvent(
            event_bar="2026-04-20T00:00:00+00:00",
            level="0.618",
            price=87.6,
            human_label="rejection",
        ),
    ]
    issues = validate_behavior_facit(facit, parent, require_human=True)
    assert not issues

    issues_empty = validate_behavior_facit(facit, parent, require_human=False)
    assert not any("human_label not set" in i for i in issues_empty)


def test_auto_candidate_in_event_not_facit(tmp_path, monkeypatch):
    parent = _write_parent(tmp_path, monkeypatch)
    facit = scaffold_from_parent(parent, leg_ids=("leg_1",))
    apply_auto_candidates(facit, _candles_down_leg())

    ev = facit.legs[0].levels["0.618"].events[0]
    assert ev.auto_candidate is not None
    assert ev.human_label is None

    issues = validate_behavior_facit(facit, parent, require_human=True)
    assert any("human_label not set" in i for i in issues)


def test_legacy_v2_loads_as_events(tmp_path):
    raw = {
        "schema_version": 2,
        "parent_label_path": "x",
        "exchange": "binance",
        "symbol": "BTC/USDT",
        "timeframe": "1d",
        "legs": [
            {
                "leg_id": "leg_1",
                "leg_direction": "down",
                "levels": {
                    "0.618": {
                        "human_label": "rejection",
                        "event_bar": "2026-01-29T00:00:00+00:00",
                        "price": 87.0,
                    }
                },
            }
        ],
    }
    path = tmp_path / "legacy.json"
    path.write_text(json.dumps(raw))
    facit = load_behavior_facit(path)
    evs = facit.legs[0].levels["0.618"].events
    assert len(evs) == 1
    assert evs[0].human_label == "rejection"


def test_save_roundtrip_v3(tmp_path, monkeypatch):
    parent = _write_parent(tmp_path, monkeypatch)
    facit = scaffold_from_parent(parent, leg_ids=("leg_1",))
    facit.legs[0].levels["0.618"].events = [
        LevelEvent(
            event_bar="2026-03-10T00:00:00+00:00",
            level="0.618",
            human_label="continuation",
        )
    ]

    out = tmp_path / "behavior.json"
    save_behavior_facit(facit, out)
    raw = json.loads(out.read_text())

    assert raw["schema_version"] == 3
    assert raw["facit_model"] == "events_per_level"
    lvl = raw["legs"][0]["levels"]["0.618"]
    assert "events" in lvl
    assert lvl["events"][0]["human_label"] == "continuation"
    assert "human_label" not in lvl

    loaded = load_behavior_facit(out)
    assert loaded.legs[0].levels["0.618"].events[0].human_label == "continuation"

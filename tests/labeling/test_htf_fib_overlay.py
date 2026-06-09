import json

from fibengine.labeling import htf_fib_overlay as overlay
from fibengine.labeling.human_fib import FibAnchor, make_annotation, save_annotation
from fibengine.labeling.store import set_labels_dir


def _sample_ann(symbol="BTC/USD", timeframe="1M"):
    return make_annotation(
        symbol=symbol,
        timeframe=timeframe,
        exchange="bitfinex",
        anchor_a=FibAnchor(time="2018-01-01T00:00:00+00:00", price=20000.0),
        anchor_b=FibAnchor(time="2018-06-01T00:00:00+00:00", price=6000.0),
        fib_id=f"fib_BTC-USD_{timeframe}_20180101T000000",
    )


def test_htf_timeframes_for_chart_ladder():
    assert overlay.htf_timeframes_for_chart("1M") == []
    assert overlay.htf_timeframes_for_chart("1w") == ["1M"]
    assert overlay.htf_timeframes_for_chart("1d") == ["1M", "1w"]
    assert overlay.htf_timeframes_for_chart("4h") == ["1M", "1w", "1d"]
    assert overlay.htf_timeframes_for_chart("1h") == ["1M", "1w", "1d", "4h"]
    assert overlay.htf_timeframes_for_chart("15m") == []


def test_normalize_timeframe_aliases():
    assert overlay.normalize_timeframe("monthly") == "1M"
    assert overlay.normalize_timeframe("weekly") == "1w"


def test_list_saved_annotations_skips_events_json(tmp_path):
    set_labels_dir(tmp_path)
    ann = _sample_ann()
    save_annotation(ann)
    events = ann.fib_id + "_events.json"
    (overlay.human_fib_timeframe_dir("bitfinex", "BTC/USD", "1M") / events).write_text(
        json.dumps({"fib_id": ann.fib_id}),
        encoding="utf-8",
    )

    loaded = overlay.list_saved_annotations("bitfinex", "BTC/USD", "1M")

    assert len(loaded) == 1
    assert loaded[0].fib_id == ann.fib_id


def test_load_htf_overlays_collects_higher_timeframes(tmp_path):
    set_labels_dir(tmp_path)
    save_annotation(_sample_ann(timeframe="1M"))
    save_annotation(_sample_ann(timeframe="1w"))

    rows = overlay.load_htf_overlays("bitfinex", "BTC/USD", "1d")

    assert [htf for htf, _ in rows] == ["1M", "1w"]
    set_labels_dir(None)

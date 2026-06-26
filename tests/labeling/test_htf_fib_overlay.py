import json

import pandas as pd

from fibengine.labeling import htf_fib_overlay as overlay
from fibengine.labeling.human_fib import FibAnchor, make_annotation, save_annotation
from fibengine.labeling.store import set_labels_dir


def _daily_df(start: str, end: str) -> pd.DataFrame:
    idx = pd.date_range(start, end, freq="D", tz="UTC")
    return pd.DataFrame({"high": 1.0, "low": 1.0}, index=idx)


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


def test_htf_anchor_markers_high_and_low_in_window():
    ann = _sample_ann(timeframe="1M")  # H 2018-01-01 @ 20000, L 2018-06-01 @ 6000
    df = _daily_df("2018-01-01", "2018-06-30")

    markers = overlay.htf_anchor_markers(df, [("1M", ann)])

    by_label = {label: (idx, price, color) for idx, price, label, color in markers}
    assert set(by_label) == {"1M·H", "1M·L"}
    assert by_label["1M·H"][1] == 20000.0
    assert by_label["1M·L"][1] == 6000.0
    # anchor placed at the bar nearest its OWN timestamp (H = first bar 2018-01-01)
    assert by_label["1M·H"][0] == 0
    assert by_label["1M·H"][2] == overlay.HTF_OVERLAY_COLORS["1M"]


def test_htf_anchor_markers_skips_anchor_outside_window():
    ann = _sample_ann(timeframe="1M")
    df = _daily_df("2018-05-15", "2018-06-30")  # only the low anchor is in range

    labels = [label for _, _, label, _ in overlay.htf_anchor_markers(df, [("1M", ann)])]

    assert labels == ["1M·L"]


def test_htf_anchor_markers_empty_df_returns_nothing():
    ann = _sample_ann()
    empty = pd.DataFrame({"high": [], "low": []}, index=pd.DatetimeIndex([], tz="UTC"))

    assert overlay.htf_anchor_markers(empty, [("1M", ann)]) == []


def test_overlays_in_view_keeps_only_overlapping_spans():
    ann = _sample_ann(timeframe="1M")  # span 2018-01-01 .. 2018-06-01
    overlays = [("1M", ann)]
    t = pd.Timestamp

    # view overlapping the span -> kept
    assert overlay.overlays_in_view(overlays, t("2018-03-01", tz="UTC"), t("2018-04-01", tz="UTC"))
    # view entirely after the span -> dropped
    assert (
        overlay.overlays_in_view(overlays, t("2019-01-01", tz="UTC"), t("2019-06-01", tz="UTC"))
        == []
    )


def test_cycle_focus_id_wraps_through_none():
    ids = ["a", "b", "c"]
    assert overlay.cycle_focus_id(None, ids) == "a"
    assert overlay.cycle_focus_id("a", ids) == "b"
    assert overlay.cycle_focus_id("c", ids) is None  # past last -> no focus
    assert overlay.cycle_focus_id("x", ids) == "a"  # unknown current -> first
    assert overlay.cycle_focus_id(None, []) is None  # nothing to focus


def test_select_focused_filters_to_one_parent():
    a = _sample_ann(timeframe="1M")
    b = _sample_ann(timeframe="1w")
    overlays = [("1M", a), ("1w", b)]

    assert overlay.select_focused(overlays, None) == overlays
    assert overlay.select_focused(overlays, a.fib_id) == [("1M", a)]
    assert overlay.select_focused(overlays, "nonexistent") == []


def test_filter_to_session_shows_only_session_fibs_by_default():
    a = _sample_ann(timeframe="1M")
    b = _sample_ann(timeframe="1w")
    overlays = [("1M", a), ("1w", b)]
    session = {a.fib_id}

    assert overlay.filter_to_session(overlays, session, show_frozen=False) == [("1M", a)]
    assert overlay.filter_to_session(overlays, session, show_frozen=True) == overlays
    assert overlay.filter_to_session(overlays, set(), show_frozen=False) == []

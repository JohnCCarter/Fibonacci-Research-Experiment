import numpy as np
import pandas as pd

from fibengine.core.config import LevelEventConfig
from fibengine.core.models import Pivot, Swing
from fibengine.research.level_events import LevelInteractionStream, detect_level_events

RISE = [100 + i * 2 for i in range(11)]  # bars 0..10: 100 -> 120 (low@0, high@10)


def _df(closes: list[float]) -> pd.DataFrame:
    arr = np.array(closes, dtype=float)
    n = len(arr)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {"open": arr, "high": arr + 0.5, "low": arr - 0.5, "close": arr, "volume": np.ones(n)},
        index=idx,
    )


def _up_swing(df: pd.DataFrame) -> Swing:
    # low@0 -> high@10; med high=close+0.5, low=close-0.5 blir 0.5-nivån priset 110.0.
    return Swing(
        start=Pivot(0, df.index[0], float(df["low"].iloc[0]), "low", 3.0),
        end=Pivot(10, df.index[10], float(df["high"].iloc[10]), "high", 3.0),
    )


def _stream_for_half(closes: list[float]) -> LevelInteractionStream:
    df = _df(closes)
    swing = _up_swing(df)
    cfg = LevelEventConfig(levels=[0.5])
    streams = detect_level_events(df, swing, cfg, fib_ratios=[0.5])
    assert len(streams) == 1
    stream = streams[0]
    assert stream.level == "0.5"
    assert stream.price == 110.0
    return stream


def test_continuation_break_through_level():
    stream = _stream_for_half(RISE + [118, 116, 114, 112, 110, 108, 106])
    assert len(stream.events) == 1
    event = stream.events[0]
    assert event.auto_candidate == "continuation_candidate"
    assert event.approach_side == "above"
    assert event.touch_type == "wick_below"
    # ISO-tidsstämpel som går att parsa tillbaka.
    assert pd.Timestamp(event.event_bar).tzinfo is not None


def test_rejection_touch_and_bounce_away():
    stream = _stream_for_half(RISE + [114, 112, 110.6, 113, 116, 118])
    assert len(stream.events) == 1
    event = stream.events[0]
    assert event.auto_candidate == "rejection_candidate"
    assert event.approach_side == "above"


def test_failure_accepted_below_then_reverses():
    stream = _stream_for_half(RISE + [114, 112, 110, 109, 108, 111, 113])
    assert len(stream.events) == 1
    assert stream.events[0].auto_candidate == "failure_candidate"


def test_debounce_collapses_consecutive_touches_to_one_event():
    stream = _stream_for_half(RISE + [110, 110, 110, 110, 114, 116])
    assert len(stream.events) == 1


def test_no_events_when_level_never_touched():
    stream = _stream_for_half(RISE + [119, 119, 118, 119, 120, 119])
    assert stream.events == []


def test_to_dict_shape_matches_issue_schema():
    stream = _stream_for_half(RISE + [118, 116, 114, 112, 110, 108, 106])
    d = stream.to_dict()
    assert set(d) == {"level", "price", "events"}
    event = d["events"][0]
    assert set(event) == {
        "event_bar",
        "bar_index",
        "touch_type",
        "approach_side",
        "auto_candidate",
        "note",
        "evidence",
    }
    assert set(event["evidence"]) == {
        "forward_bars",
        "closes_beyond",
        "closes_back",
        "max_penetration_atr",
    }

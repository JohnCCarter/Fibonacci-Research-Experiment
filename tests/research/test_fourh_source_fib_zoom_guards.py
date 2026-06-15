"""Tests for fourh_source_fib_zoom — fail-closed guards and strict separation.

Guard failures all occur before load_candles is called, so no monkeypatching needed.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

import fibengine.research.fourh_source_fib_zoom as mod
from fibengine.research.fourh_source_fib_zoom import (
    SCOPE_2017_H2,
    SCOPE_2021_DEC2020_MAR2021,
    SOURCE_TF,
    render_fourh_source_fib_zoom,
)


def _write_fib(
    fib_dir: Path,
    *,
    sid: str = "20170801T040000",
    a_time: str = "2017-08-01T04:00:00Z",
    a_price: float = 2700.0,
    b_time: str = "2017-08-15T04:00:00Z",
    b_price: float = 4400.0,
    timeframe: str = "4h",
    profile: str = "tradingview_log_chamoun",
    scale: str = "log",
    created_by: str = "human",
    source: str = "manual_labeling_tool",
    ratios: tuple[float, ...] = (0.0, 0.382, 0.5, 0.618, 0.786, 1.0),
    fib_id: str | None = None,
) -> Path:
    fib_dir.mkdir(parents=True, exist_ok=True)
    lo, hi = min(a_price, b_price), max(a_price, b_price)
    fid = fib_id or f"fib_BTC-USD_{timeframe}_{sid}"
    payload = {
        "fib_id": fid,
        "symbol": "BTC/USD",
        "timeframe": timeframe,
        "exchange": "bitfinex",
        "created_by": created_by,
        "source": source,
        "scale_mode": scale,
        "levels_profile": profile,
        "anchor_a": {"time": a_time, "price": a_price},
        "anchor_b": {"time": b_time, "price": b_price},
        "direction": "up" if b_price > a_price else "down",
        "levels": [{"ratio": r, "price": lo + r * (hi - lo)} for r in ratios],
    }
    path = fib_dir / f"fib_BTC-USD_{timeframe}_{sid}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_empty_fib_dir_fails(tmp_path):
    fib_dir = tmp_path / "empty"
    fib_dir.mkdir()
    with pytest.raises(FileNotFoundError, match="fib_.*json"):
        render_fourh_source_fib_zoom(
            fib_dir=fib_dir, scope=SCOPE_2017_H2, out_root=tmp_path / "zoom"
        )


def test_empty_scope_fails(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(
        fib_dir,
        sid="20170301T040000",
        a_time="2017-03-01T04:00:00Z",
        a_price=1100.0,
        b_time="2017-03-20T04:00:00Z",
        b_price=1800.0,
    )
    with pytest.raises(ValueError, match="selected 0 fibs"):
        render_fourh_source_fib_zoom(
            fib_dir=fib_dir, scope=SCOPE_2017_H2, out_root=tmp_path / "zoom"
        )


def test_unknown_scope_fails(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir)
    with pytest.raises(ValueError, match="Unknown scope"):
        render_fourh_source_fib_zoom(
            fib_dir=fib_dir, scope="1M_scope_that_doesnt_exist", out_root=tmp_path / "zoom"
        )


def test_fib_id_not_in_scope_fails(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(
        fib_dir,
        sid="20210105T040000",
        a_time="2021-01-05T04:00:00Z",
        a_price=29000.0,
        b_time="2021-01-08T08:00:00Z",
        b_price=41500.0,
    )
    with pytest.raises(ValueError, match="not found in scope"):
        render_fourh_source_fib_zoom(
            fib_dir=fib_dir,
            scope=SCOPE_2021_DEC2020_MAR2021,
            out_root=tmp_path / "zoom",
            fib_id="fib_BTC-USD_4h_20210415T040000",
        )


@pytest.mark.parametrize(
    ("over", "match"),
    [
        ({"timeframe": "1d"}, "timeframe"),
        ({"profile": "some_linear_profile"}, "levels_profile"),
        ({"scale": "linear"}, "scale_mode"),
        ({"ratios": (0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0)}, "0.236"),
        ({"created_by": "machine", "source": "auto_fib_detector"}, "non-manual origin"),
        ({"fib_id": "fib_BTC-USD_4h_candidate_20170801"}, "candidate"),
    ],
)
def test_fail_closed_guard_rejects(tmp_path, over, match):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, **over)
    with pytest.raises(ValueError, match=match):
        render_fourh_source_fib_zoom(
            fib_dir=fib_dir, scope=SCOPE_2017_H2, out_root=tmp_path / "zoom"
        )


def test_source_tf_is_4h():
    assert SOURCE_TF == "4h"


def test_no_reaction_review_imports_and_no_1h():
    source = inspect.getsource(mod)
    assert "from fibengine.research.source_fib_projection" not in source
    assert "import source_fib_projection" not in source
    assert "import review_sample" not in source
    assert 'SOURCE_TF = "1h"' not in source

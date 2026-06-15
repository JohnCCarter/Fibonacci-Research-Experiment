"""Tests for fourh_source_fib_zoom — scope selection and rendering paths."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import fibengine.research.fourh_source_fib_zoom as mod
from fibengine.research.fourh_source_fib_zoom import (
    SCOPE_2017_H2,
    SCOPE_2021_DEC2020_MAR2021,
    _select_scope,
    render_fourh_source_fib_zoom,
)


def _df() -> pd.DataFrame:
    idx = pd.date_range("2016-12-01", periods=12_000, freq="4h", tz="UTC")
    base = np.linspace(700, 70_000, len(idx))
    return pd.DataFrame(
        {
            "open": base * 0.98,
            "high": base * 1.05,
            "low": base * 0.95,
            "close": base,
            "volume": np.ones(len(idx)),
        },
        index=idx,
    )


def _fake_load_candles(cfg, **_kw) -> pd.DataFrame:
    return _df()


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


def test_2017_h2_renders_h2_only_and_path_structure(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, sid="20170801T040000", a_time="2017-08-01T04:00:00Z")
    _write_fib(
        fib_dir,
        sid="20170301T040000",
        a_time="2017-03-01T04:00:00Z",
        a_price=1100.0,
        b_time="2017-03-20T04:00:00Z",
        b_price=1800.0,
    )
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    result = render_fourh_source_fib_zoom(
        fib_dir=fib_dir, scope=SCOPE_2017_H2, out_root=tmp_path / "zoom"
    )

    assert result.scope == SCOPE_2017_H2 and result.fib_count == 1 and result.rendered == 1
    art = result.artifacts[0]
    assert art.fib_id == "fib_BTC-USD_4h_20170801T040000" and not art.skipped
    assert art.clean is not None and art.levels is not None
    assert art.clean.parent.name == art.fib_id and art.clean.parent.parent.name == SCOPE_2017_H2
    assert art.clean.name == "4h_clean.png" and art.levels.name == "4h_levels.png"
    assert art.clean.exists() and art.clean.stat().st_size > 1000
    assert art.levels.exists() and art.levels.stat().st_size > 1000


def test_2021_scope_selects_jan_mar_excludes_dec_and_apr(tmp_path):
    fib_dir = tmp_path / "fibs"
    _write_fib(
        fib_dir,
        sid="20210105T040000",
        a_time="2021-01-05T04:00:00Z",
        a_price=29000.0,
        b_time="2021-01-08T08:00:00Z",
        b_price=41500.0,
    )
    _write_fib(
        fib_dir,
        sid="20210415T040000",
        a_time="2021-04-15T04:00:00Z",
        a_price=55000.0,
        b_time="2021-04-25T04:00:00Z",
        b_price=46000.0,
    )
    _write_fib(
        fib_dir,
        sid="20201225T120000",
        a_time="2020-12-25T12:00:00Z",
        a_price=23000.0,
        b_time="2020-12-27T08:00:00Z",
        b_price=28000.0,
    )

    from fibengine.research.monthly_fib_map import _load_fibs

    ids = {a.fib_id for a in _select_scope(_load_fibs(fib_dir), SCOPE_2021_DEC2020_MAR2021)}

    assert "fib_BTC-USD_4h_20210105T040000" in ids
    assert "fib_BTC-USD_4h_20210415T040000" not in ids
    assert "fib_BTC-USD_4h_20201225T120000" not in ids


def test_2021_scope_renders_and_path_structure(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _write_fib(
        fib_dir,
        sid="20210105T040000",
        a_time="2021-01-05T04:00:00Z",
        a_price=29000.0,
        b_time="2021-01-08T08:00:00Z",
        b_price=41500.0,
    )
    _write_fib(
        fib_dir,
        sid="20210415T040000",
        a_time="2021-04-15T04:00:00Z",
        a_price=55000.0,
        b_time="2021-04-25T04:00:00Z",
        b_price=46000.0,
    )
    _write_fib(
        fib_dir,
        sid="20201225T120000",
        a_time="2020-12-25T12:00:00Z",
        a_price=23000.0,
        b_time="2020-12-27T08:00:00Z",
        b_price=28000.0,
    )
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    result = render_fourh_source_fib_zoom(
        fib_dir=fib_dir, scope=SCOPE_2021_DEC2020_MAR2021, out_root=tmp_path / "zoom"
    )
    assert result.fib_count == 1
    assert result.artifacts[0].clean is not None
    assert result.artifacts[0].clean.parent.parent.name == SCOPE_2021_DEC2020_MAR2021


def test_fib_id_renders_only_that_fib(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _write_fib(
        fib_dir,
        sid="20210105T040000",
        a_time="2021-01-05T04:00:00Z",
        a_price=29000.0,
        b_time="2021-01-08T08:00:00Z",
        b_price=41500.0,
    )
    _write_fib(
        fib_dir,
        sid="20210110T080000",
        a_time="2021-01-10T08:00:00Z",
        a_price=35000.0,
        b_time="2021-01-12T00:00:00Z",
        b_price=40000.0,
    )
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    result = render_fourh_source_fib_zoom(
        fib_dir=fib_dir,
        scope=SCOPE_2021_DEC2020_MAR2021,
        out_root=tmp_path / "zoom",
        fib_id="fib_BTC-USD_4h_20210105T040000",
    )
    assert result.fib_count == 1 and result.artifacts[0].fib_id == "fib_BTC-USD_4h_20210105T040000"


def test_out_of_range_anchor_surfaced(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir, sid="20170801T040000", a_time="2017-08-01T04:00:00Z")
    _write_fib(
        fib_dir,
        sid="20170901T040000",
        a_time="2017-09-01T04:00:00Z",
        a_price=2000.0,
        b_time="2099-09-10T04:00:00Z",
        b_price=5000.0,
    )
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)

    result = render_fourh_source_fib_zoom(
        fib_dir=fib_dir, scope=SCOPE_2017_H2, out_root=tmp_path / "zoom"
    )
    skipped = [a for a in result.artifacts if a.skipped]
    assert len(skipped) == 1 and skipped[0].skip_reason is not None
    assert result.rendered == 1


def test_no_review_sample_csv_produced(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _write_fib(fib_dir)
    monkeypatch.setattr(mod, "load_candles", _fake_load_candles)
    render_fourh_source_fib_zoom(fib_dir=fib_dir, scope=SCOPE_2017_H2, out_root=tmp_path / "zoom")
    assert not list(tmp_path.rglob("review_sample.csv"))

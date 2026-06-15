"""Structural chart-contract + metadata-snapshot tests (stdlib, no PNG baselines).

Renders synthetic flows, builds stable summaries, and compares them to committed golden
JSON under tests/research/snapshots/. Deterministic (synthetic candles + fibs); no binary
baselines, no pixel diffing. Regenerate goldens with: UPDATE_SNAPSHOTS=1 pytest -k summary
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

import fibengine.research.fourh_source_fib_map as map_mod
import fibengine.research.fourh_source_fib_zoom as zoom_mod
from fibengine.research.render_summary import (
    gallery_summary,
    map_summary,
    zoom_summary,
)

SNAP_DIR = Path(__file__).parent / "snapshots"


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
    fib_dir: Path, *, sid: str, a_time: str, a_price: float, b_time: str, b_price: float
):
    fib_dir.mkdir(parents=True, exist_ok=True)
    lo, hi = min(a_price, b_price), max(a_price, b_price)
    fid = f"fib_BTC-USD_4h_{sid}"
    ratios = (0.0, 0.382, 0.5, 0.618, 0.786, 1.0)
    payload = {
        "fib_id": fid,
        "symbol": "BTC/USD",
        "timeframe": "4h",
        "exchange": "bitfinex",
        "created_by": "human",
        "source": "manual_labeling_tool",
        "scale_mode": "log",
        "levels_profile": "tradingview_log_chamoun",
        "anchor_a": {"time": a_time, "price": a_price},
        "anchor_b": {"time": b_time, "price": b_price},
        "direction": "up" if b_price > a_price else "down",
        "levels": [{"ratio": r, "price": lo + r * (hi - lo)} for r in ratios],
    }
    (fib_dir / f"{fid}.json").write_text(json.dumps(payload), encoding="utf-8")


def _check_snapshot(name: str, data: dict) -> None:
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAP_DIR / name
    if os.environ.get("UPDATE_SNAPSHOTS"):
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    assert path.exists(), f"missing golden snapshot {path} (run UPDATE_SNAPSHOTS=1)"
    assert json.loads(path.read_text(encoding="utf-8")) == data


def _png(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"\x89PNG\r\n\x1a\n")


# --- map flow -------------------------------------------------------------------------


def test_map_summary_contract_and_snapshot(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _write_fib(
        fib_dir,
        sid="20170801T040000",
        a_time="2017-08-01T04:00:00Z",
        a_price=2700.0,
        b_time="2017-08-15T04:00:00Z",
        b_price=4400.0,
    )
    _write_fib(
        fib_dir,
        sid="20170901T040000",
        a_time="2017-09-01T04:00:00Z",
        a_price=3000.0,
        b_time="2017-09-20T04:00:00Z",
        b_price=5000.0,
    )
    monkeypatch.setattr(map_mod, "load_candles", _fake_load_candles)

    result = map_mod.render_fourh_source_fib_map(fib_dir=fib_dir, out_root=tmp_path / "out")
    summary = map_summary(result, tmp_path / "out")

    assert summary["flow"] == "fourh_source_fib_map"
    assert summary["fib_count"] == 2
    g = summary["groups"][0]
    assert g["clean"].endswith("_4h_clean.png") and g["levels"].endswith("_4h_levels.png")
    assert "/" not in g["clean"] or not g["clean"].startswith("/")  # relative
    assert str(tmp_path) not in json.dumps(summary)  # no absolute paths
    _check_snapshot("map_summary.json", summary)


# --- zoom flow ------------------------------------------------------------------------


def test_zoom_summary_contract_and_snapshot(tmp_path, monkeypatch):
    fib_dir = tmp_path / "fibs"
    _write_fib(
        fib_dir,
        sid="20210105T040000",
        a_time="2021-01-05T04:00:00Z",
        a_price=29000.0,
        b_time="2021-01-08T08:00:00Z",
        b_price=41500.0,
    )
    monkeypatch.setattr(zoom_mod, "load_candles", _fake_load_candles)

    result = zoom_mod.render_fourh_source_fib_zoom(
        fib_dir=fib_dir, scope=zoom_mod.SCOPE_2021_DEC2020_MAR2021, out_root=tmp_path / "out"
    )
    summary = zoom_summary(result, tmp_path / "out")

    assert summary["flow"] == "fourh_source_fib_zoom"
    assert summary["scope"] == "2021_dec2020_mar2021"
    assert summary["rendered"] == 1 and summary["fib_count"] == 1
    art = summary["artifacts"][0]
    assert art["clean"].endswith("4h_clean.png") and art["levels"].endswith("4h_levels.png")
    assert art["clean"].startswith("2021_dec2020_mar2021/")  # scope/fib_id/ pairing, fwd slash
    assert str(tmp_path) not in json.dumps(summary)
    _check_snapshot("zoom_summary.json", summary)


# --- gallery flow ---------------------------------------------------------------------


def test_gallery_summary_contract_and_snapshot(tmp_path):
    root = tmp_path / "fourh_source_fib_zoom"
    fib = "fib_BTC-USD_4h_20171228T200000"
    _png(root / "2017_h2" / fib / "4h_clean.png")
    _png(root / "2017_h2" / fib / "4h_levels.png")

    summary = gallery_summary(root)

    assert summary["flow"] == "artifact_gallery"
    grp = summary["groups"][0]
    assert grp["label"] == "2017_h2"
    item = grp["items"][0]
    assert item["kinds"] == ["clean", "levels"]  # pairing present
    assert item["images"]["clean"] == f"2017_h2/{fib}/4h_clean.png"  # relative fwd-slash
    assert str(tmp_path) not in json.dumps(summary)
    _check_snapshot("gallery_summary.json", summary)


# --- guards ---------------------------------------------------------------------------


def test_snapshots_are_text_json_only():
    # The regression layer must never introduce binary baselines.
    for p in SNAP_DIR.glob("*"):
        assert p.suffix == ".json", f"non-JSON snapshot {p}"
        json.loads(p.read_text(encoding="utf-8"))  # parses as text JSON

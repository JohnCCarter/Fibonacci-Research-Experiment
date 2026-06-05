"""Tester fÃ¶r human-review-paketet (research-only, syntetisk data, ingen nÃ¤tverk)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from fibengine.core.config import Settings
from fibengine.core.models import Pivot, Swing
from fibengine.research import human_review_level_events as hr
from fibengine.research.human_review_level_events import (
    REVIEW_COLUMNS,
    HumanReviewConfig,
    collect_candidates,
    make_review_id,
    render_chart,
    run_human_review,
    sample_candidates,
)
from fibengine.research.level_events import LevelEventConfig


def _df(closes: list[float]) -> pd.DataFrame:
    arr = np.array(closes, dtype=float)
    n = len(arr)
    idx = pd.date_range("2024-01-01", periods=n, freq="1h", tz="UTC")
    return pd.DataFrame(
        {"open": arr, "high": arr + 0.5, "low": arr - 0.5, "close": arr, "volume": np.ones(n)},
        index=idx,
    )


def _trend_df() -> pd.DataFrame:
    # Tydlig trend med pullbacks sÃ¥ detektorn ger flera nivÃ¥-events.
    grid = np.arange(0, 160)
    closes = np.interp(grid, [0, 40, 70, 110, 159], [100, 150, 120, 165, 130])
    return _df(list(closes))


def _up_swing(df: pd.DataFrame, start: int = 0, end: int = 40) -> Swing:
    return Swing(
        start=Pivot(start, df.index[start], float(df["low"].iloc[start]), "low", 3.0),
        end=Pivot(end, df.index[end], float(df["high"].iloc[end]), "high", 3.0),
        status="confirmed",
    )


def _settings() -> Settings:
    s = Settings()
    s.data.symbol = "BTC/USD"
    s.data.timeframe = "1h"
    s.data.exchange = "Bitfinex"
    return s


def _candidates(df: pd.DataFrame, settings: Settings) -> list[dict]:
    """Bygg rader direkt frÃ¥n en kÃ¤nd swing (utan walk-forward/select_swing)."""
    level_cfg = LevelEventConfig()
    ratios = settings.fib.levels
    meta = {
        "symbol": settings.data.symbol,
        "timeframe": settings.data.timeframe,
        "exchange": settings.data.exchange,
    }
    swing = _up_swing(df)
    rows = []
    streams = hr.detect_level_events(df, swing, level_cfg, ratios, settings.pivots.atr_period)
    for stream in streams:
        for ev in stream.events:
            rows.append(hr._row_for_event(df, swing, meta, stream.level, stream.price, ev))
    return rows


def test_review_row_schema_has_required_fields_and_placeholders():
    df = _trend_df()
    rows = _candidates(df, _settings())
    assert rows, "fÃ¶rvÃ¤ntade minst en kandidat"
    for r in rows:
        assert set(r.keys()) == set(REVIEW_COLUMNS)
        # Tomma platshÃ¥llare som mÃ¤nniskan fyller i.
        assert r["human_label"] == ""
        assert r["human_confidence"] == ""
        assert r["human_note"] == ""
        # Obligatoriska detektorfÃ¤lt + swing-kontext finns.
        for key in (
            "fib_source",
            "fib_level",
            "fib_price",
            "fib_levels",
            "event_bar",
            "event_time",
            "relation",
            "auto_candidate",
            "touch_type",
            "approach_side",
            "swing_start_time",
            "swing_end_time",
            "swing_direction",
            "anchor_a_time",
            "anchor_a_price",
            "anchor_a_bar",
            "anchor_b_time",
            "anchor_b_price",
            "anchor_b_bar",
            "chart_path",
        ):
            assert r[key] not in (None, "")
        assert r["relation"] in {"above", "below", "touch", "cross"}
        assert r["anchor_a_bar"] == r["swing_start_bar"]
        assert r["anchor_b_bar"] == r["swing_end_bar"]


def test_chart_path_tied_to_review_id_and_filesystem_safe():
    rid = make_review_id("BTC/USD", "1h", "0.5", 12, 40, 73, "continuation_candidate")
    assert "/" not in rid and "." not in rid
    assert rid == "BTC-USD_1h_L0p5_s12_e40_b73_cont"


def test_review_id_distinguishes_legs_sharing_end_pivot():
    # Walk-forward kan lÃ¥sa tvÃ¥ legs med samma end men olika start; id:n fÃ¥r ej kollidera.
    a = make_review_id("BTC/USD", "1h", "0.5", 12, 40, 73, "continuation_candidate")
    b = make_review_id("BTC/USD", "1h", "0.5", 20, 40, 73, "continuation_candidate")
    assert a != b


def test_deterministic_sampling_with_seed():
    df = _trend_df()
    rows = _candidates(df, _settings())
    cfg = HumanReviewConfig(max_events=5, seed=7)
    a = [r["review_id"] for r in sample_candidates(rows, cfg)]
    b = [r["review_id"] for r in sample_candidates(rows, cfg)]
    assert a == b
    assert len(a) <= 5


def test_sampling_respects_caps():
    df = _trend_df()
    rows = _candidates(df, _settings())
    cfg = HumanReviewConfig(max_events=100, max_per_candidate=1, max_per_level=1, seed=1)
    sampled = sample_candidates(rows, cfg)
    from collections import Counter

    by_type = Counter(r["auto_candidate"] for r in sampled)
    by_level = Counter(r["fib_level"] for r in sampled)
    assert all(v <= 1 for v in by_type.values())
    assert all(v <= 1 for v in by_level.values())
    assert len(sampled) <= 100


def test_sampling_filters_by_candidate_type_and_level():
    df = _trend_df()
    rows = _candidates(df, _settings())
    present_type = rows[0]["auto_candidate"]
    cfg = HumanReviewConfig(max_events=100, candidate_types=[present_type], seed=2)
    sampled = sample_candidates(rows, cfg)
    assert sampled
    assert all(r["auto_candidate"] == present_type for r in sampled)


def test_render_chart_writes_nonempty_png(tmp_path):
    df = _trend_df()
    rows = _candidates(df, _settings())
    cfg = HumanReviewConfig()
    out = tmp_path / "charts" / f"{rows[0]['review_id']}.png"
    render_chart(df, rows[0], out, cfg)
    assert out.exists()
    assert out.stat().st_size > 0


def test_collect_candidates_single_mode_uses_selected_swing(monkeypatch):
    df = _trend_df()
    settings = _settings()
    swing = _up_swing(df)
    monkeypatch.setattr(hr, "select_swing", lambda _df, _p, _s: swing)
    rows = collect_candidates(df, settings, mode="single")
    assert rows
    assert all(r["swing_end_bar"] == 40 for r in rows)
    assert all(r["event_bar"] > 40 for r in rows)


def test_end_to_end_package_files_created(monkeypatch, tmp_path):
    df = _trend_df()
    settings = _settings()
    swing = _up_swing(df)
    monkeypatch.setattr(hr, "load_candles", lambda _cfg: df)
    monkeypatch.setattr(hr, "select_swing", lambda _df, _p, _s: swing)
    monkeypatch.setattr(hr, "REVIEW_ROOT", tmp_path / "review")

    result = run_human_review(
        settings=settings, cfg=HumanReviewConfig(max_events=6, seed=3), mode="single"
    )
    run_dir = tmp_path / "review" / result["run_id"]
    assert (run_dir / "review_sample.csv").exists()
    assert (run_dir / "review_sample.jsonl").exists()
    assert (run_dir / "REVIEW_INDEX.md").exists()
    pngs = list((run_dir / "charts").glob("*.png"))
    assert pngs, "fÃ¶rvÃ¤ntade minst en chart-PNG"
    assert len(pngs) == result["total_sampled"]
    assert result["total_sampled"] <= 6


def test_csv_and_jsonl_rows_agree(monkeypatch, tmp_path):
    import csv
    import json

    df = _trend_df()
    settings = _settings()
    swing = _up_swing(df)
    monkeypatch.setattr(hr, "load_candles", lambda _cfg: df)
    monkeypatch.setattr(hr, "select_swing", lambda _df, _p, _s: swing)
    monkeypatch.setattr(hr, "REVIEW_ROOT", tmp_path / "review")

    result = run_human_review(
        settings=settings, cfg=HumanReviewConfig(max_events=6, seed=3), mode="single"
    )
    run_dir = tmp_path / "review" / result["run_id"]
    with (run_dir / "review_sample.csv").open() as f:
        csv_rows = list(csv.DictReader(f))
    jsonl_rows = [
        json.loads(line) for line in (run_dir / "review_sample.jsonl").read_text().splitlines()
    ]
    assert len(csv_rows) == len(jsonl_rows) == result["total_sampled"]
    assert [r["review_id"] for r in csv_rows] == [r["review_id"] for r in jsonl_rows]
    # En PNG per rad.
    for r in jsonl_rows:
        assert (run_dir / r["chart_path"]).exists()

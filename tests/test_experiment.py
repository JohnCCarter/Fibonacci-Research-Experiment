"""End-to-end-test fÃ¶r run_experiment med mockad data + labels (ingen nÃ¤tverk)."""

import json

import numpy as np
import pandas as pd

from fibengine import experiment as exp_mod
from fibengine.core.config import Settings
from fibengine.labeling.store import Point, SwingLabel


def _df() -> pd.DataFrame:
    closes = np.interp(np.arange(0, 61), [0, 20, 40, 60], [100, 120, 105, 130])
    idx = pd.date_range("2024-01-01", periods=len(closes), freq="1h", tz="UTC")
    return pd.DataFrame(
        {
            "open": closes,
            "high": closes + 0.5,
            "low": closes - 0.5,
            "close": closes,
            "volume": np.ones(len(closes)),
        },
        index=idx,
    )


def _settings() -> Settings:
    s = Settings()
    s.pivots.min_prominence_atr = 0.3
    s.scoring.weights = {
        "magnitude": 1.0,
        "recency": 0.8,
        "prominence": 0.6,
        "cleanliness": 0.5,
        "round_number": 0.2,
        "duration": -0.3,
        "structure_alignment": 0.9,
        "scale_confluence": 0.7,
    }
    return s


def test_run_experiment_writes_audit_and_aggregate(tmp_path, monkeypatch):
    df = _df()
    in_window = SwingLabel(
        exchange="Bitfinex",
        symbol="BTC/USD",
        timeframe="1h",
        high=Point(df.index[60].isoformat(), 130.0),
        low=Point(df.index[40].isoformat(), 105.0),
    )
    monkeypatch.setattr(exp_mod, "load_candles", lambda cfg, **k: df)
    monkeypatch.setattr(
        exp_mod, "list_labels", lambda source=None: [in_window] if source != "machine" else []
    )
    monkeypatch.setattr(exp_mod, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(exp_mod, "LEADERBOARD", tmp_path / "leaderboard.jsonl")

    run_dir = exp_mod.run_experiment(_settings())
    metrics = json.loads((run_dir / "metrics.json").read_text())
    assert metrics["aggregate"]["n"] == 1
    assert metrics["aggregate"]["excluded_out_of_window"] == 0
    assert (run_dir / "config.json").exists()
    assert (tmp_path / "leaderboard.jsonl").exists()


def test_run_experiment_excludes_out_of_window_label(tmp_path, monkeypatch):
    df = _df()
    future = (df.index[-1] + pd.Timedelta(days=365)).isoformat()
    out_label = SwingLabel(
        exchange="Bitfinex",
        symbol="BTC/USD",
        timeframe="1h",
        high=Point(future, 130.0),
        low=Point(future, 105.0),
    )
    monkeypatch.setattr(exp_mod, "load_candles", lambda cfg, **k: df)
    monkeypatch.setattr(
        exp_mod, "list_labels", lambda source=None: [out_label] if source != "machine" else []
    )
    monkeypatch.setattr(exp_mod, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(exp_mod, "LEADERBOARD", tmp_path / "leaderboard.jsonl")

    run_dir = exp_mod.run_experiment(_settings())
    metrics = json.loads((run_dir / "metrics.json").read_text())
    # Enda labeln Ã¤r out-of-window â†’ exkluderad ur aggregatet.
    assert metrics["aggregate"]["excluded_out_of_window"] == 1
    assert metrics["aggregate"]["n"] == 0
    assert metrics["aggregate"]["no_in_window_samples"] is True

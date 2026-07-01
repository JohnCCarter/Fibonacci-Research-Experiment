"""The ML/Optuna ranker must stay fail-closed until deps + human data + a locked holdout (Issue #42)."""

from __future__ import annotations

import pytest

from fibengine.research import selection_ranker_ml as ml
from fibengine.research.selection_annotation import Anchor, AnnotationWindow, Candidate


def _human_window(cid: str) -> AnnotationWindow:
    return AnnotationWindow(
        symbol="BTC/USD",
        timeframe="1d",
        exchange="bitfinex",
        window_start="2020-02-01",
        window_end="2020-04-30",
        regime_label="r",
        structure_label="s",
        created_by="human",
        candidates=(
            Candidate(
                cid,
                Anchor("2020-03-30T00:00:00+00:00", 5880.9),
                Anchor("2020-04-08T00:00:00+00:00", 7420.0),
                "up",
                "accepted",
            ),
        ),
    )


def test_gate_blocks_when_deps_missing(monkeypatch):
    monkeypatch.setattr(ml, "ml_available", lambda: False)
    with pytest.raises(ml.SelectionLearnerGated, match="install the optional extra"):
        ml.check_gate([_human_window("c1")], locked_holdout=object())


def test_gate_blocks_when_too_few_human_windows(monkeypatch):
    monkeypatch.setattr(ml, "ml_available", lambda: True)
    with pytest.raises(ml.SelectionLearnerGated, match="human annotation windows"):
        ml.check_gate([_human_window("c1")], locked_holdout=object())


def test_gate_blocks_without_locked_holdout(monkeypatch):
    monkeypatch.setattr(ml, "ml_available", lambda: True)
    windows = [_human_window(f"c{i}") for i in range(ml.MIN_HUMAN_WINDOWS)]
    with pytest.raises(ml.SelectionLearnerGated, match="locked holdout"):
        ml.check_gate(windows, locked_holdout=None)


def test_fit_and_tune_deferred_after_gate(monkeypatch):
    monkeypatch.setattr(ml, "ml_available", lambda: True)
    windows = [_human_window(f"c{i}") for i in range(ml.MIN_HUMAN_WINDOWS)]
    with pytest.raises(NotImplementedError, match="deferred"):
        ml.fit_ranker(windows, locked_holdout=object())
    with pytest.raises(NotImplementedError, match="[Oo]ptuna"):
        ml.tune_with_optuna(windows, locked_holdout=object())


def test_fixtures_do_not_count_as_human(monkeypatch):
    monkeypatch.setattr(ml, "ml_available", lambda: True)
    fixture = AnnotationWindow(
        symbol="BTC/USD",
        timeframe="1d",
        exchange="bitfinex",
        window_start="2020-02-01",
        window_end="2020-04-30",
        regime_label="r",
        structure_label="s",
        created_by="fixture",
        candidates=(
            Candidate(
                "c1",
                Anchor("2020-03-30T00:00:00+00:00", 5880.9),
                Anchor("2020-04-08T00:00:00+00:00", 7420.0),
                "up",
                "accepted",
            ),
        ),
    )
    with pytest.raises(ml.SelectionLearnerGated, match="human annotation windows"):
        ml.check_gate([fixture] * 50, locked_holdout=object())

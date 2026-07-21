"""Overwrite guard for facit saves (the 1w 20170316 base fib was lost to a collision)."""

from __future__ import annotations

import pytest

from fibengine.labeling import human_fib, store
from fibengine.labeling.human_fib import (
    FibAnchor,
    load_annotation,
    make_annotation,
    save_annotation,
)


@pytest.fixture
def labels_tmp(tmp_path):
    store.set_labels_dir(tmp_path)
    yield tmp_path
    store.set_labels_dir(None)


# Overwrite guard: the fib filename is the origin timestamp only, so two different legs
# sharing an origin candle collide — a silent save destroys committed facit (1w 20170316
# was lost this way on 2026-06-26).


def test_save_refuses_overwrite_with_different_anchors(labels_tmp):
    a = FibAnchor("2026-01-14T00:00:00Z", 97924.0)
    b1 = FibAnchor("2026-02-06T00:00:00Z", 60000.0)
    b2 = FibAnchor("2026-03-06T00:00:00Z", 120000.0)  # same origin, different endpoint
    first = make_annotation(symbol="BTC/USD", timeframe="1d", anchor_a=a, anchor_b=b1)
    save_annotation(first)
    second = make_annotation(symbol="BTC/USD", timeframe="1d", anchor_a=a, anchor_b=b2)
    with pytest.raises(human_fib.AnnotationOverwriteError, match="different anchors"):
        save_annotation(second)
    # the original facit is untouched
    assert load_annotation(human_fib.annotation_path(first)).anchor_b.price == pytest.approx(
        60000.0
    )


def test_save_allows_idempotent_resave_and_explicit_overwrite(labels_tmp):
    a = FibAnchor("2026-01-14T00:00:00Z", 97924.0)
    b1 = FibAnchor("2026-02-06T00:00:00Z", 60000.0)
    b2 = FibAnchor("2026-03-06T00:00:00Z", 120000.0)
    first = make_annotation(symbol="BTC/USD", timeframe="1d", anchor_a=a, anchor_b=b1)
    save_annotation(first)
    # identical anchors -> harmless idempotent re-save, no error
    save_annotation(make_annotation(symbol="BTC/USD", timeframe="1d", anchor_a=a, anchor_b=b1))
    # explicit overwrite is a deliberate decision and goes through
    second = make_annotation(symbol="BTC/USD", timeframe="1d", anchor_a=a, anchor_b=b2)
    path = save_annotation(second, allow_overwrite=True)
    assert load_annotation(path).anchor_b.price == pytest.approx(120000.0)

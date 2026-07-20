"""Living transcription-accuracy regression (audit 2026-07-20, FIB-AUDIT-002 / P2:12).

The docstring claim in ``fib_transcribe`` used to be a fossil (95.8% on an N that drifted
71/67/76 across sources). This test recomputes both-anchor time recovery over the FULL
current daily facit corpus — N is read from the committed corpus manifest, so the number can
never silently describe a stale corpus again. Skips (loudly) when the candle cache is absent
(cloud containers without Bitfinex egress); on labeled machines it runs in the normal gate.
"""

from __future__ import annotations

import glob
import json
from pathlib import Path

import pytest

from fibengine.core.config import load_settings
from fibengine.data.fetch import cache_path
from fibengine.labeling.fib_transcribe import transcribe_fib
from fibengine.research.corpus_manifest import MANIFEST_PATH, REPO_ROOT

FIB_DIR = REPO_ROOT / "data" / "labels" / "human_fib" / "bitfinex" / "BTC-USD" / "1d"
CONFIG = REPO_ROOT / "config" / "settings.expansion.yaml"
# Regression floor, deliberately below the historical ~0.96 point estimate: fail only on a
# real capability break, not on a few new hard fibs entering the corpus.
FLOOR = 0.90


def _daily_cfg():
    settings = load_settings(str(CONFIG))
    return settings.data.model_copy(
        update={"exchange": "bitfinex", "symbol": "BTC/USD", "timeframe": "1d"}
    )


def test_transcribe_time_recovery_regression() -> None:
    cfg = _daily_cfg()
    if not cache_path(cfg).exists():
        pytest.skip("daily candle cache missing - run data.fetch first (needs Bitfinex egress)")
    from fibengine.data.loader import load_candles

    df = load_candles(cfg, fetch_if_missing=False)
    paths = sorted(
        p for p in glob.glob(str(FIB_DIR / "fib_*.json")) if not p.endswith("_events.json")
    )
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert len(paths) == manifest["timeframes"]["1d"]["count"], (
        "corpus drifted vs manifest - regenerate the manifest first (corpus_manifest --write)"
    )

    both_ok = total = 0
    for path in paths:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
        a, b = d["anchor_a"], d["anchor_b"]
        if a["time"] == b["time"]:
            continue  # same-candle fib: no time order to recover (FIB-AUDIT-005)
        hi, lo = (a, b) if a["price"] >= b["price"] else (b, a)
        res = transcribe_fib(
            df,
            high_price=hi["price"],
            low_price=lo["price"],
            direction=d["direction"],
            symbol="BTC/USD",
            timeframe="1d",
        )
        if res.annotation is None:
            total += 1
            continue
        rec_a, rec_b = res.annotation.anchor_a, res.annotation.anchor_b
        both_ok += int(rec_a.time == a["time"] and rec_b.time == b["time"])
        total += 1

    assert total > 0
    rate = both_ok / total
    print(f"\ntranscribe time-recovery: {both_ok}/{total} = {rate:.3f} (floor {FLOOR})")
    assert rate >= FLOOR, f"time-recovery {rate:.3f} fell below regression floor {FLOOR}"

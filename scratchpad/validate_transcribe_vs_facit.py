"""Validate fib_transcribe time-recovery against the 67 daily facit fibs (price+time known).

Leakage-free, deterministic. For each facit fib: feed its anchor PRICES (high/low) + direction
through transcribe_fib, then compare the RECOVERED times to the facit's recorded times. This
discriminates "the tool works" from "2 lucky screenshots" — especially the disambiguation
heuristic when a price repeats on several candles. Also dumps the delta distribution so
EXACT_TOL/NEAR_TOL can be calibrated empirically. Read-only; no facit is written.
"""

from __future__ import annotations

import glob
import json
import os

from fibengine.core.config import load_settings
from fibengine.data.loader import load_candles
from fibengine.labeling.fib_transcribe import transcribe_fib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIBS = sorted(glob.glob(f"{ROOT}/data/labels/human_fib/bitfinex/BTC-USD/1d/fib_*.json"))

settings = load_settings(f"{ROOT}/config/settings.expansion.yaml")
cfg = settings.data.model_copy(
    update={"exchange": "bitfinex", "symbol": "BTC/USD", "timeframe": "1d"}
)
df = load_candles(cfg, fetch_if_missing=False)

both_ok = a_ok = b_ok = total = 0
ambig_total = ambig_ok = 0  # anchors where a price repeats (n_within_near > 1) — the real test
deltas: list[float] = []
misses: list[str] = []

for path in FIBS:
    d = json.load(open(path))
    a, b = d["anchor_a"], d["anchor_b"]
    hi, lo = (a, b) if a["price"] >= b["price"] else (b, a)
    res = transcribe_fib(
        df,
        high_price=hi["price"],
        low_price=lo["price"],
        direction=d["direction"],
        symbol="BTC/USD",
        timeframe="1d",
    )
    total += 1
    if res.annotation is None:
        misses.append(f"{d['fib_id']}: no annotation (unrecoverable)")
        continue
    # recovered high/low time by role (origin/extreme map onto hi/lo via direction)
    rec = {m.role: m for m in res.matches}
    rec_hi, rec_lo = rec["high"], rec["low"]
    deltas += [m.rel_delta for m in res.matches if m.rel_delta is not None]

    hi_match = rec_hi.time == hi["time"]
    lo_match = rec_lo.time == lo["time"]
    a_ok += hi_match
    b_ok += lo_match
    both_ok += hi_match and lo_match
    for m, ok in ((rec_hi, hi_match), (rec_lo, lo_match)):
        if m.n_within_near > 1:
            ambig_total += 1
            ambig_ok += ok
    if not (hi_match and lo_match):
        misses.append(
            f"{d['fib_id']} ({d['direction']}): "
            f"hi {hi['time'][:10]}->{(rec_hi.time or '?')[:10]} {'OK' if hi_match else 'X'} "
            f"(near={rec_hi.n_within_near}); "
            f"lo {lo['time'][:10]}->{(rec_lo.time or '?')[:10]} {'OK' if lo_match else 'X'} "
            f"(near={rec_lo.n_within_near})"
        )


def pct(n: int, d: int) -> str:
    return f"{n}/{d} ({n / d:.1%})" if d else "0/0"


print(f"facit fibs: {total}")
print(f"both anchors time-match: {pct(both_ok, total)}")
print(f"  high-anchor: {pct(a_ok, total)}   low-anchor: {pct(b_ok, total)}")
print(f"repeated-price anchors correct: {pct(ambig_ok, ambig_total)}  (disambig test)")
if deltas:
    s = sorted(deltas)
    print(
        f"delta dist: min={s[0]:.2e} median={s[len(s) // 2]:.2e} "
        f"p90={s[int(0.9 * len(s))]:.2e} max={s[-1]:.2e}"
    )
    print(
        f"  within EXACT_TOL(2e-4): {sum(x <= 2e-4 for x in s)}/{len(s)}  "
        f"NEAR_TOL(1e-3): {sum(x <= 1e-3 for x in s)}/{len(s)}"
    )
if misses:
    print(f"\nmismatches ({len(misses)}):")
    for m in misses:
        print("  " + m)

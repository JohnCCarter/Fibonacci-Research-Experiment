"""#38 precursor sonde (read-only, leakage-free): do daily facit anchors sit on the
candle WICK EXTREME or on BODY/CLOSE?  Compares each human anchor price to the OHLC of
its own pinned daily candle. Pure stdlib. No detector, no target leakage, no edge claim."""

import csv
import glob
import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = f"{ROOT}/data/raw/bitfinex/BTC-USD/1d/limit_3500.csv"
FIBS = sorted(glob.glob(f"{ROOT}/data/labels/human_fib/bitfinex/BTC-USD/1d/fib_*.json"))

# index candles by date string (YYYY-MM-DD)
candles = {}
with open(CSV, newline="") as f:
    for r in csv.DictReader(f):
        day = r["timestamp"][:10]
        candles[day] = {k: float(r[k]) for k in ("open", "high", "low", "close")}

# tie tolerance: anchor counts as "on" a level if within this fraction of candle range
TIE_FRAC = 0.05  # 5% of the candle's high-low range = effectively snapped


def classify(anchor_price, is_top, c):
    rng = c["high"] - c["low"]
    if rng <= 0:
        return "degenerate", 0.0, 0.0, 0.0
    if is_top:
        wick, body = c["high"], max(c["open"], c["close"])
    else:
        wick, body = c["low"], min(c["open"], c["close"])
    d_wick = abs(anchor_price - wick) / rng
    d_body = abs(anchor_price - body) / rng
    # if anchor sits far from BOTH edges it isn't snapped to this candle extreme at all
    near = min(d_wick, d_body)
    if near > 0.25:  # >25% of range from the nearer edge
        label = "neither"
    elif abs(d_wick - d_body) <= TIE_FRAC:
        label = "tie"  # candle has ~no wick on that side (doji-ish)
    elif d_wick < d_body:
        label = "wick"
    else:
        label = "body_close"
    return label, d_wick, d_body, near


rows, unmatched = [], []
for path in FIBS:
    d = json.load(open(path))
    fid = d["fib_id"]
    a, b = d["anchor_a"], d["anchor_b"]
    # higher-priced anchor is the TOP, lower is the BOTTOM (direction-agnostic, robust)
    top, bot = (a, b) if a["price"] >= b["price"] else (b, a)
    for anchor, is_top, side in ((top, True, "top"), (bot, False, "bottom")):
        day = anchor["time"][:10]
        c = candles.get(day)
        if c is None:
            unmatched.append((fid, side, day))
            continue
        label, dw, db, near = classify(anchor["price"], is_top, c)
        rows.append((fid, side, label, dw, db, near))


# ---- report ----
def tally(filt):
    cnt = Counter(r[2] for r in rows if filt(r))
    n = sum(cnt.values())
    return cnt, n


print(f"facit: {len(FIBS)}  classified: {len(rows)}  unmatched: {len(unmatched)}")
for side in ("top", "bottom"):
    cnt, n = tally(lambda r, s=side: r[1] == s)
    parts = "  ".join(
        f"{k}={cnt[k]} ({cnt[k] / n:.0%})"
        for k in ("wick", "body_close", "tie", "neither", "degenerate")
        if cnt[k]
    )
    print(f"  {side:7s} n={n:3d}: {parts}")
cnt, n = tally(lambda r: True)
parts = "  ".join(
    f"{k}={cnt[k]} ({cnt[k] / n:.0%})"
    for k in ("wick", "body_close", "tie", "neither", "degenerate")
    if cnt[k]
)
print(f"  ALL     n={n:3d}: {parts}")


# median normalized distances
def med(xs):
    xs = sorted(xs)
    m = len(xs) // 2
    return (xs[m] if len(xs) % 2 else (xs[m - 1] + xs[m]) / 2) if xs else float("nan")


print(f"  median d_wick (norm by range): {med([r[3] for r in rows]):.3f}")
print(f"  median d_body (norm by range): {med([r[4] for r in rows]):.3f}")
if unmatched:
    print("  unmatched (anchor day not in candle cache):")
    for u in unmatched[:10]:
        print("    ", u)

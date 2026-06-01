"""One-off review helper for BTC 1d multi-leg label."""

from pandas import to_datetime

from fibengine.core.config import load_settings
from fibengine.core.fib import fib_from_prices
from fibengine.data.loader import load_candles
from fibengine.evaluation.bars import bar_of_timestamp
from fibengine.labeling.store import load_label

lbl = load_label("data/labels/binance/BTC-USDT/1d.json")
w = load_label("data/labels/binance/BTC-USDT/1w.json")
ddf = load_candles(
    load_settings().data.model_copy(update={"symbol": "BTC/USDT", "timeframe": "1d"})
)
legs = lbl.all_legs()
print("n_legs", len(legs))
print("created", lbl.created_at[:19])

bad_snap = []
for leg in legs:
    for pt, kind in [(leg.high, "H"), (leg.low, "L")]:
        bar, ok = bar_of_timestamp(ddf, pt.timestamp)
        if not ok:
            bad_snap.append((leg.id, kind, "OOW"))
            continue
        row = ddf.iloc[bar]
        target = float(row["high"] if kind == "H" else row["low"])
        if abs(target - pt.price) >= 0.02:
            bad_snap.append((leg.id, kind, pt.price, target))

print("snap_failures", len(bad_snap))

down = up = 0
for leg in legs:
    hi = to_datetime(leg.high.timestamp, utc=True)
    lo = to_datetime(leg.low.timestamp, utc=True)
    if lo < hi:
        up += 1
    else:
        down += 1
print("down_legs", down, "up_legs", up)

print("\n--- Timeline (leg id, direction, high date, low date) ---")
for leg in legs:
    hi = to_datetime(leg.high.timestamp, utc=True)
    lo = to_datetime(leg.low.timestamp, utc=True)
    direction = "up" if lo < hi else "down"
    print(
        leg.id,
        direction,
        leg.high.timestamp[:10],
        int(leg.high.price),
        leg.low.timestamp[:10],
        int(leg.low.price),
    )

print("\nweekly HTF", int(w.high.price), "->", int(w.low.price))
print(
    "leg_1 == weekly impulse endpoints",
    legs[0].high.price == w.high.price and legs[0].low.price == w.low.price,
)

# best up-leg from ~60k toward 80k+
best = None
for leg in legs:
    hi = to_datetime(leg.high.timestamp, utc=True)
    lo = to_datetime(leg.low.timestamp, utc=True)
    if lo < hi and leg.low.price <= 61000 and leg.high.price >= 78000:
        if best is None or leg.high.price > best.high.price:
            best = leg
if best:
    f618 = fib_from_prices(best.low.price, best.high.price, [0.618])
    print(
        "best_up_from_60k",
        best.id,
        best.low.timestamp[:10],
        "->",
        best.high.timestamp[:10],
        int(best.high.price),
        "fib618",
        int(f618[0.618]),
    )

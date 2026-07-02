"""Windowed snap of Chamoun's 1w cascade legs to the frozen 1w cache (2026-07-02).

Unblocks the CASCADE probe: a PRICE-ONLY snap scrambled chronology because BTC passed 16-30k twice.
Chamoun dated BOTTOM_LEFT = 2020-21 ("nr 1"). Directions are already encoded in the drawn prices
(origin<endpoint = up; origin>endpoint = down), so "furthest=downtrend" = RIGHT (most recent).

Per group we constrain the search to a rough YEAR window, then snap:
  - up leg   (1<0): origin -> week LOW  ~= price "1"; endpoint -> week HIGH ~= price "0"
  - down leg (1>0): origin -> week HIGH ~= price "1"; endpoint -> week LOW  ~= price "0"
requiring the endpoint week strictly AFTER the origin week. This is a mechanical dating aid, not the
probe; no fib/edge claim.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

CACHE = Path("data/raw/bitfinex/BTC-USD/1w/limit_1000.csv")

# (origin "1", endpoint "0"); grouped as drawn. Year windows are rough, per Chamoun's dating.
GROUPS = {
    "BOTTOM_LEFT (2020-21, up)": (
        [(16838, 19592), (24240, 30968)],
        ("2020-06-01", "2021-07-01"),
    ),
    "MID (2023-25, up)": (
        [(38572, 73666), (58943, 108100), (74501, 125710)],
        ("2022-11-01", "2025-12-31"),
    ),
    "RIGHT (2025-26, down)": (
        [(116500, 80822), (97850, 60100)],
        ("2025-10-05", "2026-06-30"),  # after the Oct-2025 ATH: down-cascade follows the top
    ),
}


def load_weeks() -> list[dict]:
    rows = []
    with open(CACHE, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append(
                {
                    "t": datetime.fromisoformat(r["timestamp"]),
                    "high": float(r["high"]),
                    "low": float(r["low"]),
                }
            )
    return rows


def snap_price(weeks, price, use_high, after=None):
    """Nearest week whose high (or low) matches `price`, optionally after a given datetime."""
    best, best_err = None, None
    for w in weeks:
        if after is not None and w["t"] <= after:
            continue
        px = w["high"] if use_high else w["low"]
        err = abs(px - price) / price
        if best_err is None or err < best_err:
            best, best_err = w, err
    return best, best_err


def main() -> None:
    all_weeks = load_weeks()
    for name, (legs, (lo, hi)) in GROUPS.items():
        w0, w1 = (
            datetime.fromisoformat(lo + "T00:00:00+00:00"),
            datetime.fromisoformat(hi + "T00:00:00+00:00"),
        )
        weeks = [w for w in all_weeks if w0 <= w["t"] <= w1]
        print(f"\n### {name}  (window {lo}..{hi}, {len(weeks)} weeks)")
        for o, e in legs:
            up = o < e
            o_week, o_err = snap_price(weeks, o, use_high=not up)
            e_week, e_err = snap_price(weeks, e, use_high=up, after=o_week["t"] if o_week else None)
            dur = (e_week["t"] - o_week["t"]).days // 7 if (o_week and e_week) else None
            mag = abs(e - o) / min(o, e)
            print(
                f"  1({o:>7,})->0({e:>8,}) {'UP  ' if up else 'DOWN'} | "
                f"1@{o_week['t'].date()} (err {o_err:.1%})  0@{e_week['t'].date()} "
                f"(err {e_err:.1%}) | dur={dur}w mag={mag:.0%}"
            )


if __name__ == "__main__":
    main()

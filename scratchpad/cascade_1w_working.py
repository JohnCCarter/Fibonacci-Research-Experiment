"""1w CASCADE working set — Chamoun-drawn (2026-07-01), for the scale-consistency cascade probe.

WHY THIS EXISTS: the committed facit is too sparse to chain (power check: 1d 9 links/76, longest
run 2), so Chamoun drew ONE continuous weekly cascade on TradingView to test his strongest
introspective signal — "nasta rena impuls i sekvensen ... eget ben i trenden, inte chop inne i ett
storre ben" (trend-sequential cascade). Source = a 1w BTC/USD Bitfinex screenshot pasted in chat
(NOT on disk; do not commit the image). The prices below are the fib "1"/"0" labels he drew.

CHAMOUN'S CLARIFICATIONS (gist, 2026-07-01):
  - bottom-left = TWO fib structures: {16,838 / 19,592} and {24,240 / 30,968}
  - leg corrected: 58,943 -> 108,100 (agent misread it as 63,913)
  - "tva separata kaskader" (two separate cascades — group scale-consistency per cascade)
  - "dem langst bort ar nedgang" (the furthest cascade is a DOWNTREND); direction UNRESOLVED

DATING RESOLVED 2026-07-02: Chamoun dated BOTTOM_LEFT = 2020-21 ("nr 1"); directions read off the
drawn prices (origin<endpoint=up, origin>endpoint=down), so "furthest=downtrend" = RIGHT (most
recent). Windowed snap in cascade_1w_snap.py placed every leg forward-in-time (BL 2020-11..2021-01,
MID 2024-01..2025-10, RIGHT 2025-10..2026-06). See DATED below.

CV PROBE DEAD (advisor, 2026-07-02): the scale-consistency test cannot run — 7 legs total (2/3/2 per
group), and duration is ALREADY inconsistent (MID 7w/44w/26w, ~6x spread) plus a within-MID snap
inversion (leg 3 origin before leg 2 endpoint). Grouping into cascades = "ingen aning" (Chamoun has
no introspection on it), so "cascade" is an imposed frame. Redirect: the drawn cascade's value is as
contrastive annotation input (why each leg, why not neighbours), not a geometric statistic. Kept as
durable facit only.
"""

from __future__ import annotations

# Leg price pairs as drawn (origin "1", endpoint "0"). DATED 2026-07-02 (see DATED below).
BOTTOM_LEFT = [(16838, 19592), (24240, 30968)]  # up; 2020-11 .. 2021-01
MID = [(38572, 73666), (58943, 108100), (74501, 125710)]  # up; 2024-01 .. 2025-10 (endpoint = ATH)
RIGHT = [(116500, 80822), (97850, 60100)]  # down; 2025-10 .. 2026-06 (furthest = downtrend)

ALL_LEGS = BOTTOM_LEFT + MID + RIGHT

# (price_1, price_0, iso_week_1, iso_week_0) — snap output from cascade_1w_snap.py.
DATED = {
    "BOTTOM_LEFT_up": [
        (16838, 19592, "2020-11-12", "2020-11-19"),
        (24240, 30968, "2020-12-17", "2021-01-21"),
    ],
    "MID_up": [
        (38572, 73666, "2024-01-18", "2024-03-07"),
        (58943, 108100, "2024-08-15", "2025-06-19"),
        (74501, 125710, "2025-04-03", "2025-10-02"),
    ],
    "RIGHT_down": [
        (116500, 80822, "2025-10-09", "2026-04-30"),
        (97850, 60100, "2026-01-08", "2026-06-04"),
    ],
}

if __name__ == "__main__":
    print("1w cascade working set (DATED 2026-07-02; CV probe dead — kept as facit):")
    for i, (o, e) in enumerate(ALL_LEGS, 1):
        print(f"  leg{i}: 1({o:>7,}) -> 0({e:>8,})  mag={abs(e - o) / min(o, e):.0%}")

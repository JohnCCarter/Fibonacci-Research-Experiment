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

BLOCKER (why we paused): a PRICE-ONLY snap to the 1w cache scrambles the chronology. BTC passed the
low levels (16-30k) MORE THAN ONCE (~2020-21 AND ~2022-23), so nearest-price matching places the
early legs on wrong weeks (one leg even ran backward in time). Unique highs (125,710) snap fine;
repeated levels do not. FIX on resume: rough YEAR per cascade + direction confirm, then window snap.

PLANNED PROBE (when the legs are correctly dated) — advisor-designed, do NOT build a circular one:
  scale-consistency = coefficient-of-variation of leg MAGNITUDE (exact from prices) and DURATION
  (weeks) across his cascade, vs independently-placed clean legs (generator) in the same span. The
  null must CONDITION OUT definitional chaining (his legs chain because he drew them to — the
  k_between trap on the sequence side): test whether his legs are TIGHTER / more scale-consistent
  than chained-but-independent clean legs, not merely that they chain. Two cascades grouped apart.

OPEN QUESTIONS FOR CHAMOUN (on resume):
  1. Roughly which YEARS does each cascade cover? (readable off his chart; no exact dates needed)
  2. Confirm: cascade 1 (furthest) = downtrend (1=high -> 0=low); cascade 2 = other direction?
"""

from __future__ import annotations

# Leg price pairs as drawn (origin "1", endpoint "0"); DIRECTION/grouping PENDING Chamoun's confirm.
# Recorded so the facit survives (chat/screenshot is not durable). NOT final until dated.
BOTTOM_LEFT = [(16838, 19592), (24240, 30968)]  # two fib structures; "furthest=downtrend" (open)
MID = [(38572, 73666), (58943, 108100), (74501, 125710)]  # 58,943 corrected
RIGHT = [(116500, 80822), (97850, 60100)]  # recent down-cascade (1=high -> 0=low)

ALL_LEGS = BOTTOM_LEFT + MID + RIGHT

if __name__ == "__main__":
    print("1w cascade working set (prices as drawn; dating BLOCKED pending years + directions):")
    for i, (o, e) in enumerate(ALL_LEGS, 1):
        print(f"  leg{i}: 1({o:>7,}) -> 0({e:>8,})  mag={abs(e - o) / min(o, e):.0%}")
    print("\nResume: get rough years per cascade + confirm directions, then snap within windows.")

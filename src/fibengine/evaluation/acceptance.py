"""Locked acceptance tolerance — "snarlikt räcker" graded into 3 hit tiers + miss.

Single source of truth for whether the engine reproduced a human fib closely ENOUGH — so we grade
"close", not "perfect", and never chase pixel-perfection. Chamoun's bar: the **origin must sit**
(tight, bars + price), the **"0" endpoint may be approximate** (price-only, looser). Three tiers so
a near-miss is graded, not binary.

LOCKED 2026-07-02. Changing these numbers is a deliberate, versioned act — do NOT tune them post-hoc
to make a result pass (validity: lock before scoring). Everything that judges engine-vs-facit
agreement should import from here.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class MatchTier(IntEnum):
    """Ordered so a higher tier is a better match; compare with ``>=`` against the accept line."""

    MISS = 0
    NEAR = 1
    SNARLIKT = 2
    EXACT = 3


@dataclass(frozen=True)
class Band:
    """One tier's band: max bar offset (``None`` = time ignored) and max price deviation (pct)."""

    max_bars: int | None
    max_price_pct: float


@dataclass(frozen=True)
class AnchorTolerance:
    """Per-anchor bands, tightest → widest."""

    exact: Band
    snarlikt: Band
    near: Band

    def graded(self) -> tuple[tuple[MatchTier, Band], ...]:
        return (
            (MatchTier.EXACT, self.exact),
            (MatchTier.SNARLIKT, self.snarlikt),
            (MatchTier.NEAR, self.near),
        )


# Origin sits tight (bars + price); the "0" endpoint is price-only and looser (Chamoun's bar).
ORIGIN = AnchorTolerance(
    exact=Band(max_bars=1, max_price_pct=0.75),
    snarlikt=Band(max_bars=2, max_price_pct=1.5),
    near=Band(max_bars=3, max_price_pct=2.0),
)
ENDPOINT = AnchorTolerance(
    exact=Band(max_bars=None, max_price_pct=2.0),
    snarlikt=Band(max_bars=None, max_price_pct=4.0),
    near=Band(max_bars=None, max_price_pct=6.0),
)

# The weakest tier that still counts as "reproduced". NEAR = Chamoun's "increase our hits" call.
ACCEPT_AT = MatchTier.NEAR


def price_pct(pred_price: float, true_price: float) -> float:
    """Absolute price deviation as a percent of the human anchor price."""
    if true_price == 0:
        raise ValueError("true_price must be non-zero")
    return abs(pred_price - true_price) / abs(true_price) * 100.0


def classify_anchor(
    pred_price: float,
    true_price: float,
    *,
    is_origin: bool,
    pred_bar: int | None = None,
    true_bar: int | None = None,
) -> MatchTier:
    """Grade one predicted anchor against the human's.

    Weakest-link: to earn a tier, BOTH the price deviation and (for the origin) the bar offset must
    fall within that tier's band. Returns the best (tightest) tier that holds, else ``MISS``.
    """
    tol = ORIGIN if is_origin else ENDPOINT
    dp = price_pct(pred_price, true_price)
    db = abs(pred_bar - true_bar) if (pred_bar is not None and true_bar is not None) else 0
    for tier, band in tol.graded():
        bar_ok = band.max_bars is None or db <= band.max_bars
        if dp <= band.max_price_pct and bar_ok:
            return tier
    return MatchTier.MISS


def anchor_accepted(tier: MatchTier, accept_at: MatchTier = ACCEPT_AT) -> bool:
    """Does this anchor's tier reach the accept line?"""
    return tier >= accept_at


def leg_accepted(
    origin_tier: MatchTier,
    endpoint_tier: MatchTier,
    accept_at: MatchTier = ACCEPT_AT,
) -> bool:
    """A leg is reproduced iff BOTH anchors reach the accept tier (weakest link)."""
    return anchor_accepted(origin_tier, accept_at) and anchor_accepted(endpoint_tier, accept_at)

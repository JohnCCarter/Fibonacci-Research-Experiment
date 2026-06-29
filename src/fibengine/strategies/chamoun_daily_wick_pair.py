"""Chamoun daily wick-pair A/B-väljare (#38, deskriptiv ankar-accuracy).

Net-ny detektionsfilosofi vs ``pivots.detect``: kandidat-ankaren är **rejection
wicks** (lång stake relativt candle-range) på daily, och A/B-paret väljs som det
impulsben vars endpoint **bryter** föregående motsvarande extrem (BOS) och vars
start är den **dominanta** motsatta rejection-wicken i retracement-zonen. Detta
är within-TF sekventiell impuls-logik (samma som facit-bilderna visar), inte
cross-TF nesting.

Ren funktion: **anroparen** trunkerar ramen kausalt (``df`` ⊆ index ≤ B) före
anrop — modulen tittar aldrig framåt. Endast A/B-VAL; ingen edge/PnL/continuation.

Wick-tröskeln (``wick_frac``) är en **a priori-hypotesknapp**, satt före run och
rapporterad — den trimmas aldrig mot facit (det vore leakage).

Låst pre-reg: docs/research_wiki/reviews/btc-fib-daily-wick-pair-anchor-prereg-20260629.md
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from fibengine.core.config import PivotConfig
from fibengine.core.models import Pivot, Swing
from fibengine.data.loader import atr

# A priori: en rejection-wick stakar ut minst denna andel av candle-range på sin
# sida. Satt före run (ingen facit-trimning). Rapporteras med resultatet.
DEFAULT_WICK_FRAC = 0.5


@dataclass
class WickPairSelection:
    """Vald A/B-leg + audit-trail över varför just det paret valdes."""

    swing: Swing | None
    candidates: list[Pivot]
    audit: list[dict] = field(default_factory=list)


def _wick_fracs(o: float, h: float, low: float, c: float) -> tuple[float, float]:
    """(övre, undre) wick som andel av range; (0, 0) för degenererad candle."""
    rng = h - low
    if rng <= 0:
        return 0.0, 0.0
    upper = (h - max(o, c)) / rng
    lower = (min(o, c) - low) / rng
    return upper, lower


def detect_wick_pivots(
    df: pd.DataFrame,
    cfg: PivotConfig,
    wick_frac: float = DEFAULT_WICK_FRAC,
) -> list[Pivot]:
    """Kandidat-universum: lokala extrema vars swing-sida är en rejection-wick.

    Som ``detect_pivots`` lokaliseras lokala extrema över ett lookback-fönster och
    filtreras på ATR-skalad prominens, MEN dessutom krävs att den extrema sidans
    wick är minst ``wick_frac`` av candle-range. Det är den enda skillnaden mot
    pivot-kontrollen — wick-geometrin, inte pivot-primitiven.
    """
    o = df["open"].to_numpy()
    h = df["high"].to_numpy()
    low = df["low"].to_numpy()
    c = df["close"].to_numpy()
    atr_series = atr(df, cfg.atr_period).to_numpy()
    n = len(df)
    lb = cfg.lookback
    pivots: list[Pivot] = []

    for i in range(n):
        local_atr = atr_series[i]
        if not local_atr or local_atr != local_atr:  # NaN/0 under uppvärmning
            continue
        window_high = h[max(0, i - lb) : min(n, i + lb + 1)].max()
        window_low = low[max(0, i - lb) : min(n, i + lb + 1)].min()
        is_high = h[i] == window_high
        is_low = low[i] == window_low
        if is_high and is_low:  # inside/degenererad — låt prominens avgöra sidan
            is_high = (h[i] - window_low) >= (window_high - low[i])
            is_low = not is_high
        upper_frac, lower_frac = _wick_fracs(o[i], h[i], low[i], c[i])

        if is_high and upper_frac >= wick_frac:
            prom = (h[i] - window_low) / local_atr
            if prom >= cfg.min_prominence_atr:
                pivots.append(Pivot(i, df.index[i], float(h[i]), "high", float(prom)))
        if is_low and lower_frac >= wick_frac:
            prom = (window_high - low[i]) / local_atr
            if prom >= cfg.min_prominence_atr:
                pivots.append(Pivot(i, df.index[i], float(low[i]), "low", float(prom)))

    return _dedupe_alternating(pivots)


def _dedupe_alternating(pivots: list[Pivot]) -> list[Pivot]:
    """Sortera på tid, kollapsa intilliggande pivots av samma typ till den mest extrema."""
    pivots = sorted(pivots, key=lambda p: p.index)
    result: list[Pivot] = []
    for p in pivots:
        if result and result[-1].kind == p.kind:
            prev = result[-1]
            keep_new = p.price > prev.price if p.kind == "high" else p.price < prev.price
            if keep_new:
                result[-1] = p
        else:
            result.append(p)
    return result


def select_wick_pair(
    df: pd.DataFrame,
    cfg: PivotConfig,
    wick_frac: float = DEFAULT_WICK_FRAC,
) -> WickPairSelection:
    """Välj A/B-paret: B = senaste BOS-rejection-extrem, A = dominant motsatt wick.

    B (endpoint) = den senaste rejection-pivot som bryter alla föregående pivots av
    samma typ (down: ny lägsta low; up: ny högsta high). A (start) = den dominanta
    motsatta rejection-pivoten i retracement-zonen mellan föregående samma-typ-extrem
    och B. Returnerar ``swing=None`` om inget BOS-par finns (räknas som miss, inte krasch).
    """
    cands = detect_wick_pivots(df, cfg, wick_frac)
    audit: list[dict] = []

    # Senaste BOS-endpoint: en pivot som är mer extrem än alla tidigare av sin typ.
    best_high = float("-inf")
    best_low = float("inf")
    bos: list[tuple[int, Pivot, int]] = []  # (kandidat-idx i cands, pivot, prev_same_idx)
    last_high_idx: int | None = None
    last_low_idx: int | None = None
    for j, p in enumerate(cands):
        if p.kind == "high":
            if p.price > best_high:
                bos.append((j, p, last_high_idx if last_high_idx is not None else -1))
            best_high = max(best_high, p.price)
            last_high_idx = j
        else:
            if p.price < best_low:
                bos.append((j, p, last_low_idx if last_low_idx is not None else -1))
            best_low = min(best_low, p.price)
            last_low_idx = j

    if not bos:
        audit.append({"event": "no_bos_endpoint", "n_candidates": len(cands)})
        return WickPairSelection(swing=None, candidates=cands, audit=audit)

    b_j, b_pivot, prev_same_j = bos[-1]
    zone_start = prev_same_j + 1 if prev_same_j >= 0 else 0
    opp_kind = "low" if b_pivot.kind == "high" else "high"
    zone = [p for p in cands[zone_start:b_j] if p.kind == opp_kind]
    audit.append(
        {
            "event": "bos_endpoint_chosen",
            "b_index": b_pivot.index,
            "b_kind": b_pivot.kind,
            "b_price": b_pivot.price,
            "n_bos_candidates": len(bos),
            "zone_opp_pivots": len(zone),
        }
    )
    if not zone:
        audit.append({"event": "no_opposite_start_in_zone"})
        return WickPairSelection(swing=None, candidates=cands, audit=audit)

    # Dominant start: högsta high (för down-impuls) / lägsta low (för up-impuls).
    if opp_kind == "high":
        a_pivot = max(zone, key=lambda p: p.price)
    else:
        a_pivot = min(zone, key=lambda p: p.price)
    audit.append(
        {
            "event": "start_chosen",
            "a_index": a_pivot.index,
            "a_kind": a_pivot.kind,
            "a_price": a_pivot.price,
        }
    )
    swing = Swing(start=a_pivot, end=b_pivot, status="provisional")
    return WickPairSelection(swing=swing, candidates=cands, audit=audit)

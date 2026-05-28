"""Multi-skala-confluence: är en svängs vändpunkter signifikanta på flera grader?

Fraktal självlikhet i praktiken: en stor våg innehåller mindre vågor. En sväng
vars endpunkter också är fraktal-vändpunkter på *större* grad är mer pålitlig.
Detta är den testbara mekanismen — confluence över skalor, inte 1.618-mystik.
"""

from __future__ import annotations

import pandas as pd

from fibengine.config import PivotConfig
from fibengine.models import Pivot, Swing
from fibengine.pivots.detect import detect_pivots


def detect_pivots_multi(
    df: pd.DataFrame, base_cfg: PivotConfig, degrees: list[int]
) -> dict[int, list[Pivot]]:
    """Kör fraktal-detektion en gång per grad (fractal_n). Returnerar grad -> pivots."""
    multi: dict[int, list[Pivot]] = {}
    for d in degrees:
        cfg = base_cfg.model_copy(update={"mode": "fractal", "fractal_n": d})
        multi[d] = detect_pivots(df, cfg)
    return multi


def _endpoints(swing: Swing) -> tuple[Pivot, Pivot]:
    """Returnera (high-endpunkt, low-endpunkt) oavsett legens riktning."""
    if swing.start.kind == "high":
        return swing.start, swing.end
    return swing.end, swing.start


def endpoint_confluence(
    swing: Swing, multi_pivots: dict[int, list[Pivot]], tol_bars: int
) -> float:
    """Andel större grader där BÅDE legens high och low bekräftas. ∈ [0, 1].

    Neutral 0.5 när inga större grader/pivots finns att jämföra mot.
    """
    if not multi_pivots:
        return 0.5
    high_ep, low_ep = _endpoints(swing)
    scores: list[float] = []
    for pivots in multi_pivots.values():
        if not pivots:
            continue
        hi_conf = any(
            p.kind == "high" and abs(p.index - high_ep.index) <= tol_bars for p in pivots
        )
        lo_conf = any(
            p.kind == "low" and abs(p.index - low_ep.index) <= tol_bars for p in pivots
        )
        scores.append((hi_conf + lo_conf) / 2.0)
    if not scores:
        return 0.5
    return sum(scores) / len(scores)

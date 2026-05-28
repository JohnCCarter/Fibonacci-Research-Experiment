"""Kausalt walk-forward: hur stabilt väljer motorn swing över tid? (Lager A)

Vid varje cursor-position t kör vi urvalet på ENBART data ≤ t (df.iloc[:t+1]),
så ingen framtid läcker in — fraktaler nära högerkanten saknar bekräftande
framtida barer och blir naturligt inte pivots. Vi mäter sedan hur ofta valet
ändras, hur länge en vald leg håller, och hur långt endpunkterna driftar.
"""

from __future__ import annotations

import pandas as pd

from fibengine.config import Settings
from fibengine.models import Swing
from fibengine.scoring import select_swing


def walk_forward_selection(
    df: pd.DataFrame, settings: Settings, warmup_bars: int, step: int
) -> list[dict]:
    """Stega genom historiken och välj swing kausalt vid varje steg."""
    records: list[dict] = []
    for t in range(warmup_bars, len(df), step):
        window = df.iloc[: t + 1]
        swing = select_swing(window, settings.pivots, settings.scoring)
        records.append({"t": t, "swing": swing})
    return records


def _leg_id(swing: Swing | None) -> tuple[int, int] | None:
    return None if swing is None else (swing.start.index, swing.end.index)


def _transition(a: Swing | None, b: Swing | None, ext_tol: int) -> str:
    """Klassificera en övergång: 'same', 'extension' (ofarlig) eller 'jump'."""
    if a is None or b is None:
        return "same" if a is b else "jump"
    if _leg_id(a) == _leg_id(b):
        return "same"
    same_origin = a.direction == b.direction and a.start.index == b.start.index
    if same_origin and 0 < (b.end.index - a.end.index) <= ext_tol:
        return "extension"
    return "jump"


def stability_metrics(records: list[dict], extension_tol_bars: int = 5) -> dict:
    """Sammanfatta hur stabilt urvalet är över walk-forward-stegen.

    `flip_rate` räknar bara riktiga hopp — en sväng vars endpunkt växer +1 bar
    (samma start, samma riktning) klassas som 'extension', inte instabilitet.
    """
    legs = [r["swing"] for r in records]
    ids = [_leg_id(s) for s in legs]
    dirs = [None if s is None else s.direction for s in legs]
    n = len(ids)
    if n < 2:
        return {"steps": n, "flip_rate": 0.0, "raw_change_rate": 0.0,
                "extension_rate": 0.0, "persistence_steps": float(n),
                "direction_consistency": 1.0, "mean_endpoint_drift_bars": 0.0,
                "confirmed_rate": _confirmed_rate(legs), "n_none": sum(1 for x in ids if x is None)}

    pairs = list(zip(ids, ids[1:], strict=False))
    transitions = [
        _transition(a, b, extension_tol_bars)
        for a, b in zip(legs, legs[1:], strict=False)
    ]
    n_pairs = len(pairs)
    raw_change_rate = sum(1 for a, b in pairs if a != b) / n_pairs
    flip_rate = sum(1 for t in transitions if t == "jump") / n_pairs
    extension_rate = sum(1 for t in transitions if t == "extension") / n_pairs

    dir_pairs = list(zip(dirs, dirs[1:], strict=False))
    valid_dir_pairs = [(a, b) for a, b in dir_pairs if a is not None and b is not None]
    if valid_dir_pairs:
        same_dir = sum(1 for a, b in valid_dir_pairs if a == b)
        direction_consistency = same_dir / len(valid_dir_pairs)
    else:
        direction_consistency = 0.5

    # Genomsnittlig run-längd för samma leg-identitet.
    runs: list[int] = []
    cur = 1
    for a, b in pairs:
        if a == b:
            cur += 1
        else:
            runs.append(cur)
            cur = 1
    runs.append(cur)
    persistence = sum(runs) / len(runs)

    # Endpunkts-drift vid riktiga hopp (i barer).
    drifts: list[int] = []
    for (a, b), t in zip(zip(legs, legs[1:], strict=False), transitions, strict=False):
        if t == "jump" and a is not None and b is not None:
            drifts.append(abs(a.start.index - b.start.index) + abs(a.end.index - b.end.index))
    mean_drift = sum(drifts) / len(drifts) if drifts else 0.0

    return {
        "steps": n,
        "flip_rate": round(flip_rate, 4),
        "raw_change_rate": round(raw_change_rate, 4),
        "extension_rate": round(extension_rate, 4),
        "persistence_steps": round(persistence, 4),
        "direction_consistency": round(direction_consistency, 4),
        "mean_endpoint_drift_bars": round(mean_drift, 4),
        "confirmed_rate": _confirmed_rate(legs),
        "n_none": sum(1 for x in ids if x is None),
    }


def _confirmed_rate(legs: list[Swing | None]) -> float:
    present = [s for s in legs if s is not None]
    if not present:
        return 0.0
    return round(sum(1 for s in present if s.status == "confirmed") / len(present), 4)

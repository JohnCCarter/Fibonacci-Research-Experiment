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


def stability_metrics(records: list[dict]) -> dict:
    """Sammanfatta hur stabilt urvalet är över walk-forward-stegen."""
    legs = [r["swing"] for r in records]
    ids = [_leg_id(s) for s in legs]
    dirs = [None if s is None else s.direction for s in legs]
    n = len(ids)
    if n < 2:
        return {"steps": n, "flip_rate": 0.0, "persistence_steps": float(n),
                "direction_consistency": 1.0, "mean_endpoint_drift_bars": 0.0,
                "n_none": sum(1 for x in ids if x is None)}

    pairs = list(zip(ids, ids[1:], strict=False))
    changes = sum(1 for a, b in pairs if a != b)
    flip_rate = changes / len(pairs)

    dir_pairs = list(zip(dirs, dirs[1:], strict=False))
    same_dir = sum(1 for a, b in dir_pairs if a is not None and a == b)
    direction_consistency = same_dir / len(dir_pairs)

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

    # Endpunkts-drift när valet faktiskt byts (i barer).
    drifts: list[int] = []
    for a, b in zip(legs, legs[1:], strict=False):
        if a is not None and b is not None and _leg_id(a) != _leg_id(b):
            drifts.append(abs(a.start.index - b.start.index) + abs(a.end.index - b.end.index))
    mean_drift = sum(drifts) / len(drifts) if drifts else 0.0

    return {
        "steps": n,
        "flip_rate": round(flip_rate, 4),
        "persistence_steps": round(persistence, 4),
        "direction_consistency": round(direction_consistency, 4),
        "mean_endpoint_drift_bars": round(mean_drift, 4),
        "n_none": sum(1 for x in ids if x is None),
    }

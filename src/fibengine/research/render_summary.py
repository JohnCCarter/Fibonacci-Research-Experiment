"""Stable, text-diffable summaries of chart-render results for structural regression.

Converts render results / output dirs into deterministic dicts — no absolute paths, no
timestamps, forward-slash relative paths, sorted order — so accidental drift in counts,
filenames, clean/levels pairing, scope/grouping, or windows is caught by committed JSON
snapshots. **No pixels, no binary baselines, no new dependencies.** This is the automatic
structural regression layer; it complements (does not replace) the HTML gallery + review
ledger manual visual layer.

The summary intentionally omits level *prices* (those live in — and are contract-tested
via — the source fib JSON) and any volatile metadata. Functions are duck-typed on the
render result objects, so importing this module pulls no plotting backend.
"""

from __future__ import annotations

import os
from pathlib import Path

from fibengine.research.artifact_gallery import _scan


def _rel(path: Path | str | None, root: Path | str) -> str | None:
    """Forward-slash path relative to ``root`` (stable across machines); None passthrough."""
    if path is None:
        return None
    return Path(os.path.relpath(Path(path), Path(root))).as_posix()


def map_summary(result, root: Path | str) -> dict:
    """Structural summary of a ``FourhSourceFibMap`` (annual maps), groups sorted by label."""
    groups = sorted(result.per_group, key=lambda g: g.label)
    return {
        "flow": "fourh_source_fib_map",
        "fib_count": result.fib_count,
        "groups": [
            {
                "label": g.label,
                "fib_count": g.fib_count,
                "drawn": g.drawn,
                "skipped": len(g.skipped),
                "clean": _rel(g.clean, root),
                "levels": _rel(g.levels, root),
                "window_start": g.window_start,
                "window_end": g.window_end,
            }
            for g in groups
        ],
    }


def zoom_summary(result, root: Path | str) -> dict:
    """Structural summary of a ``FourhSourceFibZoom`` (per-fib), artifacts sorted by fib_id."""
    arts = sorted(result.artifacts, key=lambda a: a.fib_id)
    return {
        "flow": "fourh_source_fib_zoom",
        "scope": result.scope,
        "fib_count": result.fib_count,
        "rendered": result.rendered,
        "skipped": len(result.skipped),
        "artifacts": [
            {
                "fib_id": a.fib_id,
                "clean": _rel(a.clean, root),
                "levels": _rel(a.levels, root),
                "skipped": a.skipped,
            }
            for a in arts
        ],
    }


def gallery_summary(root: Path | str) -> dict:
    """Structural summary of an artifact-gallery output dir (groups/items/kinds + links)."""
    root = Path(root)
    groups = _scan(root)  # already sorted by group label; raises if empty
    return {
        "flow": "artifact_gallery",
        "groups": [
            {
                "label": g.label,
                "items": [
                    {
                        "label": item_label,
                        "kinds": sorted(g.items[item_label].images),
                        "images": {
                            kind: _rel(g.items[item_label].images[kind], root)
                            for kind in sorted(g.items[item_label].images)
                        },
                    }
                    for item_label in sorted(g.items)
                ],
            }
            for g in groups
        ],
    }

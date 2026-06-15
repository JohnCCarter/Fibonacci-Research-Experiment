"""Static HTML gallery for review artifacts — stdlib-only, zero dependencies.

Scans a directory of generated review PNGs (e.g. ``experiments/review/
fourh_source_fib_map`` or ``.../fourh_source_fib_zoom``) and writes a self-contained
``index.html`` beside them, grouping clean + levels per item with relative ``<img>``
links so the batch can be reviewed in a browser.

This is a **review-ergonomics helper, not a renderer**: it never creates charts, never
reads or touches source fibs, and never modifies the existing markdown index. The HTML is
written under ``experiments/review/**`` (gitignored) and **must not be committed**.

Two output layouts are recognized automatically:

- **map** (flat): ``<root>/fourh_source_fib_map_<label>_4h_<kind>.png`` — one ``maps``
  group, one item per ``<label>`` stem (everything before ``_4h_``).
- **zoom** (nested): ``<root>/<scope>/<fib_id>/4h_<kind>.png`` — one group per scope, one
  item per fib_id.

No external CSS/JS; all styling is inline. Links are relative. Open ``index.html``
directly in a browser.

Usage::

    python -m fibengine.research.artifact_gallery \\
        --root experiments/review/fourh_source_fib_zoom

    python -m fibengine.research.artifact_gallery \\
        --root experiments/review/fourh_source_fib_map
"""

from __future__ import annotations

import argparse
import html
import os
from dataclasses import dataclass, field
from pathlib import Path

# Column order for the clean/levels pair, left-to-right.
_KIND_ORDER = ("clean", "levels", "levels_labeled", "other")


def _classify_kind(name: str) -> str:
    """Map a PNG filename to its chart kind by substring (longest match first)."""
    low = name.lower()
    if "levels_labeled" in low:
        return "levels_labeled"
    if "levels" in low:
        return "levels"
    if "clean" in low:
        return "clean"
    return "other"


def _map_item_label(name: str) -> str:
    """Item label of a flat map PNG: the stem before the ``_4h_<kind>.png`` suffix."""
    marker = "_4h_"
    if marker in name:
        return name[: name.rindex(marker)]
    return Path(name).stem


@dataclass
class _Item:
    label: str
    images: dict[str, Path] = field(default_factory=dict)  # kind -> path


@dataclass
class _Group:
    label: str
    items: dict[str, _Item] = field(default_factory=dict)  # item label -> _Item


def _scan(root: Path) -> list[_Group]:
    """Group every PNG under ``root`` into (group -> item -> kind) by path shape.

    Raises ``FileNotFoundError`` if no PNGs are found, so an empty/unrendered directory
    fails clearly instead of writing an empty gallery.
    """
    pngs = sorted(root.rglob("*.png"))
    if not pngs:
        raise FileNotFoundError(
            f"No .png artifacts found under {root} — render the maps/zoom first, "
            "then build the gallery."
        )
    groups: dict[str, _Group] = {}
    for p in pngs:
        parts = p.relative_to(root).parts
        if len(parts) >= 3:  # nested zoom: <scope>/<fib_id>/file.png
            group_label, item_label = parts[0], parts[1]
        elif len(parts) == 2:  # one level: <group>/file.png
            group_label, item_label = parts[0], Path(parts[1]).stem
        else:  # flat map: file.png
            group_label, item_label = "maps", _map_item_label(parts[0])
        group = groups.setdefault(group_label, _Group(label=group_label))
        item = group.items.setdefault(item_label, _Item(label=item_label))
        item.images[_classify_kind(p.name)] = p
    return [groups[k] for k in sorted(groups)]


def _rel(target: Path, start_dir: Path) -> str:
    """Relative POSIX link from ``start_dir`` to ``target`` (forward slashes, browser-safe)."""
    return Path(os.path.relpath(target, start_dir)).as_posix()


def _render_html(groups: list[_Group], out_html: Path, title: str) -> str:
    start = out_html.parent
    esc = html.escape
    n_items = sum(len(g.items) for g in groups)
    n_imgs = sum(len(i.images) for g in groups for i in g.items.values())
    parts: list[str] = [
        "<!doctype html>",
        '<html lang="en"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{esc(title)}</title>",
        "<style>",
        "body{font-family:system-ui,Arial,sans-serif;margin:1rem;background:#111;color:#eee}",
        "h1{font-size:1.3rem}",
        "h2{font-size:1.1rem;border-bottom:1px solid #444;margin-top:2rem;padding-top:.4rem}",
        "h3{font-size:.9rem;color:#9cf;margin:.7rem 0 .2rem;font-family:monospace}",
        ".pair{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:1rem}",
        ".pair figure{margin:0;flex:1 1 360px;max-width:49%}",
        ".pair img{width:100%;height:auto;border:1px solid #333;background:#fff}",
        ".pair figcaption{font-size:.72rem;color:#aaa}",
        "nav{margin:.5rem 0}",
        "nav a{color:#9cf;margin-right:.7rem;font-size:.8rem}",
        ".summary{color:#aaa;font-size:.85rem}",
        "a{text-decoration:none}",
        "</style></head><body>",
        f"<h1>{esc(title)}</h1>",
        f'<p class="summary">{len(groups)} group(s) · {n_items} item(s) · {n_imgs} image(s)</p>',
        "<nav>"
        + " ".join(f'<a href="#{esc(g.label)}">{esc(g.label)}</a>' for g in groups)
        + "</nav>",
    ]
    for g in groups:
        parts.append(f'<h2 id="{esc(g.label)}">{esc(g.label)}</h2>')
        for item_label in sorted(g.items):
            item = g.items[item_label]
            parts.append(f"<h3>{esc(item.label)}</h3>")
            parts.append('<div class="pair">')
            for kind in _KIND_ORDER:
                if kind in item.images:
                    src = esc(_rel(item.images[kind], start))
                    parts.append(
                        f'<figure><a href="{src}"><img src="{src}" '
                        f'alt="{esc(item.label)} {kind}" loading="lazy"></a>'
                        f"<figcaption>{kind}</figcaption></figure>"
                    )
            parts.append("</div>")
    parts.append("</body></html>")
    return "\n".join(parts)


def build_gallery(
    root: Path | str,
    out_html: Path | str | None = None,
    title: str | None = None,
) -> Path:
    """Write a static ``index.html`` gallery for the PNGs under ``root``.

    Parameters
    ----------
    root:
        Directory of generated PNGs (under ``experiments/review/**``).
    out_html:
        Output HTML path. Defaults to ``<root>/index.html`` (gitignored, do not commit).
    title:
        Gallery title. Defaults to ``"Artifact gallery — <root name>"``.

    Returns the path to the written HTML file.
    """
    root = Path(root)
    if not root.exists():
        raise FileNotFoundError(f"Gallery root does not exist: {root}")
    groups = _scan(root)
    out = Path(out_html) if out_html else root / "index.html"
    title = title or f"Artifact gallery — {root.name}"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_render_html(groups, out, title), encoding="utf-8")
    return out


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Build a static HTML gallery for review PNG artifacts (stdlib-only)."
    )
    p.add_argument(
        "--root",
        required=True,
        help="Directory of generated PNGs under experiments/review/** (map or zoom output)",
    )
    p.add_argument("--out", default=None, help="Output HTML path (default: <root>/index.html)")
    p.add_argument("--title", default=None, help="Gallery title")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    out_path = build_gallery(args.root, out_html=args.out, title=args.title)
    print(f"gallery written: {out_path}")

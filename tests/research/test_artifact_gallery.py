"""Tests for artifact_gallery — static HTML gallery, stdlib-only, no artifacts committed."""

from __future__ import annotations

import inspect
from pathlib import Path

import pytest

import fibengine.research.artifact_gallery as mod
from fibengine.research.artifact_gallery import build_gallery


def _png(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"\x89PNG\r\n\x1a\n")  # content irrelevant; gallery only links to it


def test_zoom_layout_groups_by_scope_and_pairs(tmp_path):
    root = tmp_path / "fourh_source_fib_zoom"
    fib = "fib_BTC-USD_4h_20171228T200000"
    _png(root / "2017_h2" / fib / "4h_clean.png")
    _png(root / "2017_h2" / fib / "4h_levels.png")

    out = build_gallery(root)

    assert out == root / "index.html" and out.exists()
    text = out.read_text(encoding="utf-8")
    assert 'id="2017_h2"' in text  # grouped by scope
    assert fib in text  # fib_id shown
    assert f'src="2017_h2/{fib}/4h_clean.png"' in text  # relative link, clean
    assert f'src="2017_h2/{fib}/4h_levels.png"' in text  # relative link, levels
    assert ">clean<" in text and ">levels<" in text  # both kinds captioned


def test_map_layout_groups_and_pairs(tmp_path):
    root = tmp_path / "fourh_source_fib_map"
    _png(root / "fourh_source_fib_map_2018_4h_clean.png")
    _png(root / "fourh_source_fib_map_2018_4h_levels.png")

    out = build_gallery(root)
    text = out.read_text(encoding="utf-8")

    assert "fourh_source_fib_map_2018" in text  # item label = stem before _4h_
    assert 'src="fourh_source_fib_map_2018_4h_clean.png"' in text
    assert 'src="fourh_source_fib_map_2018_4h_levels.png"' in text


def test_relative_links_only_no_absolute_or_external(tmp_path):
    root = tmp_path / "z"
    _png(root / "s" / "f" / "4h_clean.png")

    text = build_gallery(root).read_text(encoding="utf-8")

    assert "file://" not in text
    assert "http://" not in text and "https://" not in text
    assert str(tmp_path) not in text  # no absolute path leakage into links


def test_empty_dir_raises_clearly(tmp_path):
    root = tmp_path / "empty"
    root.mkdir()
    with pytest.raises(FileNotFoundError, match="No .png artifacts"):
        build_gallery(root)


def test_missing_root_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="does not exist"):
        build_gallery(tmp_path / "nope")


def test_output_lands_beside_artifacts(tmp_path):
    root = tmp_path / "r"
    _png(root / "s" / "f" / "4h_clean.png")
    out = build_gallery(root)
    assert out.parent == root  # default index.html under the given root (gitignored tree)


def test_no_external_deps_imported():
    src = inspect.getsource(mod)
    for forbidden in (
        "import pandas",
        "import numpy",
        "import matplotlib",
        "import mplfinance",
        "import pydantic",
    ):
        assert forbidden not in src


def test_existing_markdown_index_untouched(tmp_path):
    root = tmp_path / "fourh_source_fib_map"
    _png(root / "fourh_source_fib_map_2018_4h_clean.png")
    md = root / "fourh_source_fib_map_index.md"
    md.write_text("ORIGINAL MARKDOWN INDEX", encoding="utf-8")

    build_gallery(root)

    assert md.read_text(encoding="utf-8") == "ORIGINAL MARKDOWN INDEX"


def test_single_kind_item_renders_without_pair(tmp_path):
    root = tmp_path / "z"
    _png(root / "s" / "f" / "4h_clean.png")  # only clean, no levels
    text = build_gallery(root).read_text(encoding="utf-8")
    assert ">clean<" in text and ">levels<" not in text

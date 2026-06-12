"""
test_fodg_write_reload_roundtrip.py -- FODG write and reload roundtrip tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-19
Tests that FODG mutations (add_page, rename_page, remove_page, create_fodg)
persist after write_fodg + reload.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    load,
    create_fodg,
    write_fodg,
    add_page,
    rename_page,
    remove_page,
    page_names,
    get_page_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodg"


def test_add_page_persists_after_write_reload(tmp_path):
    m = load(str(_SAMPLES / "minimal-drawing.fodg"))
    m2 = add_page(m, "NewPage")
    dest = tmp_path / "out.fodg"
    write_fodg(m2, str(dest))
    m3 = load(str(dest))
    assert "NewPage" in page_names(m3)


def test_rename_page_persists_after_write_reload(tmp_path):
    m = create_fodg([{"name": "OriginalPage"}])
    m2 = rename_page(m, 0, "RenamedPage")
    dest = tmp_path / "renamed.fodg"
    write_fodg(m2, str(dest))
    m3 = load(str(dest))
    assert "RenamedPage" in page_names(m3)
    assert "OriginalPage" not in page_names(m3)


def test_remove_page_persists_after_write_reload(tmp_path):
    m = create_fodg([{"name": "PageA"}, {"name": "PageB"}])
    m2 = remove_page(m, 1)
    dest = tmp_path / "removed.fodg"
    write_fodg(m2, str(dest))
    m3 = load(str(dest))
    assert get_page_count(m3) == 1
    assert "PageA" in page_names(m3)
    assert "PageB" not in page_names(m3)


def test_create_fodg_write_reload_page_count(tmp_path):
    m = create_fodg([{"name": "P1"}, {"name": "P2"}, {"name": "P3"}])
    dest = tmp_path / "three_pages.fodg"
    write_fodg(m, str(dest))
    m2 = load(str(dest))
    assert get_page_count(m2) == 3


def test_create_fodg_write_reload_page_names(tmp_path):
    m = create_fodg([{"name": "Alpha"}, {"name": "Beta"}])
    dest = tmp_path / "named_pages.fodg"
    write_fodg(m, str(dest))
    m2 = load(str(dest))
    names = page_names(m2)
    assert "Alpha" in names
    assert "Beta" in names


def test_add_page_with_text_write_reload(tmp_path):
    m = create_fodg([{"name": "Cover"}])
    m2 = add_page(m, {"name": "Content", "texts": ["Hello World"]})
    dest = tmp_path / "with_text.fodg"
    write_fodg(m2, str(dest))
    m3 = load(str(dest))
    assert "Content" in page_names(m3)
    assert get_page_count(m3) == 2

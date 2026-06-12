"""
test_fodg_metadata_shape_pipeline.py -- FODG metadata + shape count pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-52
Tests get_page_metadata list with name keys, count_shapes int,
export_to_txt is string, get_shape_count int from file, page_names list.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    write_fodg,
    get_page_metadata,
    count_shapes,
    export_to_txt,
    get_shape_count,
    page_names,
)

_PAGES = [
    {"name": "Slide1"},
    {"name": "Slide2"},
    {"name": "Slide3"},
]
_MODEL = create_fodg(_PAGES)


def _write_fodg(tmp_path):
    dest = tmp_path / "doc.fodg"
    write_fodg(_MODEL, str(dest))
    return dest


def test_get_page_metadata_list(tmp_path):
    dest = _write_fodg(tmp_path)
    meta = get_page_metadata(str(dest))
    assert isinstance(meta, list)
    assert len(meta) == 3


def test_get_page_metadata_has_name(tmp_path):
    dest = _write_fodg(tmp_path)
    meta = get_page_metadata(str(dest))
    assert "name" in meta[0]
    assert meta[0]["name"] == "Slide1"


def test_count_shapes_is_int():
    count = count_shapes(_MODEL)
    assert isinstance(count, int)


def test_export_to_txt_is_string(tmp_path):
    dest = _write_fodg(tmp_path)
    txt = export_to_txt(str(dest))
    assert isinstance(txt, str)


def test_page_names_list():
    names = page_names(_MODEL)
    assert isinstance(names, list)
    assert "Slide1" in names
    assert "Slide3" in names

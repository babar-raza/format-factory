"""
test_fodg_shapes_pipeline.py -- FODG shapes pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-61
Tests get_shapes returns list, count_shapes int, get_text_shapes list,
get_page_count, page_names list.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    write_fodg,
    get_shapes,
    count_shapes,
    get_text_shapes,
    get_page_count,
    page_names,
)

_PAGES = [{"name": "Slide1"}, {"name": "Slide2"}, {"name": "Slide3"}]
_MODEL = create_fodg(_PAGES)


def _write(tmp_path):
    dest = tmp_path / "doc.fodg"
    write_fodg(_MODEL, str(dest))
    return dest


def test_get_shapes_returns_list(tmp_path):
    dest = _write(tmp_path)
    result = get_shapes(str(dest))
    assert isinstance(result, list)


def test_count_shapes_int():
    result = count_shapes(_MODEL)
    assert isinstance(result, int)


def test_get_text_shapes_list():
    result = get_text_shapes(_MODEL)
    assert isinstance(result, list)


def test_get_page_count():
    count = get_page_count(_MODEL)
    assert count == 3


def test_page_names_list():
    names = page_names(_MODEL)
    assert isinstance(names, list)
    assert "Slide1" in names

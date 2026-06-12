"""
test_fodg_shape_count_pipeline.py -- FODG shape count pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-73
Tests get_shape_count int, count_shapes int, get_text_shapes list,
get_page_metadata list, export_to_txt string.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    create_fodg,
    write_fodg,
    get_shape_count,
    count_shapes,
    get_text_shapes,
    get_page_metadata,
    export_to_txt,
)


def _make_file(tmp_path):
    model = create_fodg([
        {"name": "Slide1"},
        {"name": "Slide2"},
        {"name": "Slide3"},
    ])
    dest = tmp_path / "doc.fodg"
    write_fodg(model, str(dest))
    return dest, model


def test_get_shape_count_int(tmp_path):
    dest, _ = _make_file(tmp_path)
    result = get_shape_count(str(dest))
    assert isinstance(result, int)


def test_count_shapes_int(tmp_path):
    _, model = _make_file(tmp_path)
    result = count_shapes(model)
    assert isinstance(result, int)


def test_get_text_shapes_list(tmp_path):
    _, model = _make_file(tmp_path)
    result = get_text_shapes(model)
    assert isinstance(result, list)


def test_get_page_metadata_list(tmp_path):
    dest, _ = _make_file(tmp_path)
    result = get_page_metadata(str(dest))
    assert isinstance(result, list)
    assert len(result) == 3


def test_export_to_txt_string(tmp_path):
    dest, _ = _make_file(tmp_path)
    result = export_to_txt(str(dest))
    assert isinstance(result, str)

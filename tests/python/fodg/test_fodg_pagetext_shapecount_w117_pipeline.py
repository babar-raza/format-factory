"""
test_fodg_pagetext_shapecount_w117_pipeline.py -- FODG get_page_text + get_shape_count pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-117
Tests get_shape_count returns int, shape count positive, get_page_text returns list,
page text has content, page text and shape count consistent.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    load,
    get_shape_count,
    get_page_text,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodg"
_FODG = _SAMPLES / "minimal-drawing.fodg"


def test_get_shape_count_returns_int():
    result = get_shape_count(_FODG)
    assert isinstance(result, int)


def test_get_shape_count_positive():
    result = get_shape_count(_FODG)
    assert result >= 1


def test_get_page_text_returns_list():
    model = load(_FODG)
    result = get_page_text(model, 0)
    assert isinstance(result, list)


def test_get_page_text_has_content():
    model = load(_FODG)
    result = get_page_text(model, 0)
    assert len(result) >= 1


def test_page_text_nonempty_when_shapes_present():
    model = load(_FODG)
    shape_count = get_shape_count(_FODG)
    page_text = get_page_text(model, 0)
    assert shape_count >= 1 and len(page_text) >= 1

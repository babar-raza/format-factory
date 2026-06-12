"""
test_fodg_shapes_count_pipeline.py -- FODG get_shapes + count_shapes pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-100
Tests count_shapes int, count=2 for model with texts, get_shapes returns list,
count_shapes=0 for empty model, add_page then count_shapes increases.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    create_fodg,
    write_fodg,
    get_shapes,
    count_shapes,
    add_page,
)


def _make_model_with_shapes():
    return create_fodg([
        {"name": "Slide1", "texts": ["Hello", "World"]},
        {"name": "Slide2", "texts": ["Foo"]},
    ])


def test_count_shapes_returns_int():
    model = _make_model_with_shapes()
    assert isinstance(count_shapes(model), int)


def test_count_shapes_correct_value():
    model = _make_model_with_shapes()
    assert count_shapes(model) == 3


def test_count_shapes_empty_model():
    model = create_fodg([{"name": "Empty"}])
    assert count_shapes(model) == 0


def test_get_shapes_returns_list(tmp_path):
    model = _make_model_with_shapes()
    dest = tmp_path / "doc.fodg"
    write_fodg(model, str(dest))
    shapes = get_shapes(str(dest))
    assert isinstance(shapes, list)


def test_add_page_increases_shapes_total():
    model = _make_model_with_shapes()
    before = count_shapes(model)
    new_model = add_page(model, {"name": "Slide3", "texts": ["New"]})
    assert count_shapes(new_model) == before + 1

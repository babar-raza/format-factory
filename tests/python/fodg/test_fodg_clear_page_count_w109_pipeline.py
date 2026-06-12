"""
test_fodg_clear_page_count_w109_pipeline.py -- FODG clear_page + get_page_count pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-109
Tests get_page_count returns int, count=2, clear_page returns dict,
cleared page has no shapes, count unchanged after clear.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    clear_page,
    get_page_count,
)


def _make_model():
    model = create_fodg([
        {"name": "Slide1", "shapes": [{"type": "text", "content": "Hello"}]},
        {"name": "Slide2", "shapes": [{"type": "text", "content": "World"}]},
    ])
    return model


def test_get_page_count_returns_int():
    model = _make_model()
    assert isinstance(get_page_count(model), int)


def test_get_page_count_correct():
    model = _make_model()
    assert get_page_count(model) == 2


def test_clear_page_returns_dict():
    model = _make_model()
    result = clear_page(model, 0)
    assert isinstance(result, dict)


def test_cleared_page_has_no_shapes():
    model = _make_model()
    result = clear_page(model, 0)
    assert result["pages"][0]["shapes"] == []


def test_page_count_unchanged_after_clear():
    model = _make_model()
    result = clear_page(model, 0)
    assert get_page_count(result) == 2

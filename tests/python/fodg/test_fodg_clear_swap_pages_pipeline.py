"""
test_fodg_clear_swap_pages_pipeline.py -- FODG clear_page + swap_pages pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-88
Tests clear_page returns model, clear_page removes shapes, swap_pages swaps order,
swap_pages returns model, page count unchanged after swap.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    create_fodg,
    clear_page,
    swap_pages,
    get_page_count,
    page_names,
)

_PAGES = [
    {"name": "Alpha", "shapes": [{"type": "text", "text": "A1"}, {"type": "text", "text": "A2"}]},
    {"name": "Beta", "shapes": [{"type": "text", "text": "B1"}]},
    {"name": "Gamma", "shapes": [{"type": "text", "text": "C1"}]},
]


def test_clear_page_returns_model(tmp_path):
    model = create_fodg(_PAGES)
    result = clear_page(model, 0)
    assert isinstance(result, dict)


def test_clear_page_removes_shapes(tmp_path):
    model = create_fodg(_PAGES)
    model = clear_page(model, 0)
    page = model["pages"][0]
    shapes = page.get("shapes", [])
    assert len(shapes) == 0


def test_swap_pages_swaps_order(tmp_path):
    model = create_fodg(_PAGES)
    orig_first = page_names(model)[0]
    orig_second = page_names(model)[1]
    model = swap_pages(model, 0, 1)
    names = page_names(model)
    assert names[0] == orig_second
    assert names[1] == orig_first


def test_swap_pages_returns_model(tmp_path):
    model = create_fodg(_PAGES)
    result = swap_pages(model, 0, 2)
    assert isinstance(result, dict)


def test_page_count_unchanged_after_swap(tmp_path):
    model = create_fodg(_PAGES)
    before = get_page_count(model)
    model = swap_pages(model, 0, 1)
    assert get_page_count(model) == before

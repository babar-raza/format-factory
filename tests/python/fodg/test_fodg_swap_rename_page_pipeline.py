"""
test_fodg_swap_rename_page_pipeline.py -- FODG swap_pages + rename_page pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-106
Tests swap_pages returns model, swaps page order, rename_page changes name,
count unchanged after swap, count unchanged after rename.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    create_fodg,
    swap_pages,
    rename_page,
)


def _make_model():
    return create_fodg([
        {"name": "First"},
        {"name": "Second"},
        {"name": "Third"},
    ])


def test_swap_pages_returns_model():
    model = _make_model()
    new_model = swap_pages(model, 0, 2)
    assert isinstance(new_model, dict)


def test_swap_pages_changes_order():
    model = _make_model()
    new_model = swap_pages(model, 0, 2)
    names = [p["name"] for p in new_model["pages"]]
    assert names[0] == "Third"
    assert names[2] == "First"


def test_swap_pages_count_unchanged():
    model = _make_model()
    before = model["page_count"]
    new_model = swap_pages(model, 0, 1)
    assert new_model["page_count"] == before


def test_rename_page_changes_name():
    model = _make_model()
    new_model = rename_page(model, 1, "Renamed")
    names = [p["name"] for p in new_model["pages"]]
    assert "Renamed" in names
    assert "Second" not in names


def test_rename_page_count_unchanged():
    model = _make_model()
    before = model["page_count"]
    new_model = rename_page(model, 0, "NewFirst")
    assert new_model["page_count"] == before

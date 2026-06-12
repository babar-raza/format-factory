"""
test_fodg_page_ops_pipeline.py -- FODG page operations pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-55
Tests add_page increases count, remove_page decreases count, rename_page changes name,
duplicate_page, swap_pages.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    add_page,
    remove_page,
    rename_page,
    duplicate_page,
    swap_pages,
    get_page_count,
    page_names,
)

_PAGES = [{"name": "Page1"}, {"name": "Page2"}]


def test_add_page_increases_count():
    model = create_fodg(_PAGES)
    model = add_page(model, {"name": "Page3"})
    assert get_page_count(model) == 3


def test_remove_page_decreases_count():
    model = create_fodg(_PAGES)
    model = remove_page(model, 0)
    assert get_page_count(model) == 1


def test_rename_page_changes_name():
    model = create_fodg(_PAGES)
    model = rename_page(model, 0, "Renamed")
    names = page_names(model)
    assert "Renamed" in names


def test_duplicate_page_increases_count():
    model = create_fodg(_PAGES)
    model = duplicate_page(model, 0)
    assert get_page_count(model) == 3


def test_swap_pages_changes_order():
    model = create_fodg(_PAGES)
    model = swap_pages(model, 0, 1)
    names = page_names(model)
    assert names[0] == "Page2"
    assert names[1] == "Page1"

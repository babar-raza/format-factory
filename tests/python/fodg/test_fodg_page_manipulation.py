"""
test_fodg_page_manipulation.py -- FODG page manipulation pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-32
Tests duplicate_page (count increases), swap_pages (names swap),
get_page_by_name, get_page_index, has_page on created FODG models.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import (
    create_fodg,
    duplicate_page,
    swap_pages,
    get_page_by_name,
    get_page_index,
    has_page,
    get_page_count,
    page_names,
)

_MODEL = create_fodg([{"name": "Alpha"}, {"name": "Beta"}, {"name": "Gamma"}])


def test_duplicate_page_increases_count():
    m2 = duplicate_page(_MODEL, 0)
    assert get_page_count(m2) == 4


def test_swap_pages_changes_order():
    m2 = swap_pages(_MODEL, 0, 2)
    names = page_names(m2)
    assert names[0] == "Gamma"
    assert names[2] == "Alpha"


def test_get_page_by_name_found():
    page = get_page_by_name(_MODEL, "Beta")
    assert page is not None
    assert page["name"] == "Beta"


def test_get_page_index():
    idx = get_page_index(_MODEL, "Gamma")
    assert idx == 2


def test_has_page_true_and_false():
    assert has_page(_MODEL, "Alpha") is True
    assert has_page(_MODEL, "Nonexistent") is False

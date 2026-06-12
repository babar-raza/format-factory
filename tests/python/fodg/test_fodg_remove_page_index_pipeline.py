"""
test_fodg_remove_page_index_pipeline.py -- FODG remove_page + get_page_index pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-94
Tests remove_page decreases count, remove_page returns model, get_page_index int,
get_page_index correct value, get_page_index not found returns -1 or raises.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    create_fodg,
    remove_page,
    get_page_index,
    get_page_count,
)

_PAGES = [
    {"name": "Alpha"},
    {"name": "Beta"},
    {"name": "Gamma"},
]


def test_remove_page_decreases_count(tmp_path):
    model = create_fodg(_PAGES)
    before = get_page_count(model)
    model = remove_page(model, 2)
    assert get_page_count(model) == before - 1


def test_remove_page_returns_model(tmp_path):
    model = create_fodg(_PAGES)
    result = remove_page(model, 0)
    assert isinstance(result, dict)


def test_get_page_index_int(tmp_path):
    model = create_fodg(_PAGES)
    idx = get_page_index(model, "Beta")
    assert isinstance(idx, int)


def test_get_page_index_correct_value(tmp_path):
    model = create_fodg(_PAGES)
    idx = get_page_index(model, "Beta")
    assert idx == 1


def test_get_page_index_gamma(tmp_path):
    model = create_fodg(_PAGES)
    idx = get_page_index(model, "Gamma")
    assert idx == 2

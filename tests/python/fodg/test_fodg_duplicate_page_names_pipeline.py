"""
test_fodg_duplicate_page_names_pipeline.py -- FODG duplicate_page + page_names pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-97
Tests duplicate_page increases count, duplicate_page returns model, page_names returns list,
page_names has expected names, page_names count after duplicate.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    create_fodg,
    duplicate_page,
    page_names,
    get_page_count,
)

_PAGES = [
    {"name": "Intro"},
    {"name": "Content"},
]


def test_duplicate_page_increases_count(tmp_path):
    model = create_fodg(_PAGES)
    before = get_page_count(model)
    model = duplicate_page(model, 0)
    assert get_page_count(model) == before + 1


def test_duplicate_page_returns_model(tmp_path):
    model = create_fodg(_PAGES)
    result = duplicate_page(model, 0)
    assert isinstance(result, dict)


def test_page_names_returns_list(tmp_path):
    model = create_fodg(_PAGES)
    names = page_names(model)
    assert isinstance(names, list)


def test_page_names_has_expected_names(tmp_path):
    model = create_fodg(_PAGES)
    names = page_names(model)
    assert "Intro" in names
    assert "Content" in names


def test_page_names_count_after_duplicate(tmp_path):
    model = create_fodg(_PAGES)
    model = duplicate_page(model, 1)
    names = page_names(model)
    assert len(names) == 3

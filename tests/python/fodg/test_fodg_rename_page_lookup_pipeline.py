"""
test_fodg_rename_page_lookup_pipeline.py -- FODG rename_page + get_page_by_name pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-85
Tests rename_page changes name, get_page_by_name returns dict,
get_page_by_name not found None, rename_page returns model, page count unchanged.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import (
    create_fodg,
    rename_page,
    get_page_by_name,
    get_page_count,
    page_names,
)

_PAGES = [
    {"name": "PageOne", "shapes": [{"type": "text", "text": "A"}]},
    {"name": "PageTwo", "shapes": [{"type": "text", "text": "B"}]},
]


def test_rename_page_changes_name(tmp_path):
    model = create_fodg(_PAGES)
    model = rename_page(model, 0, "RenamedPage")
    names = page_names(model)
    assert "RenamedPage" in names
    assert "PageOne" not in names


def test_get_page_by_name_returns_dict(tmp_path):
    model = create_fodg(_PAGES)
    page = get_page_by_name(model, "PageTwo")
    assert isinstance(page, dict)


def test_get_page_by_name_not_found_none(tmp_path):
    model = create_fodg(_PAGES)
    result = get_page_by_name(model, "NoSuchPage")
    assert result is None


def test_rename_page_returns_model(tmp_path):
    model = create_fodg(_PAGES)
    result = rename_page(model, 1, "NewName")
    assert isinstance(result, dict)


def test_page_count_unchanged_after_rename(tmp_path):
    model = create_fodg(_PAGES)
    before = get_page_count(model)
    model = rename_page(model, 0, "Other")
    assert get_page_count(model) == before

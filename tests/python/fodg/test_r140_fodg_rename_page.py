"""Tests for fodg_codec.rename_page() — Sprint 6, R140."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import FodgError, add_page, create_fodg, rename_page


def _make_model_with_pages(count: int) -> dict:
    model = create_fodg([])
    for i in range(count):
        model = add_page(model, {"name": f"Page{i+1}", "texts": [f"text{i+1}"]})
    return model


def test_rename_first_page():
    model = _make_model_with_pages(2)
    result = rename_page(model, 0, "NewName")
    assert result["pages"][0]["name"] == "NewName"


def test_rename_last_page():
    model = _make_model_with_pages(3)
    result = rename_page(model, 2, "Last")
    assert result["pages"][2]["name"] == "Last"


def test_rename_does_not_affect_others():
    model = _make_model_with_pages(3)
    result = rename_page(model, 1, "Middle")
    assert result["pages"][0]["name"] == "Page1"
    assert result["pages"][2]["name"] == "Page3"


def test_rename_does_not_mutate():
    model = _make_model_with_pages(2)
    original_name = model["pages"][0]["name"]
    rename_page(model, 0, "NewName")
    assert model["pages"][0]["name"] == original_name


def test_rename_out_of_range_raises():
    model = _make_model_with_pages(2)
    try:
        rename_page(model, 5, "x")
        assert False, "Expected FodgError"
    except FodgError:
        pass


def test_rename_negative_index_raises():
    model = _make_model_with_pages(2)
    try:
        rename_page(model, -1, "x")
        assert False, "Expected FodgError"
    except FodgError:
        pass


def test_rename_type_error_model():
    try:
        rename_page("not a dict", 0, "name")
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_rename_type_error_name():
    model = _make_model_with_pages(1)
    try:
        rename_page(model, 0, 123)
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_rename_preserves_page_count():
    model = _make_model_with_pages(3)
    result = rename_page(model, 0, "New")
    assert result["page_count"] == 3

"""Tests for fodg_codec.remove_page() — Sprint 6, R140."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import FodgError, add_page, create_fodg, remove_page


def _make_model_with_pages(count: int) -> dict:
    model = create_fodg([])
    for i in range(count):
        model = add_page(model, {"name": f"Page{i+1}", "texts": [f"text{i+1}"]})
    return model


def test_remove_first_page():
    model = _make_model_with_pages(3)
    result = remove_page(model, 0)
    assert result["page_count"] == 2
    assert result["pages"][0]["name"] == "Page2"


def test_remove_last_page():
    model = _make_model_with_pages(3)
    result = remove_page(model, 2)
    assert result["page_count"] == 2
    assert result["pages"][-1]["name"] == "Page2"


def test_remove_middle_page():
    model = _make_model_with_pages(3)
    result = remove_page(model, 1)
    assert result["page_count"] == 2
    assert result["pages"][0]["name"] == "Page1"
    assert result["pages"][1]["name"] == "Page3"


def test_remove_does_not_mutate():
    model = _make_model_with_pages(2)
    original_count = model["page_count"]
    remove_page(model, 0)
    assert model["page_count"] == original_count


def test_remove_out_of_range_raises():
    model = _make_model_with_pages(2)
    try:
        remove_page(model, 5)
        assert False, "Expected FodgError"
    except FodgError:
        pass


def test_remove_negative_index_raises():
    model = _make_model_with_pages(2)
    try:
        remove_page(model, -1)
        assert False, "Expected FodgError"
    except FodgError:
        pass


def test_remove_type_error():
    try:
        remove_page("not a dict", 0)
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_remove_empty_pages_raises():
    model = create_fodg([])
    try:
        remove_page(model, 0)
        assert False, "Expected FodgError"
    except FodgError:
        pass


def test_shapes_total_updated():
    model = _make_model_with_pages(3)
    before_total = model.get("shapes_total", 0)
    result = remove_page(model, 0)
    assert result.get("shapes_total", 0) <= before_total

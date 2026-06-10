"""Tests for get_page_by_name() — FODG page lookup by name.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-4-001
TC-PRODUCT-FODG-GET-PAGE-BY-NAME
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import create_fodg, get_page_by_name


class TestGetPageByName:
    def test_returns_correct_page(self):
        model = create_fodg([{"name": "Page1"}, {"name": "Page2"}])
        page = get_page_by_name(model, "Page2")
        assert page is not None
        assert page["name"] == "Page2"

    def test_returns_first_page(self):
        model = create_fodg([{"name": "Page1"}, {"name": "Page2"}])
        page = get_page_by_name(model, "Page1")
        assert page is not None
        assert page["name"] == "Page1"

    def test_returns_none_when_not_found(self):
        model = create_fodg([{"name": "Page1"}])
        page = get_page_by_name(model, "Nonexistent")
        assert page is None

    def test_empty_drawing_returns_none(self):
        model = create_fodg([])
        assert get_page_by_name(model, "Page1") is None

    def test_case_sensitive(self):
        model = create_fodg([{"name": "Drawing"}])
        assert get_page_by_name(model, "drawing") is None
        assert get_page_by_name(model, "DRAWING") is None
        assert get_page_by_name(model, "Drawing") is not None

    def test_page_has_text_content(self):
        model = create_fodg([{"name": "Slide1", "texts": ["Hello", "World"]}])
        page = get_page_by_name(model, "Slide1")
        assert page is not None
        assert "Hello" in page["text_content"]

    def test_type_error_on_non_dict_model(self):
        with pytest.raises(TypeError):
            get_page_by_name("not a dict", "Page1")

    def test_type_error_on_non_string_name(self):
        model = create_fodg([{"name": "Page1"}])
        with pytest.raises(TypeError):
            get_page_by_name(model, 0)

    def test_returns_dict(self):
        model = create_fodg([{"name": "P1"}])
        result = get_page_by_name(model, "P1")
        assert isinstance(result, dict)

    def test_shape_count_in_returned_page(self):
        model = create_fodg([{"name": "Chart", "texts": ["A", "B", "C"]}])
        page = get_page_by_name(model, "Chart")
        assert page["shape_count"] == 3

"""Tests for get_text_shapes() — FODG text shape extraction.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-5-001
TC-PRODUCT-FODG-TEXT-SHAPES
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import create_fodg, get_text_shapes


class TestGetTextShapes:
    def test_returns_pages_with_text(self):
        model = create_fodg([
            {"name": "Page1", "texts": ["Hello", "World"]},
            {"name": "Page2", "texts": []},
        ])
        result = get_text_shapes(model)
        assert len(result) == 1
        assert result[0]["page_name"] == "Page1"

    def test_text_content_present(self):
        model = create_fodg([{"name": "P1", "texts": ["Foo", "Bar"]}])
        result = get_text_shapes(model)
        assert result[0]["text_content"] == ["Foo", "Bar"]

    def test_empty_texts_excluded(self):
        model = create_fodg([{"name": "P1", "texts": []}])
        result = get_text_shapes(model)
        assert result == []

    def test_multiple_pages_all_with_text(self):
        model = create_fodg([
            {"name": "P1", "texts": ["a"]},
            {"name": "P2", "texts": ["b"]},
        ])
        result = get_text_shapes(model)
        assert len(result) == 2

    def test_page_index_set(self):
        model = create_fodg([
            {"name": "P1", "texts": []},
            {"name": "P2", "texts": ["text"]},
        ])
        result = get_text_shapes(model)
        assert result[0]["page_index"] == 1

    def test_empty_model_empty_result(self):
        model = create_fodg([])
        assert get_text_shapes(model) == []

    def test_type_error_on_non_dict(self):
        with pytest.raises(TypeError):
            get_text_shapes("not a dict")

    def test_returns_list(self):
        model = create_fodg([{"name": "P1", "texts": ["hello"]}])
        assert isinstance(get_text_shapes(model), list)

    def test_filters_empty_strings(self):
        model = {"is_fodg": True, "page_count": 1, "pages": [
            {"name": "P1", "text_content": ["", "real text"], "shape_count": 2}
        ], "shapes_total": 2}
        result = get_text_shapes(model)
        assert len(result) == 1
        assert result[0]["text_content"] == ["real text"]

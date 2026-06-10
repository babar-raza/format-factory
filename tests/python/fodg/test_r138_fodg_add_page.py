"""Tests for add_page() — FODG page addition.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-5-001
TC-PRODUCT-FODG-ADD-PAGE
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import add_page, create_fodg


class TestAddPage:
    def test_adds_one_page(self):
        model = create_fodg([{"name": "P1", "texts": ["a"]}])
        result = add_page(model, {"name": "P2", "texts": ["b"]})
        assert result["page_count"] == 2

    def test_new_page_at_end(self):
        model = create_fodg([{"name": "P1", "texts": []}])
        result = add_page(model, {"name": "P2", "texts": ["hello"]})
        assert result["pages"][-1]["name"] == "P2"

    def test_does_not_mutate_original(self):
        model = create_fodg([{"name": "P1", "texts": []}])
        add_page(model, {"name": "P2", "texts": []})
        assert model["page_count"] == 1

    def test_default_page_name(self):
        model = create_fodg([{"name": "P1", "texts": []}])
        result = add_page(model, {})
        assert result["pages"][-1]["name"] == "Page2"

    def test_text_content_set(self):
        model = create_fodg([])
        result = add_page(model, {"name": "P1", "texts": ["x", "y"]})
        assert result["pages"][0]["text_content"] == ["x", "y"]

    def test_shapes_total_updated(self):
        model = create_fodg([{"name": "P1", "texts": ["a", "b"]}])
        result = add_page(model, {"name": "P2", "texts": ["c"]})
        assert result["shapes_total"] == 3

    def test_empty_page_added(self):
        model = create_fodg([])
        result = add_page(model, {"name": "Empty"})
        assert result["page_count"] == 1
        assert result["pages"][0]["shape_count"] == 0

    def test_type_error_non_dict_model(self):
        with pytest.raises(TypeError):
            add_page("not a dict", {"name": "P1"})

    def test_type_error_non_dict_page(self):
        model = create_fodg([])
        with pytest.raises(TypeError):
            add_page(model, 12345)  # int is not str or dict

    def test_returns_dict(self):
        model = create_fodg([])
        assert isinstance(add_page(model, {}), dict)

    def test_multiple_additions(self):
        model = create_fodg([])
        model = add_page(model, {"name": "P1"})
        model = add_page(model, {"name": "P2"})
        model = add_page(model, {"name": "P3"})
        assert model["page_count"] == 3
        assert [p["name"] for p in model["pages"]] == ["P1", "P2", "P3"]

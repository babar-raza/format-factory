"""R170 — FODG find_shapes_by_text_pattern and export_page_to_json tests.

Sprint: FORMAT-FACTORY-PROOF-CLOSED-SELF-HEALING-PROFESSIONALIZE-PRODUCT-READINESS-RNEXT-001
"""
from __future__ import annotations

import json
import pytest

from src.python.fodg.fodg_codec import (
    create_fodg,
    find_shapes_by_text_pattern,
    export_page_to_json,
)


def _make_model() -> dict:
    return create_fodg([
        {"name": "Slide 1", "texts": ["Hello world", "Test pattern", "Another text"]},
        {"name": "Slide 2", "texts": ["Different content", "No match here"]},
    ])


class TestFindShapesByTextPattern:
    def test_finds_simple_pattern(self):
        model = _make_model()
        results = find_shapes_by_text_pattern(model, "Hello")
        assert len(results) == 1
        assert results[0]["text"] == "Hello world"

    def test_finds_multiple_matches(self):
        model = _make_model()
        results = find_shapes_by_text_pattern(model, r"(Hello|Another)")
        assert len(results) == 2

    def test_no_match_returns_empty_list(self):
        model = _make_model()
        results = find_shapes_by_text_pattern(model, "XYZ_NONEXISTENT_12345")
        assert results == []

    def test_result_has_required_keys(self):
        model = _make_model()
        results = find_shapes_by_text_pattern(model, "world")
        assert results
        r = results[0]
        assert "page_idx" in r
        assert "shape_idx" in r
        assert "text" in r
        assert "matched" in r

    def test_page_idx_correct(self):
        model = _make_model()
        results = find_shapes_by_text_pattern(model, "Different")
        assert len(results) == 1
        assert results[0]["page_idx"] == 1

    def test_invalid_regex_returns_empty(self):
        model = _make_model()
        results = find_shapes_by_text_pattern(model, "[invalid")
        assert results == []

    def test_non_dict_model_raises_type_error(self):
        with pytest.raises(TypeError):
            find_shapes_by_text_pattern("not a dict", "pattern")

    def test_function_in_all(self):
        from src.python.fodg import __all__ as fodg_all
        assert "find_shapes_by_text_pattern" in fodg_all


class TestExportPageToJson:
    def test_returns_string(self):
        model = _make_model()
        result = export_page_to_json(model, 0)
        assert isinstance(result, str)

    def test_returns_valid_json(self):
        model = _make_model()
        result = export_page_to_json(model, 0)
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_contains_page_name(self):
        model = _make_model()
        result = export_page_to_json(model, 0)
        parsed = json.loads(result)
        assert parsed.get("name") == "Slide 1"

    def test_second_page(self):
        model = _make_model()
        result = export_page_to_json(model, 1)
        parsed = json.loads(result)
        assert parsed.get("name") == "Slide 2"

    def test_out_of_range_returns_empty_json(self):
        model = _make_model()
        result = export_page_to_json(model, 99)
        assert result == "{}"

    def test_negative_idx_returns_empty_json(self):
        model = _make_model()
        result = export_page_to_json(model, -1)
        assert result == "{}"

    def test_non_dict_model_raises_type_error(self):
        with pytest.raises(TypeError):
            export_page_to_json("not a dict", 0)

    def test_function_in_all(self):
        from src.python.fodg import __all__ as fodg_all
        assert "export_page_to_json" in fodg_all

"""R169 — FODG get_page_text tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from src.python.fodg.fodg_codec import get_page_text, load, create_fodg


_SHAPES = Path("samples/by-format/fodg/shapes-basic.fodg")
_MINIMAL = Path("samples/by-format/fodg/minimal-drawing.fodg")


def _make_model_with_text(page_texts: list[list[str]]) -> dict:
    """Create a FODG model with pages that each have given text_content."""
    pages = [{"name": f"Page{i+1}", "texts": texts}
             for i, texts in enumerate(page_texts)]
    model = create_fodg(pages)
    return model


class TestGetPageTextBasic:
    def test_returns_list(self):
        model = _make_model_with_text([["hello", "world"]])
        result = get_page_text(model, 0)
        assert isinstance(result, list)

    def test_returns_correct_texts(self):
        model = _make_model_with_text([["foo", "bar", "baz"]])
        result = get_page_text(model, 0)
        assert result == ["foo", "bar", "baz"]

    def test_empty_strings_excluded(self):
        model = _make_model_with_text([["hello", "", "world"]])
        result = get_page_text(model, 0)
        assert "" not in result
        assert "hello" in result
        assert "world" in result

    def test_out_of_range_returns_empty(self):
        model = _make_model_with_text([["hello"]])
        result = get_page_text(model, 99)
        assert result == []

    def test_negative_index_returns_empty(self):
        model = _make_model_with_text([["hello"]])
        result = get_page_text(model, -1)
        assert result == []

    def test_empty_page_returns_empty(self):
        model = _make_model_with_text([[]])
        result = get_page_text(model, 0)
        assert result == []

    def test_second_page_text(self):
        model = _make_model_with_text([["page1"], ["page2a", "page2b"]])
        result = get_page_text(model, 1)
        assert result == ["page2a", "page2b"]

    def test_type_error_on_non_dict(self):
        with pytest.raises(TypeError):
            get_page_text("not a dict", 0)


class TestGetPageTextOnFile:
    def test_minimal_drawing_no_error(self):
        model = load(_MINIMAL)
        result = get_page_text(model, 0)
        assert isinstance(result, list)

    def test_shapes_basic_no_error(self):
        model = load(_SHAPES)
        result = get_page_text(model, 0)
        assert isinstance(result, list)

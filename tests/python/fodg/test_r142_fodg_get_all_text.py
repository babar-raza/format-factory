"""Tests for fodg_codec.get_all_text() — Sprint 7, R142."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import add_page, create_fodg, get_all_text


def test_empty_model_returns_empty():
    model = create_fodg([])
    assert get_all_text(model) == []


def test_single_page_single_text():
    model = create_fodg([])
    model = add_page(model, {"name": "P1", "texts": ["Hello"]})
    assert get_all_text(model) == ["Hello"]


def test_multiple_texts_per_page():
    model = create_fodg([])
    model = add_page(model, {"name": "P1", "texts": ["A", "B", "C"]})
    result = get_all_text(model)
    assert result == ["A", "B", "C"]


def test_multiple_pages():
    model = create_fodg([])
    model = add_page(model, {"name": "P1", "texts": ["Page1Text"]})
    model = add_page(model, {"name": "P2", "texts": ["Page2Text"]})
    result = get_all_text(model)
    assert "Page1Text" in result
    assert "Page2Text" in result


def test_empty_strings_skipped():
    model = create_fodg([])
    model = add_page(model, {"name": "P1", "texts": ["real", "", "also_real"]})
    result = get_all_text(model)
    assert "" not in result
    assert len(result) == 2


def test_type_error():
    try:
        get_all_text("not a dict")
        assert 1 == 0, "Expected TypeError"

    except TypeError:
        pass


def test_returns_list():
    model = create_fodg([])
    assert isinstance(get_all_text(model), list)


def test_page_with_no_texts():
    model = create_fodg([])
    model = add_page(model, {"name": "Empty", "texts": []})
    assert get_all_text(model) == []

"""Tests for fodg.fodg_codec.find_text() — PIGE Sprint."""
from __future__ import annotations

import sys
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from fodg.fodg_codec import find_text


def _make_doc_with_text():
    """Build a model dict directly with shapes containing text."""
    return {
        "pages": [
            {
                "name": "Cover",
                "shapes": [{"text": "Welcome to Format Factory"}],
            },
            {
                "name": "Details",
                "shapes": [
                    {"text": "Product overview"},
                    {"text": "Technical details and specs"},
                ],
            },
        ],
    }


def test_find_exact_match():
    model = _make_doc_with_text()
    results = find_text(model, "Welcome")
    assert len(results) == 1
    assert results[0]["page_name"] == "Cover"
    assert results[0]["page_index"] == 0


def test_find_across_pages():
    model = _make_doc_with_text()
    results = find_text(model, "details", case_sensitive=False)
    assert len(results) == 1
    assert results[0]["page_name"] == "Details"


def test_find_case_sensitive_no_match():
    model = _make_doc_with_text()
    results = find_text(model, "welcome")  # lowercase
    assert len(results) == 0


def test_find_case_insensitive_match():
    model = _make_doc_with_text()
    results = find_text(model, "welcome", case_sensitive=False)
    assert len(results) == 1


def test_find_no_match():
    model = _make_doc_with_text()
    results = find_text(model, "nonexistent")
    assert results == []


def test_find_in_empty_model():
    model = {"pages": []}
    results = find_text(model, "test")
    assert results == []


def test_result_has_required_keys():
    model = _make_doc_with_text()
    results = find_text(model, "Welcome")
    assert len(results) == 1
    r = results[0]
    for key in ("page_index", "page_name", "shape_index", "text"):
        assert key in r


def test_returns_list():
    model = _make_doc_with_text()
    assert isinstance(find_text(model, "anything"), list)


def test_available_from_package():
    from fodg import find_text as fn
    assert callable(fn)

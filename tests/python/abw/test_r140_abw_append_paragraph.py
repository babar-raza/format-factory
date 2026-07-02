"""Tests for abw.abw_codec.append_paragraph() — Sprint 6, R140."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import append_paragraph, create_abw


def test_append_increases_count():
    model = create_abw(["hello"])
    result = append_paragraph(model, "world")
    assert result["paragraph_count"] == 2


def test_append_adds_text():
    model = create_abw(["hello"])
    result = append_paragraph(model, "world")
    assert result["paragraphs"][-1] == "world"


def test_append_to_empty():
    model = create_abw([])
    result = append_paragraph(model, "first")
    assert result["paragraphs"] == ["first"]
    assert result["paragraph_count"] == 1


def test_append_does_not_mutate():
    model = create_abw(["a"])
    original_len = len(model["paragraphs"])
    append_paragraph(model, "b")
    assert len(model["paragraphs"]) == original_len


def test_append_preserves_is_abw():
    model = create_abw([])
    result = append_paragraph(model, "x")
    assert result["is_abw"] is True


def test_append_preserves_existing_paras():
    model = create_abw(["a", "b"])
    result = append_paragraph(model, "c")
    assert result["paragraphs"][:2] == ["a", "b"]


def test_append_empty_string():
    model = create_abw(["a"])
    result = append_paragraph(model, "")
    assert result["paragraphs"][-1] == ""


def test_append_type_error_model():
    try:
        append_paragraph("not a dict", "text")
        assert 1 == 0, "Expected TypeError"

    except TypeError:
        pass


def test_append_type_error_text():
    model = create_abw([])
    try:
        append_paragraph(model, 42)
        assert 1 == 0, "Expected TypeError"

    except TypeError:
        pass


def test_append_multiple():
    model = create_abw([])
    model = append_paragraph(model, "one")
    model = append_paragraph(model, "two")
    model = append_paragraph(model, "three")
    assert model["paragraph_count"] == 3
    assert model["paragraphs"] == ["one", "two", "three"]

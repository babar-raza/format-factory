"""Tests for abw.abw_codec.export_to_plain_text() — PIGE Sprint."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, append_paragraph, export_to_plain_text


def _make_doc(*paragraphs: str) -> dict:
    model = create_abw([])
    for p in paragraphs:
        model = append_paragraph(model, p)
    return model


def test_empty_document_returns_empty_string():
    model = create_abw([])
    assert export_to_plain_text(model) == ""


def test_single_paragraph():
    model = _make_doc("Hello world")
    assert export_to_plain_text(model) == "Hello world"


def test_two_paragraphs_joined_with_double_newline():
    model = _make_doc("First paragraph", "Second paragraph")
    result = export_to_plain_text(model)
    assert result == "First paragraph\n\nSecond paragraph"


def test_three_paragraphs():
    model = _make_doc("A", "B", "C")
    result = export_to_plain_text(model)
    assert result == "A\n\nB\n\nC"


def test_preserves_internal_whitespace():
    model = _make_doc("hello  world", "foo\tbar")
    result = export_to_plain_text(model)
    assert "hello  world" in result
    assert "foo\tbar" in result


def test_returns_string():
    model = _make_doc("test")
    assert isinstance(export_to_plain_text(model), str)


def test_non_dict_raises():
    with pytest.raises(TypeError):
        export_to_plain_text("not a dict")


def test_available_from_package():
    from abw import export_to_plain_text as fn
    assert callable(fn)

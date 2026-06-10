"""Tests for abw.abw_codec.has_paragraph() — Sprint 10, R148."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, has_paragraph


def test_exact_match_found():
    model = create_abw(["Hello world", "Goodbye"])
    assert has_paragraph(model, "Hello world") is True


def test_partial_match_not_found():
    model = create_abw(["Hello world"])
    assert has_paragraph(model, "Hello") is False


def test_not_found():
    model = create_abw(["Alpha", "Beta"])
    assert has_paragraph(model, "Gamma") is False


def test_empty_model():
    model = create_abw([])
    assert has_paragraph(model, "anything") is False


def test_returns_bool():
    model = create_abw(["text"])
    result = has_paragraph(model, "text")
    assert isinstance(result, bool)


def test_empty_string_paragraph():
    model = create_abw(["", "content"])
    assert has_paragraph(model, "") is True

"""Tests for abw.abw_codec.last_paragraph() — Sprint 11, R150."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, last_paragraph


def _model(paragraphs):
    m = create_abw([])
    return {**m, "paragraphs": paragraphs, "paragraph_count": len(paragraphs)}


def test_last_of_three():
    assert last_paragraph(_model(["Alpha", "Beta", "Gamma"])) == "Gamma"


def test_last_of_one():
    assert last_paragraph(_model(["Only"])) == "Only"


def test_empty_paragraphs_returns_empty_string():
    assert last_paragraph(_model([])) == ""


def test_does_not_mutate_model():
    m = _model(["A", "B"])
    last_paragraph(m)
    assert m["paragraphs"] == ["A", "B"]


def test_returns_string():
    result = last_paragraph(_model(["hello"]))
    assert isinstance(result, str)


def test_whitespace_paragraph():
    assert last_paragraph(_model(["other", "  "])) == "  "

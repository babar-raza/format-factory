"""Tests for abw.abw_codec.paragraph_at() — Sprint 12, R152."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from abw.abw_codec import create_abw, paragraph_at


def _model(paragraphs):
    m = create_abw([])
    return {**m, "paragraphs": paragraphs, "paragraph_count": len(paragraphs)}


def test_first_paragraph():
    assert paragraph_at(_model(["A", "B", "C"]), 0) == "A"


def test_last_paragraph_by_index():
    assert paragraph_at(_model(["A", "B", "C"]), 2) == "C"


def test_negative_index():
    assert paragraph_at(_model(["A", "B", "C"]), -1) == "C"


def test_out_of_range_raises_index_error():
    try:
        paragraph_at(_model(["A"]), 5)
        assert False, "Expected IndexError"
    except IndexError:
        pass


def test_returns_string():
    assert isinstance(paragraph_at(_model(["hello"]), 0), str)

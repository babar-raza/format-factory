"""
test_abw_longest_wrap_pipeline.py -- ABW longest_paragraph + word_wrap pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-75
Tests longest_paragraph returns string, is longest, word_wrap returns model,
has_paragraph true/false, paragraph_at index.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    create_abw,
    longest_paragraph,
    word_wrap,
    has_paragraph,
    paragraph_at,
)


_PARAGRAPHS = [
    "Short text",
    "This is a much longer paragraph with many more words in it",
    "Medium length paragraph here",
]


def test_longest_paragraph_returns_string():
    model = create_abw(_PARAGRAPHS)
    result = longest_paragraph(model)
    assert isinstance(result, str)


def test_longest_paragraph_is_longest():
    model = create_abw(_PARAGRAPHS)
    result = longest_paragraph(model)
    assert result == "This is a much longer paragraph with many more words in it"


def test_word_wrap_returns_model():
    model = create_abw(_PARAGRAPHS)
    result = word_wrap(model, width=20)
    assert isinstance(result, dict)
    assert "paragraphs" in result


def test_has_paragraph_true():
    model = create_abw(_PARAGRAPHS)
    assert has_paragraph(model, "Short text") is True


def test_paragraph_at_index():
    model = create_abw(_PARAGRAPHS)
    result = paragraph_at(model, 2)
    assert result == "Medium length paragraph here"

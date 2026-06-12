"""
test_abw_para_at_count_words_pipeline.py -- ABW get_paragraph_at + count_words pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-108
Tests get_paragraph_at returns string, first para has Hello, count_words returns int,
count=9 for 3 paragraphs of 3 words, count_words after append increases.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    create_abw,
    get_paragraph_at,
    count_words,
    append_paragraph,
)

_PARAGRAPHS = [
    "Hello World today",
    "Quick brown fox",
    "One two three",
]


def _make_model():
    return create_abw(_PARAGRAPHS)


def test_get_paragraph_at_returns_string():
    model = _make_model()
    para = get_paragraph_at(model, 0)
    assert isinstance(para, str)


def test_get_paragraph_at_correct_content():
    model = _make_model()
    para = get_paragraph_at(model, 0)
    assert "Hello" in para


def test_count_words_returns_int():
    model = _make_model()
    total = count_words(model)
    assert isinstance(total, int)


def test_count_words_correct_value():
    model = _make_model()
    total = count_words(model)
    assert total == 9


def test_count_words_increases_after_append():
    model = _make_model()
    before = count_words(model)
    new_model = append_paragraph(model, "Four five six seven")
    after = count_words(new_model)
    assert after == before + 4

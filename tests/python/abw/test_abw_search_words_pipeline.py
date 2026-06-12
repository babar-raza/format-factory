"""
test_abw_search_words_pipeline.py -- ABW search_text + get_words pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-96
Tests search_text returns list of indices, search_text finds correct paragraph,
get_words returns list, get_words has content, search_text empty for no match.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    create_abw,
    search_text,
    get_words,
)

_PARAGRAPHS = [
    "The quick brown fox jumps over the lazy dog.",
    "Python is a great programming language.",
    "Format factory processes many file formats efficiently.",
]


def test_search_text_returns_list(tmp_path):
    model = create_abw(_PARAGRAPHS)
    result = search_text(model, "Python")
    assert isinstance(result, list)


def test_search_text_finds_correct_paragraph(tmp_path):
    model = create_abw(_PARAGRAPHS)
    result = search_text(model, "Python")
    assert 1 in result


def test_get_words_returns_list(tmp_path):
    model = create_abw(_PARAGRAPHS)
    result = get_words(model, 0)
    assert isinstance(result, list)


def test_get_words_has_content(tmp_path):
    model = create_abw(_PARAGRAPHS)
    result = get_words(model, 0)
    assert len(result) > 0
    assert "fox" in result or "quick" in result


def test_search_text_empty_no_match(tmp_path):
    model = create_abw(_PARAGRAPHS)
    result = search_text(model, "xyzzy_notpresent_9999")
    assert result == []

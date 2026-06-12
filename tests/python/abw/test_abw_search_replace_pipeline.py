"""
test_abw_search_replace_pipeline.py -- ABW search replace pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-66
Tests search_paragraph finds match, search_replace modifies text, search_text returns indices,
get_words list, get_unique_words sorted.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    create_abw,
    search_paragraph,
    search_replace_paragraph,
    search_text,
    get_words,
    get_unique_words,
)

_MODEL = create_abw([
    "The quick brown fox",
    "jumps over the lazy dog",
    "The fox is quick",
])


def test_search_paragraph_finds_match():
    results = search_paragraph(_MODEL, "fox")
    assert isinstance(results, list)
    assert len(results) >= 1


def test_search_replace_modifies_text():
    model = search_replace_paragraph(_MODEL, "fox", "cat")
    results = search_paragraph(model, "cat")
    assert len(results) >= 1


def test_search_text_returns_indices():
    indices = search_text(_MODEL, "fox")
    assert isinstance(indices, list)
    assert 0 in indices


def test_get_words_list():
    words = get_words(_MODEL, 0)
    assert isinstance(words, list)
    assert "quick" in words


def test_get_unique_words_sorted():
    words = get_unique_words(_MODEL)
    assert words == sorted(words)
    assert "fox" in words

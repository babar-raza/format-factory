"""Tests for abw_codec.text_stats — mainstream-product-deepening-rnext3.

Covers: normal document, empty paragraphs list, single paragraph,
multi-paragraph, avg calculation, TypeError on non-dict input.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import text_stats


# ---------------------------------------------------------------------------
# Normal behavior
# ---------------------------------------------------------------------------

def test_text_stats_basic():
    model = {"paragraphs": ["Hello world", "Foo bar baz"]}
    result = text_stats(model)
    assert result["paragraph_count"] == 2
    assert result["word_count"] == 5
    assert result["char_count"] == 22
    assert result["avg_words_per_paragraph"] == 2.5


def test_text_stats_single_paragraph():
    model = {"paragraphs": ["One two three"]}
    result = text_stats(model)
    assert result["paragraph_count"] == 1
    assert result["word_count"] == 3
    assert result["char_count"] == 13
    assert result["avg_words_per_paragraph"] == 3.0


def test_text_stats_keys_present():
    model = {"paragraphs": ["a b"]}
    result = text_stats(model)
    assert set(result.keys()) == {
        "paragraph_count", "word_count", "char_count", "avg_words_per_paragraph"
    }


def test_text_stats_returns_dict():
    model = {"paragraphs": ["hello"]}
    assert isinstance(text_stats(model), dict)


# ---------------------------------------------------------------------------
# Boundary cases
# ---------------------------------------------------------------------------

def test_text_stats_empty_paragraphs():
    model = {"paragraphs": []}
    result = text_stats(model)
    assert result["paragraph_count"] == 0
    assert result["word_count"] == 0
    assert result["char_count"] == 0
    assert result["avg_words_per_paragraph"] == 0.0


def test_text_stats_missing_paragraphs_key():
    model = {}
    result = text_stats(model)
    assert result["paragraph_count"] == 0
    assert result["word_count"] == 0


def test_text_stats_empty_paragraph_string():
    model = {"paragraphs": [""]}
    result = text_stats(model)
    assert result["paragraph_count"] == 1
    assert result["word_count"] == 0
    assert result["char_count"] == 0
    assert result["avg_words_per_paragraph"] == 0.0


def test_text_stats_avg_precision():
    model = {"paragraphs": ["a b c", "d e"]}
    result = text_stats(model)
    assert result["avg_words_per_paragraph"] == 2.5


# ---------------------------------------------------------------------------
# Invalid input
# ---------------------------------------------------------------------------

def test_text_stats_non_dict_raises_type_error():
    with pytest.raises(TypeError):
        text_stats("not a dict")


def test_text_stats_list_raises_type_error():
    with pytest.raises(TypeError):
        text_stats(["paragraphs"])

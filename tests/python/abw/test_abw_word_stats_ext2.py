"""Tests for abw_word_stats extension functions (ext2 batch)."""
from __future__ import annotations

from pathlib import Path

from abw.abw_word_stats import (
    paragraph_count,
    total_char_count,
    most_frequent_word,
    avg_words_per_paragraph,
    nonempty_paragraph_count,
    max_word_length,
)
from abw.abw_codec import load

SAMPLES = Path("samples/by-format/abw")
MINIMAL = SAMPLES / "minimal-document.abw"
MULTI = SAMPLES / "two-paragraphs.abw"


def _model(path):
    return load(path)


# --- paragraph_count ---

def test_paragraph_count_returns_int():
    assert isinstance(paragraph_count(_model(MINIMAL)), int)


def test_paragraph_count_minimal_positive():
    assert paragraph_count(_model(MINIMAL)) >= 0


def test_paragraph_count_multi():
    assert paragraph_count(_model(MULTI)) >= 0


# --- total_char_count ---

def test_total_char_count_returns_int():
    assert isinstance(total_char_count(_model(MINIMAL)), int)


def test_total_char_count_nonneg():
    assert total_char_count(_model(MINIMAL)) >= 0


# --- most_frequent_word ---

def test_most_frequent_word_returns_str():
    assert isinstance(most_frequent_word(_model(MINIMAL)), str)


def test_most_frequent_word_empty_dict():
    assert most_frequent_word({}) == ""


# --- avg_words_per_paragraph ---

def test_avg_words_per_paragraph_returns_float():
    assert isinstance(avg_words_per_paragraph(_model(MINIMAL)), float)


def test_avg_words_per_paragraph_nonneg():
    assert avg_words_per_paragraph(_model(MINIMAL)) >= 0.0


def test_avg_words_per_paragraph_empty_dict():
    assert avg_words_per_paragraph({}) == 0.0


# --- nonempty_paragraph_count ---

def test_nonempty_paragraph_count_returns_int():
    assert isinstance(nonempty_paragraph_count(_model(MINIMAL)), int)


def test_nonempty_paragraph_count_leq_total():
    model = _model(MINIMAL)
    assert nonempty_paragraph_count(model) <= paragraph_count(model)


# --- max_word_length ---

def test_max_word_length_returns_int():
    assert isinstance(max_word_length(_model(MINIMAL)), int)


def test_max_word_length_nonneg():
    assert max_word_length(_model(MINIMAL)) >= 0


def test_max_word_length_empty_dict():
    assert max_word_length({}) == 0

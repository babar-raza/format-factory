"""Tests for ABW word stats extension functions in abw_word_stats.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import load
from src.python.abw.abw_word_stats import (
    has_paragraphs,
    first_paragraph,
    last_paragraph,
    unique_word_count,
    all_paragraphs_nonempty,
    total_sentence_count,
)

SAMPLES = Path("samples/by-format/abw")
MINIMAL   = SAMPLES / "minimal-document.abw"    # 1 para "Hello"
TWO_PARA  = SAMPLES / "two-paragraphs.abw"      # 2 paras: "First paragraph." / "Second paragraph."
EMPTY_SEC = SAMPLES / "empty-section.abw"       # 0 paras

def _model(path):
    return load(path)


# has_paragraphs
def test_has_paragraphs_minimal():
    assert has_paragraphs(_model(MINIMAL)) is True

def test_has_paragraphs_two_para():
    assert has_paragraphs(_model(TWO_PARA)) is True

def test_has_paragraphs_empty():
    assert has_paragraphs(_model(EMPTY_SEC)) is False

def test_has_paragraphs_returns_bool():
    assert isinstance(has_paragraphs(_model(MINIMAL)), bool)


# first_paragraph
def test_first_paragraph_minimal():
    assert first_paragraph(_model(MINIMAL)) == "Hello"

def test_first_paragraph_two_para():
    assert first_paragraph(_model(TWO_PARA)) == "First paragraph."

def test_first_paragraph_empty():
    assert first_paragraph(_model(EMPTY_SEC)) == ""

def test_first_paragraph_returns_str():
    assert isinstance(first_paragraph(_model(MINIMAL)), str)


# last_paragraph
def test_last_paragraph_minimal():
    assert last_paragraph(_model(MINIMAL)) == "Hello"

def test_last_paragraph_two_para():
    assert last_paragraph(_model(TWO_PARA)) == "Second paragraph."

def test_last_paragraph_returns_str():
    assert isinstance(last_paragraph(_model(MINIMAL)), str)


# unique_word_count
def test_unique_word_count_minimal():
    # "Hello" → 1 unique word
    assert unique_word_count(_model(MINIMAL)) == 1

def test_unique_word_count_two_para():
    # "First paragraph." / "Second paragraph." → first,paragraph,second (3 unique after lower+split)
    count = unique_word_count(_model(TWO_PARA))
    assert count >= 2

def test_unique_word_count_returns_int():
    assert isinstance(unique_word_count(_model(MINIMAL)), int)


# all_paragraphs_nonempty
def test_all_paragraphs_nonempty_minimal():
    assert all_paragraphs_nonempty(_model(MINIMAL)) is True

def test_all_paragraphs_nonempty_two_para():
    assert all_paragraphs_nonempty(_model(TWO_PARA)) is True

def test_all_paragraphs_nonempty_returns_bool():
    assert isinstance(all_paragraphs_nonempty(_model(MINIMAL)), bool)


# total_sentence_count
def test_total_sentence_count_minimal():
    # "Hello" → 0 sentence-ending punctuation
    assert total_sentence_count(_model(MINIMAL)) == 0

def test_total_sentence_count_two_para():
    # "First paragraph." (1) + "Second paragraph." (1) → 2
    assert total_sentence_count(_model(TWO_PARA)) == 2

def test_total_sentence_count_returns_int():
    assert isinstance(total_sentence_count(_model(MINIMAL)), int)

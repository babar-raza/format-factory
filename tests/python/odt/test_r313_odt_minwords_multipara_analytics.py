"""
Tests for Sprint r313: odt_min_paragraph_words, odt_has_multiple_paragraphs.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt.odt_parser import odt_min_paragraph_words, odt_has_multiple_paragraphs

_ODT = _REPO / "samples" / "by-format" / "odt" / "valid"


# --- odt_min_paragraph_words ---

def test_odt_min_paragraph_words_minimal_two():
    assert odt_min_paragraph_words(_ODT / "minimal-document.odt") == 2


def test_odt_min_paragraph_words_two_paragraphs_two():
    # Both paragraphs have 2 words each; min is 2
    assert odt_min_paragraph_words(_ODT / "two-paragraphs.odt") == 2


def test_odt_min_paragraph_words_unicode_three():
    assert odt_min_paragraph_words(_ODT / "unicode-text.odt") == 3


def test_odt_min_paragraph_words_returns_int_minimal():
    assert isinstance(odt_min_paragraph_words(_ODT / "minimal-document.odt"), int)


def test_odt_min_paragraph_words_returns_int_unicode():
    assert isinstance(odt_min_paragraph_words(_ODT / "unicode-text.odt"), int)


def test_odt_min_paragraph_words_all_three():
    results = [
        odt_min_paragraph_words(_ODT / "minimal-document.odt"),
        odt_min_paragraph_words(_ODT / "two-paragraphs.odt"),
        odt_min_paragraph_words(_ODT / "unicode-text.odt"),
    ]
    assert results == [2, 2, 3]


# --- odt_has_multiple_paragraphs ---

def test_odt_has_multiple_paragraphs_minimal_false():
    assert odt_has_multiple_paragraphs(_ODT / "minimal-document.odt") is False


def test_odt_has_multiple_paragraphs_two_paragraphs_true():
    assert odt_has_multiple_paragraphs(_ODT / "two-paragraphs.odt") is True


def test_odt_has_multiple_paragraphs_unicode_false():
    assert odt_has_multiple_paragraphs(_ODT / "unicode-text.odt") is False


def test_odt_has_multiple_paragraphs_returns_bool_minimal():
    assert isinstance(odt_has_multiple_paragraphs(_ODT / "minimal-document.odt"), bool)


def test_odt_has_multiple_paragraphs_returns_bool_two():
    assert isinstance(odt_has_multiple_paragraphs(_ODT / "two-paragraphs.odt"), bool)


def test_odt_has_multiple_paragraphs_all_three():
    results = [
        odt_has_multiple_paragraphs(_ODT / "minimal-document.odt"),
        odt_has_multiple_paragraphs(_ODT / "two-paragraphs.odt"),
        odt_has_multiple_paragraphs(_ODT / "unicode-text.odt"),
    ]
    assert results == [False, True, False]

"""
r321 ODT analytics: odt_word_count_minus_headings, odt_has_punctuation.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt.odt_parser import odt_word_count_minus_headings, odt_has_punctuation

_ODT = _REPO / "samples" / "by-format" / "odt" / "valid"


# --- odt_word_count_minus_headings ---

def test_word_count_minus_headings_minimal():
    assert odt_word_count_minus_headings(_ODT / "minimal-document.odt") == 2

def test_word_count_minus_headings_two_paragraphs():
    assert odt_word_count_minus_headings(_ODT / "two-paragraphs.odt") == 4

def test_word_count_minus_headings_unicode():
    assert odt_word_count_minus_headings(_ODT / "unicode-text.odt") == 3

def test_word_count_minus_headings_returns_int():
    result = odt_word_count_minus_headings(_ODT / "minimal-document.odt")
    assert isinstance(result, int)

def test_word_count_minus_headings_nonnegative():
    for f in ["minimal-document.odt", "two-paragraphs.odt", "unicode-text.odt"]:
        assert odt_word_count_minus_headings(_ODT / f) >= 0

def test_word_count_minus_headings_all_distinct():
    results = [
        odt_word_count_minus_headings(_ODT / "minimal-document.odt"),
        odt_word_count_minus_headings(_ODT / "two-paragraphs.odt"),
        odt_word_count_minus_headings(_ODT / "unicode-text.odt"),
    ]
    assert len(set(results)) == 3


# --- odt_has_punctuation ---

def test_has_punctuation_minimal_true():
    assert odt_has_punctuation(_ODT / "minimal-document.odt") is True

def test_has_punctuation_two_paragraphs_true():
    assert odt_has_punctuation(_ODT / "two-paragraphs.odt") is True

def test_has_punctuation_unicode_false():
    assert odt_has_punctuation(_ODT / "unicode-text.odt") is False

def test_has_punctuation_returns_bool():
    result = odt_has_punctuation(_ODT / "minimal-document.odt")
    assert isinstance(result, bool)

def test_has_punctuation_unicode_is_bool():
    result = odt_has_punctuation(_ODT / "unicode-text.odt")
    assert isinstance(result, bool)

def test_has_punctuation_only_unicode_false():
    results = [
        odt_has_punctuation(_ODT / "minimal-document.odt"),
        odt_has_punctuation(_ODT / "two-paragraphs.odt"),
        odt_has_punctuation(_ODT / "unicode-text.odt"),
    ]
    assert results.count(False) == 1

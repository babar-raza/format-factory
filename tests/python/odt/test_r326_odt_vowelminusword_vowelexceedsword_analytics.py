"""
r326 ODT analytics: odt_vowel_count_minus_word_count, odt_vowel_count_exceeds_word_count.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt.odt_parser import odt_vowel_count_minus_word_count, odt_vowel_count_exceeds_word_count

_ODT = _REPO / "samples" / "by-format" / "odt" / "valid"


# --- odt_vowel_count_minus_word_count ---

def test_vowel_minus_word_minimal():
    assert odt_vowel_count_minus_word_count(_ODT / "minimal-document.odt") == 1

def test_vowel_minus_word_two_paragraphs():
    assert odt_vowel_count_minus_word_count(_ODT / "two-paragraphs.odt") == 5

def test_vowel_minus_word_unicode():
    assert odt_vowel_count_minus_word_count(_ODT / "unicode-text.odt") == 0

def test_vowel_minus_word_returns_int():
    result = odt_vowel_count_minus_word_count(_ODT / "minimal-document.odt")
    assert isinstance(result, int)

def test_vowel_minus_word_nonnegative():
    for f in ["minimal-document.odt", "two-paragraphs.odt", "unicode-text.odt"]:
        assert odt_vowel_count_minus_word_count(_ODT / f) >= 0

def test_vowel_minus_word_all_distinct():
    results = [
        odt_vowel_count_minus_word_count(_ODT / "minimal-document.odt"),
        odt_vowel_count_minus_word_count(_ODT / "two-paragraphs.odt"),
        odt_vowel_count_minus_word_count(_ODT / "unicode-text.odt"),
    ]
    assert len(set(results)) == 3


# --- odt_vowel_count_exceeds_word_count ---

def test_vowel_exceeds_word_minimal_true():
    assert odt_vowel_count_exceeds_word_count(_ODT / "minimal-document.odt") is True

def test_vowel_exceeds_word_two_paragraphs_true():
    assert odt_vowel_count_exceeds_word_count(_ODT / "two-paragraphs.odt") is True

def test_vowel_exceeds_word_unicode_false():
    assert odt_vowel_count_exceeds_word_count(_ODT / "unicode-text.odt") is False

def test_vowel_exceeds_word_returns_bool():
    result = odt_vowel_count_exceeds_word_count(_ODT / "minimal-document.odt")
    assert isinstance(result, bool)

def test_vowel_exceeds_word_unicode_is_bool():
    result = odt_vowel_count_exceeds_word_count(_ODT / "unicode-text.odt")
    assert isinstance(result, bool)

def test_vowel_exceeds_word_only_unicode_false():
    results = [
        odt_vowel_count_exceeds_word_count(_ODT / "minimal-document.odt"),
        odt_vowel_count_exceeds_word_count(_ODT / "two-paragraphs.odt"),
        odt_vowel_count_exceeds_word_count(_ODT / "unicode-text.odt"),
    ]
    assert results.count(False) == 1

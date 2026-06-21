"""Tests for odt_has_repeated_words and odt_word_length_range (Sprint 75)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_parser import odt_has_repeated_words, odt_word_length_range

ODT = _REPO / "samples" / "by-format" / "odt" / "valid"


# --- odt_has_repeated_words ---

def test_has_repeated_words_minimal_false():
    assert odt_has_repeated_words(ODT / "minimal-document.odt") is False


def test_has_repeated_words_two_paragraphs_true():
    assert odt_has_repeated_words(ODT / "two-paragraphs.odt") is True


def test_has_repeated_words_unicode_false():
    assert odt_has_repeated_words(ODT / "unicode-text.odt") is False


def test_has_repeated_words_returns_bool():
    assert isinstance(odt_has_repeated_words(ODT / "minimal-document.odt"), bool)


def test_has_repeated_words_two_paras_differs_from_minimal():
    assert odt_has_repeated_words(ODT / "two-paragraphs.odt") is not \
           odt_has_repeated_words(ODT / "minimal-document.odt")


# --- odt_word_length_range ---

def test_word_length_range_minimal_zero():
    assert odt_word_length_range(ODT / "minimal-document.odt") == 0


def test_word_length_range_two_paragraphs_five():
    assert odt_word_length_range(ODT / "two-paragraphs.odt") == 5


def test_word_length_range_unicode_three():
    assert odt_word_length_range(ODT / "unicode-text.odt") == 3


def test_word_length_range_returns_int():
    assert isinstance(odt_word_length_range(ODT / "minimal-document.odt"), int)


def test_word_length_range_nonnegative():
    for name in ["minimal-document.odt", "two-paragraphs.odt", "unicode-text.odt"]:
        assert odt_word_length_range(ODT / name) >= 0

"""Tests for odt_avg_word_count_per_paragraph and odt_sentence_per_paragraph (Sprint 107, R317)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt.odt_parser import odt_avg_word_count_per_paragraph, odt_sentence_per_paragraph

ODT = _REPO / "samples" / "by-format" / "odt" / "valid"


def test_avg_words_per_para_minimal():
    assert abs(odt_avg_word_count_per_paragraph(ODT / "minimal-document.odt") - 2.0) < 0.01


def test_avg_words_per_para_two_paragraphs():
    assert abs(odt_avg_word_count_per_paragraph(ODT / "two-paragraphs.odt") - 2.0) < 0.01


def test_avg_words_per_para_unicode():
    assert abs(odt_avg_word_count_per_paragraph(ODT / "unicode-text.odt") - 3.0) < 0.01


def test_avg_words_per_para_returns_float():
    assert isinstance(odt_avg_word_count_per_paragraph(ODT / "minimal-document.odt"), float)


def test_avg_words_per_para_positive():
    assert odt_avg_word_count_per_paragraph(ODT / "minimal-document.odt") > 0.0


def test_sentence_per_para_minimal():
    assert abs(odt_sentence_per_paragraph(ODT / "minimal-document.odt") - 1.0) < 0.01


def test_sentence_per_para_two_paragraphs():
    assert abs(odt_sentence_per_paragraph(ODT / "two-paragraphs.odt") - 1.0) < 0.01


def test_sentence_per_para_unicode():
    assert abs(odt_sentence_per_paragraph(ODT / "unicode-text.odt") - 0.0) < 0.01


def test_sentence_per_para_returns_float():
    assert isinstance(odt_sentence_per_paragraph(ODT / "minimal-document.odt"), float)


def test_sentence_per_para_nonnegative():
    assert odt_sentence_per_paragraph(ODT / "two-paragraphs.odt") >= 0.0

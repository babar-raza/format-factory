"""Tests for abw_words_per_char and abw_unique_words_per_paragraph (Sprint 106, R316)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import abw_words_per_char, abw_unique_words_per_paragraph

ABW = _REPO / "samples" / "by-format" / "abw"


def test_words_per_char_minimal():
    assert abs(abw_words_per_char(ABW / "minimal-document.abw") - 0.2) < 0.01


def test_words_per_char_two_paragraphs():
    assert abs(abw_words_per_char(ABW / "two-paragraphs.abw") - 0.1212) < 0.01


def test_words_per_char_empty():
    assert abs(abw_words_per_char(ABW / "empty-section.abw") - 0.0) < 0.001


def test_words_per_char_returns_float():
    assert isinstance(abw_words_per_char(ABW / "minimal-document.abw"), float)


def test_words_per_char_nonnegative():
    assert abw_words_per_char(ABW / "minimal-document.abw") >= 0.0


def test_unique_words_per_para_minimal():
    assert abs(abw_unique_words_per_paragraph(ABW / "minimal-document.abw") - 1.0) < 0.01


def test_unique_words_per_para_two_paragraphs():
    assert abs(abw_unique_words_per_paragraph(ABW / "two-paragraphs.abw") - 1.5) < 0.01


def test_unique_words_per_para_empty():
    assert abs(abw_unique_words_per_paragraph(ABW / "empty-section.abw") - 0.0) < 0.001


def test_unique_words_per_para_returns_float():
    assert isinstance(abw_unique_words_per_paragraph(ABW / "minimal-document.abw"), float)


def test_unique_words_per_para_nonnegative():
    assert abw_unique_words_per_paragraph(ABW / "two-paragraphs.abw") >= 0.0

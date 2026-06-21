"""Tests for fodt_avg_word_count_per_paragraph and fodt_word_density (Sprint 105, R315)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import fodt_avg_word_count_per_paragraph, fodt_word_density

FODT = _REPO / "samples" / "by-format" / "fodt"


def test_avg_words_minimal():
    assert abs(fodt_avg_word_count_per_paragraph(FODT / "minimal-document.fodt") - 2.0) < 0.01


def test_avg_words_headings():
    assert abs(fodt_avg_word_count_per_paragraph(FODT / "headings-and-paragraphs.fodt") - 11.0) < 0.01


def test_avg_words_list():
    assert abs(fodt_avg_word_count_per_paragraph(FODT / "list-basic.fodt") - 3.0) < 0.01


def test_avg_words_returns_float():
    assert isinstance(fodt_avg_word_count_per_paragraph(FODT / "minimal-document.fodt"), float)


def test_avg_words_positive():
    assert fodt_avg_word_count_per_paragraph(FODT / "headings-and-paragraphs.fodt") > 0.0


def test_word_density_minimal():
    assert abs(fodt_word_density(FODT / "minimal-document.fodt") - 0.1538) < 0.001


def test_word_density_headings():
    assert abs(fodt_word_density(FODT / "headings-and-paragraphs.fodt") - 0.1857) < 0.001


def test_word_density_list():
    assert abs(fodt_word_density(FODT / "list-basic.fodt") - 0.1429) < 0.001


def test_word_density_returns_float():
    assert isinstance(fodt_word_density(FODT / "minimal-document.fodt"), float)


def test_word_density_bounded():
    d = fodt_word_density(FODT / "minimal-document.fodt")
    assert 0.0 <= d <= 1.0

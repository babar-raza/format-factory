"""Tests for ODT analytics deepening (R290O): shortest_paragraph, paragraph_length_variance, digit_ratio."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_parser import odt_shortest_paragraph, odt_paragraph_length_variance, odt_digit_ratio

SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"


def test_shortest_paragraph_returns_int():
    result = odt_shortest_paragraph(SAMPLES / "two-paragraphs.odt")
    assert isinstance(result, int)
    assert result >= 0


def test_shortest_paragraph_minimal():
    result = odt_shortest_paragraph(SAMPLES / "minimal-document.odt")
    assert isinstance(result, int)


def test_paragraph_length_variance_returns_float():
    result = odt_paragraph_length_variance(SAMPLES / "two-paragraphs.odt")
    assert isinstance(result, float)
    assert result >= 0.0


def test_paragraph_length_variance_minimal():
    result = odt_paragraph_length_variance(SAMPLES / "minimal-document.odt")
    assert isinstance(result, float)


def test_digit_ratio_returns_float():
    result = odt_digit_ratio(SAMPLES / "two-paragraphs.odt")
    assert isinstance(result, float)
    assert 0.0 <= result <= 1.0


def test_digit_ratio_unicode():
    result = odt_digit_ratio(SAMPLES / "unicode-text.odt")
    assert isinstance(result, float)

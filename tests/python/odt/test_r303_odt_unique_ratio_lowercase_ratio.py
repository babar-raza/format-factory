"""Tests for odt_unique_ratio and odt_lowercase_ratio (Sprint 93, R303)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.odt.odt_parser import odt_unique_ratio, odt_lowercase_ratio

ODT = _REPO / "samples" / "by-format" / "odt" / "valid"


def test_unique_ratio_minimal():
    assert abs(odt_unique_ratio(ODT / "minimal-document.odt") - 1.0) < 0.01


def test_unique_ratio_two_paragraphs():
    assert abs(odt_unique_ratio(ODT / "two-paragraphs.odt") - 0.75) < 0.01


def test_unique_ratio_unicode():
    assert abs(odt_unique_ratio(ODT / "unicode-text.odt") - 1.0) < 0.01


def test_unique_ratio_returns_float():
    assert isinstance(odt_unique_ratio(ODT / "minimal-document.odt"), float)


def test_unique_ratio_between_zero_and_one():
    assert 0.0 <= odt_unique_ratio(ODT / "two-paragraphs.odt") <= 1.0


def test_lowercase_ratio_minimal():
    assert abs(odt_lowercase_ratio(ODT / "minimal-document.odt") - 0.692) < 0.01


def test_lowercase_ratio_two_paragraphs():
    assert abs(odt_lowercase_ratio(ODT / "two-paragraphs.odt") - 0.818) < 0.01


def test_lowercase_ratio_unicode():
    assert abs(odt_lowercase_ratio(ODT / "unicode-text.odt") - 0.615) < 0.01


def test_lowercase_ratio_returns_float():
    assert isinstance(odt_lowercase_ratio(ODT / "minimal-document.odt"), float)


def test_lowercase_ratio_positive():
    assert odt_lowercase_ratio(ODT / "minimal-document.odt") > 0.0

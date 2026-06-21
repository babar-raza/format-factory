"""Tests for fodt_vowel_count and fodt_space_count (Sprint 96, R306)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import fodt_vowel_count, fodt_space_count

FODT = _REPO / "samples" / "by-format" / "fodt"


def test_vowel_count_minimal():
    assert fodt_vowel_count(FODT / "minimal-document.fodt") == 3


def test_vowel_count_headings():
    assert fodt_vowel_count(FODT / "headings-and-paragraphs.fodt") == 88


def test_vowel_count_list():
    assert fodt_vowel_count(FODT / "list-basic.fodt") == 13


def test_vowel_count_returns_int():
    assert isinstance(fodt_vowel_count(FODT / "minimal-document.fodt"), int)


def test_vowel_count_nonnegative():
    assert fodt_vowel_count(FODT / "minimal-document.fodt") >= 0


def test_space_count_minimal():
    assert fodt_space_count(FODT / "minimal-document.fodt") == 1


def test_space_count_headings():
    assert fodt_space_count(FODT / "headings-and-paragraphs.fodt") == 37


def test_space_count_list():
    assert fodt_space_count(FODT / "list-basic.fodt") == 4


def test_space_count_returns_int():
    assert isinstance(fodt_space_count(FODT / "minimal-document.fodt"), int)


def test_space_count_nonnegative():
    assert fodt_space_count(FODT / "minimal-document.fodt") >= 0

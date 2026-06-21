"""Tests for abw_chars_per_word and abw_has_multi_para (Sprint 92, R302)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import abw_chars_per_word, abw_has_multi_para

ABW = _REPO / "samples" / "by-format" / "abw"


@pytest.fixture
def minimal():
    return ABW / "minimal-document.abw"


@pytest.fixture
def two_para():
    return ABW / "two-paragraphs.abw"


@pytest.fixture
def empty():
    return ABW / "empty-section.abw"


def test_chars_per_word_minimal(minimal):
    assert abs(abw_chars_per_word(minimal) - 5.0) < 0.01


def test_chars_per_word_two_para(two_para):
    assert abs(abw_chars_per_word(two_para) - 8.25) < 0.01


def test_chars_per_word_empty(empty):
    assert abs(abw_chars_per_word(empty) - 0.0) < 0.01


def test_chars_per_word_returns_float(minimal):
    assert isinstance(abw_chars_per_word(minimal), float)


def test_chars_per_word_nonnegative(empty):
    assert abw_chars_per_word(empty) >= 0.0


def test_has_multi_para_minimal(minimal):
    assert abw_has_multi_para(minimal) is False


def test_has_multi_para_two_para(two_para):
    assert abw_has_multi_para(two_para) is True


def test_has_multi_para_empty(empty):
    assert abw_has_multi_para(empty) is False


def test_has_multi_para_returns_bool(minimal):
    assert isinstance(abw_has_multi_para(minimal), bool)


def test_has_multi_para_true_for_two_paragraphs(two_para):
    assert abw_has_multi_para(two_para) is True

"""Tests for fodt_all_words_unique and fodt_has_more_words_than_unique (Sprint 84, R294)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.neutral_model import fodt_all_words_unique, fodt_has_more_words_than_unique

FODT = _REPO / "samples" / "by-format" / "fodt"


@pytest.fixture
def minimal():
    return FODT / "minimal-document.fodt"


@pytest.fixture
def headings():
    return FODT / "headings-and-paragraphs.fodt"


@pytest.fixture
def list_doc():
    return FODT / "list-basic.fodt"


def test_all_words_unique_minimal_true(minimal):
    assert fodt_all_words_unique(minimal) is True


def test_all_words_unique_headings_false(headings):
    assert fodt_all_words_unique(headings) is False


def test_all_words_unique_list_false(list_doc):
    assert fodt_all_words_unique(list_doc) is False


def test_all_words_unique_returns_bool(minimal):
    assert isinstance(fodt_all_words_unique(minimal), bool)


def test_has_more_words_than_unique_minimal_false(minimal):
    assert fodt_has_more_words_than_unique(minimal) is False


def test_has_more_words_than_unique_headings_true(headings):
    assert fodt_has_more_words_than_unique(headings) is True


def test_has_more_words_than_unique_list_true(list_doc):
    assert fodt_has_more_words_than_unique(list_doc) is True


def test_has_more_words_than_unique_returns_bool(minimal):
    assert isinstance(fodt_has_more_words_than_unique(minimal), bool)


def test_all_words_unique_inverse_of_has_more(minimal):
    assert fodt_all_words_unique(minimal) == (not fodt_has_more_words_than_unique(minimal))


def test_all_words_unique_inverse_of_has_more_headings(headings):
    assert fodt_all_words_unique(headings) == (not fodt_has_more_words_than_unique(headings))

"""Tests for abw_all_words_unique and abw_is_empty_document (Sprint 84, R294)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import abw_all_words_unique, abw_is_empty_document

ABW = _REPO / "samples" / "by-format" / "abw"


@pytest.fixture
def minimal():
    return ABW / "minimal-document.abw"


@pytest.fixture
def two_paras():
    return ABW / "two-paragraphs.abw"


@pytest.fixture
def empty_doc():
    return ABW / "empty-section.abw"


def test_all_words_unique_minimal_true(minimal):
    assert abw_all_words_unique(minimal) is True


def test_all_words_unique_two_paras_false(two_paras):
    assert abw_all_words_unique(two_paras) is False


def test_all_words_unique_empty_true(empty_doc):
    assert abw_all_words_unique(empty_doc) is True


def test_all_words_unique_returns_bool(minimal):
    assert isinstance(abw_all_words_unique(minimal), bool)


def test_is_empty_document_minimal_false(minimal):
    assert abw_is_empty_document(minimal) is False


def test_is_empty_document_two_paras_false(two_paras):
    assert abw_is_empty_document(two_paras) is False


def test_is_empty_document_empty_true(empty_doc):
    assert abw_is_empty_document(empty_doc) is True


def test_is_empty_document_returns_bool(minimal):
    assert isinstance(abw_is_empty_document(minimal), bool)


def test_is_empty_implies_all_words_unique(empty_doc):
    # Empty doc has no words, so trivially all unique
    assert abw_is_empty_document(empty_doc) is True
    assert abw_all_words_unique(empty_doc) is True


def test_nonempty_doc_has_words(minimal):
    assert abw_is_empty_document(minimal) is False

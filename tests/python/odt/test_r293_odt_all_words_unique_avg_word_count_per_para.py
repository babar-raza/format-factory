"""Tests for odt_all_words_unique and odt_avg_word_count_per_para (Sprint 83, R293)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_parser import odt_all_words_unique, odt_avg_word_count_per_para

ODT = _REPO / "samples" / "by-format" / "odt" / "valid"


@pytest.fixture
def minimal():
    return ODT / "minimal-document.odt"


@pytest.fixture
def two_paras():
    return ODT / "two-paragraphs.odt"


@pytest.fixture
def unicode_doc():
    return ODT / "unicode-text.odt"


def test_all_words_unique_minimal_true(minimal):
    assert odt_all_words_unique(minimal) is True


def test_all_words_unique_two_paras_false(two_paras):
    assert odt_all_words_unique(two_paras) is False


def test_all_words_unique_unicode_true(unicode_doc):
    assert odt_all_words_unique(unicode_doc) is True


def test_all_words_unique_returns_bool(minimal):
    assert isinstance(odt_all_words_unique(minimal), bool)


def test_avg_word_count_per_para_minimal(minimal):
    assert abs(odt_avg_word_count_per_para(minimal) - 2.0) < 0.001


def test_avg_word_count_per_para_two_paras(two_paras):
    assert abs(odt_avg_word_count_per_para(two_paras) - 2.0) < 0.001


def test_avg_word_count_per_para_unicode(unicode_doc):
    assert abs(odt_avg_word_count_per_para(unicode_doc) - 3.0) < 0.001


def test_avg_word_count_per_para_returns_float(minimal):
    assert isinstance(odt_avg_word_count_per_para(minimal), float)


def test_avg_word_count_per_para_positive(two_paras):
    assert odt_avg_word_count_per_para(two_paras) > 0.0


def test_all_words_unique_consistent_with_word_count(minimal):
    from odt.odt_parser import odt_word_count, odt_unique_word_count
    all_unique = odt_all_words_unique(minimal)
    assert all_unique == (odt_word_count(minimal) == odt_unique_word_count(minimal))

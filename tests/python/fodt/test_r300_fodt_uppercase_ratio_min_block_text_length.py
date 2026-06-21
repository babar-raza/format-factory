"""Tests for fodt_uppercase_ratio and fodt_min_block_text_length (Sprint 90, R300)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodt.neutral_model import fodt_uppercase_ratio, fodt_min_block_text_length

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


def test_uppercase_ratio_minimal(minimal):
    assert abs(fodt_uppercase_ratio(minimal) - 0.0769) < 0.001


def test_uppercase_ratio_headings(headings):
    assert abs(fodt_uppercase_ratio(headings) - 0.0691) < 0.001


def test_uppercase_ratio_list(list_doc):
    assert abs(fodt_uppercase_ratio(list_doc) - 0.0476) < 0.001


def test_uppercase_ratio_returns_float(minimal):
    assert isinstance(fodt_uppercase_ratio(minimal), float)


def test_uppercase_ratio_between_0_and_1(minimal):
    ratio = fodt_uppercase_ratio(minimal)
    assert 0.0 <= ratio <= 1.0


def test_min_block_text_length_minimal(minimal):
    assert fodt_min_block_text_length(minimal) == 13


def test_min_block_text_length_headings(headings):
    assert fodt_min_block_text_length(headings) == 11


def test_min_block_text_length_list(list_doc):
    assert fodt_min_block_text_length(list_doc) == 20


def test_min_block_text_length_returns_int(minimal):
    assert isinstance(fodt_min_block_text_length(minimal), int)


def test_min_block_text_length_nonnegative(minimal):
    assert fodt_min_block_text_length(minimal) >= 0

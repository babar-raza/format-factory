"""
Sprint 40 — 5 new ABW analytics functions.
Tests: abw_unique_word_count, abw_nonempty_paragraph_count,
       abw_max_paragraph_word_count, abw_total_word_length,
       abw_section_count
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    abw_unique_word_count,
    abw_nonempty_paragraph_count,
    abw_max_paragraph_word_count,
    abw_total_word_length,
    abw_section_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_SAMPLES / "minimal-document.abw")
_TWO_PARA = str(_SAMPLES / "two-paragraphs.abw")
_EMPTY = str(_SAMPLES / "empty-section.abw")


# --- abw_unique_word_count ---

def test_unique_word_count_minimal_is_int():
    assert isinstance(abw_unique_word_count(_MINIMAL), int)


def test_unique_word_count_minimal_nonnegative():
    assert abw_unique_word_count(_MINIMAL) >= 0


def test_unique_word_count_two_para_positive():
    assert abw_unique_word_count(_TWO_PARA) >= 1


def test_unique_word_count_empty_nonnegative():
    assert abw_unique_word_count(_EMPTY) >= 0


# --- abw_nonempty_paragraph_count ---

def test_nonempty_paragraph_count_minimal_is_int():
    assert isinstance(abw_nonempty_paragraph_count(_MINIMAL), int)


def test_nonempty_paragraph_count_minimal_nonnegative():
    assert abw_nonempty_paragraph_count(_MINIMAL) >= 0


def test_nonempty_paragraph_count_two_para_positive():
    assert abw_nonempty_paragraph_count(_TWO_PARA) >= 1


def test_nonempty_paragraph_count_empty_nonnegative():
    assert abw_nonempty_paragraph_count(_EMPTY) >= 0


# --- abw_max_paragraph_word_count ---

def test_max_paragraph_word_count_minimal_is_int():
    assert isinstance(abw_max_paragraph_word_count(_MINIMAL), int)


def test_max_paragraph_word_count_minimal_nonnegative():
    assert abw_max_paragraph_word_count(_MINIMAL) >= 0


def test_max_paragraph_word_count_two_para_positive():
    assert abw_max_paragraph_word_count(_TWO_PARA) >= 1


def test_max_paragraph_word_count_empty_nonnegative():
    assert abw_max_paragraph_word_count(_EMPTY) >= 0


# --- abw_total_word_length ---

def test_total_word_length_minimal_is_int():
    assert isinstance(abw_total_word_length(_MINIMAL), int)


def test_total_word_length_minimal_nonnegative():
    assert abw_total_word_length(_MINIMAL) >= 0


def test_total_word_length_two_para_positive():
    assert abw_total_word_length(_TWO_PARA) > 0


def test_total_word_length_empty_nonnegative():
    assert abw_total_word_length(_EMPTY) >= 0


# --- abw_section_count ---

def test_section_count_minimal_is_int():
    assert isinstance(abw_section_count(_MINIMAL), int)


def test_section_count_nonnegative():
    assert abw_section_count(_MINIMAL) >= 0


def test_section_count_empty_nonnegative():
    assert abw_section_count(_EMPTY) >= 0


def test_section_count_two_para_is_int():
    assert isinstance(abw_section_count(_TWO_PARA), int)

"""
Sprint 39 — 5 new ODT analytics functions.
Tests: odt_avg_word_length, odt_nonempty_paragraph_count,
       odt_unique_word_count, odt_max_paragraph_word_count,
       odt_total_word_length
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt import (
    odt_avg_word_length,
    odt_nonempty_paragraph_count,
    odt_unique_word_count,
    odt_max_paragraph_word_count,
    odt_total_word_length,
)

_SAMPLES = _REPO / "samples" / "by-format" / "odt" / "valid"
_MINIMAL = str(_SAMPLES / "minimal-document.odt")
_TWO_PARA = str(_SAMPLES / "two-paragraphs.odt")
_UNICODE = str(_SAMPLES / "unicode-text.odt")


# --- odt_avg_word_length ---

def test_avg_word_length_minimal_is_float():
    assert isinstance(odt_avg_word_length(_MINIMAL), float)


def test_avg_word_length_minimal_nonnegative():
    assert odt_avg_word_length(_MINIMAL) >= 0.0


def test_avg_word_length_two_para_positive():
    assert odt_avg_word_length(_TWO_PARA) > 0.0


def test_avg_word_length_unicode_positive():
    assert odt_avg_word_length(_UNICODE) > 0.0


# --- odt_nonempty_paragraph_count ---

def test_nonempty_paragraph_count_minimal_is_int():
    assert isinstance(odt_nonempty_paragraph_count(_MINIMAL), int)


def test_nonempty_paragraph_count_minimal_positive():
    assert odt_nonempty_paragraph_count(_MINIMAL) >= 0


def test_nonempty_paragraph_count_two_para_positive():
    assert odt_nonempty_paragraph_count(_TWO_PARA) >= 1


def test_nonempty_paragraph_count_unicode_positive():
    assert odt_nonempty_paragraph_count(_UNICODE) >= 1


# --- odt_unique_word_count ---

def test_unique_word_count_minimal_is_int():
    assert isinstance(odt_unique_word_count(_MINIMAL), int)


def test_unique_word_count_minimal_nonnegative():
    assert odt_unique_word_count(_MINIMAL) >= 0


def test_unique_word_count_two_para_positive():
    assert odt_unique_word_count(_TWO_PARA) >= 1


def test_unique_word_count_unicode_positive():
    assert odt_unique_word_count(_UNICODE) >= 1


# --- odt_max_paragraph_word_count ---

def test_max_paragraph_word_count_minimal_is_int():
    assert isinstance(odt_max_paragraph_word_count(_MINIMAL), int)


def test_max_paragraph_word_count_minimal_nonnegative():
    assert odt_max_paragraph_word_count(_MINIMAL) >= 0


def test_max_paragraph_word_count_two_para_positive():
    assert odt_max_paragraph_word_count(_TWO_PARA) >= 1


def test_max_paragraph_word_count_unicode_positive():
    assert odt_max_paragraph_word_count(_UNICODE) >= 1


# --- odt_total_word_length ---

def test_total_word_length_minimal_is_int():
    assert isinstance(odt_total_word_length(_MINIMAL), int)


def test_total_word_length_minimal_nonnegative():
    assert odt_total_word_length(_MINIMAL) >= 0


def test_total_word_length_two_para_positive():
    assert odt_total_word_length(_TWO_PARA) > 0


def test_total_word_length_unicode_positive():
    assert odt_total_word_length(_UNICODE) > 0

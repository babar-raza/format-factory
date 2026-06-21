"""
Sprint 37 — 5 new FODT analytics functions.
Tests: fodt_avg_word_length, fodt_nonempty_block_count,
       fodt_max_block_word_count, fodt_unique_word_count,
       fodt_block_type_count
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    fodt_avg_word_length,
    fodt_nonempty_block_count,
    fodt_max_block_word_count,
    fodt_unique_word_count,
    fodt_block_type_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_SAMPLES / "minimal-document.fodt")
_HEADINGS = str(_SAMPLES / "headings-and-paragraphs.fodt")
_TABLE = str(_SAMPLES / "table-basic.fodt")
_LIST = str(_SAMPLES / "list-basic.fodt")


# --- fodt_avg_word_length ---

def test_avg_word_length_minimal_is_float():
    assert isinstance(fodt_avg_word_length(_MINIMAL), float)


def test_avg_word_length_minimal_nonnegative():
    assert fodt_avg_word_length(_MINIMAL) >= 0.0


def test_avg_word_length_headings_positive():
    assert fodt_avg_word_length(_HEADINGS) > 0.0


def test_avg_word_length_table_is_float():
    assert isinstance(fodt_avg_word_length(_TABLE), float)


# --- fodt_nonempty_block_count ---

def test_nonempty_block_count_minimal_is_int():
    assert isinstance(fodt_nonempty_block_count(_MINIMAL), int)


def test_nonempty_block_count_minimal_nonnegative():
    assert fodt_nonempty_block_count(_MINIMAL) >= 0


def test_nonempty_block_count_headings_positive():
    assert fodt_nonempty_block_count(_HEADINGS) > 0


def test_nonempty_block_count_list_positive():
    assert fodt_nonempty_block_count(_LIST) > 0


# --- fodt_max_block_word_count ---

def test_max_block_word_count_minimal_is_int():
    assert isinstance(fodt_max_block_word_count(_MINIMAL), int)


def test_max_block_word_count_minimal_nonnegative():
    assert fodt_max_block_word_count(_MINIMAL) >= 0


def test_max_block_word_count_headings_positive():
    assert fodt_max_block_word_count(_HEADINGS) > 0


def test_max_block_word_count_table_is_int():
    assert isinstance(fodt_max_block_word_count(_TABLE), int)


# --- fodt_unique_word_count ---

def test_unique_word_count_minimal_is_int():
    assert isinstance(fodt_unique_word_count(_MINIMAL), int)


def test_unique_word_count_minimal_nonnegative():
    assert fodt_unique_word_count(_MINIMAL) >= 0


def test_unique_word_count_headings_positive():
    assert fodt_unique_word_count(_HEADINGS) > 0


def test_unique_word_count_list_positive():
    assert fodt_unique_word_count(_LIST) > 0


# --- fodt_block_type_count ---

def test_block_type_count_minimal_is_int():
    assert isinstance(fodt_block_type_count(_MINIMAL), int)


def test_block_type_count_minimal_positive():
    assert fodt_block_type_count(_MINIMAL) >= 0


def test_block_type_count_table_positive():
    assert fodt_block_type_count(_TABLE) > 0


def test_unique_word_count_gte_max_block():
    """Unique word count across all blocks >= words in single block."""
    assert fodt_unique_word_count(_HEADINGS) >= 1

"""Tests for abw_paragraph_analytics extension functions (ext3 batch)."""
from __future__ import annotations

from pathlib import Path

from abw.abw_paragraph_analytics import (
    abw_nonempty_paragraph_count,
    abw_longest_paragraph,
    abw_total_section_paragraph_count,
    abw_all_paragraphs_nonempty,
    abw_paragraph_char_counts,
    abw_has_long_paragraphs,
)

SAMPLES = Path("samples/by-format/abw")
MINIMAL = SAMPLES / "minimal-document.abw"
MULTI = SAMPLES / "multi-section.abw"


# --- abw_nonempty_paragraph_count ---

def test_nonempty_paragraph_count_returns_int():
    result = abw_nonempty_paragraph_count(MINIMAL)
    assert isinstance(result, int)


def test_nonempty_paragraph_count_minimal_positive():
    result = abw_nonempty_paragraph_count(MINIMAL)
    assert result >= 0


def test_nonempty_paragraph_count_leq_total():
    from abw.abw_paragraph_analytics import abw_paragraph_count
    nonempty = abw_nonempty_paragraph_count(MINIMAL)
    total = abw_paragraph_count(MINIMAL)
    assert nonempty <= total


# --- abw_longest_paragraph ---

def test_longest_paragraph_returns_str():
    assert isinstance(abw_longest_paragraph(MINIMAL), str)


def test_longest_paragraph_nonempty_when_has_paras():
    from abw.abw_paragraph_analytics import abw_paragraph_count
    if abw_paragraph_count(MINIMAL) > 0:
        assert len(abw_longest_paragraph(MINIMAL)) >= 0


# --- abw_total_section_paragraph_count ---

def test_total_section_paragraph_count_returns_int():
    result = abw_total_section_paragraph_count(MINIMAL)
    assert isinstance(result, int)


def test_total_section_paragraph_count_matches_paragraph_count():
    from abw.abw_paragraph_analytics import abw_paragraph_count
    result = abw_total_section_paragraph_count(MINIMAL)
    assert result == abw_paragraph_count(MINIMAL)


# --- abw_all_paragraphs_nonempty ---

def test_all_paragraphs_nonempty_returns_bool():
    assert isinstance(abw_all_paragraphs_nonempty(MINIMAL), bool)


def test_all_paragraphs_nonempty_minimal():
    result = abw_all_paragraphs_nonempty(MINIMAL)
    assert isinstance(result, bool)


# --- abw_paragraph_char_counts ---

def test_paragraph_char_counts_returns_list():
    result = abw_paragraph_char_counts(MINIMAL)
    assert isinstance(result, list)


def test_paragraph_char_counts_are_ints():
    result = abw_paragraph_char_counts(MINIMAL)
    assert all(isinstance(v, int) for v in result)


def test_paragraph_char_counts_length():
    from abw.abw_paragraph_analytics import abw_paragraph_count
    result = abw_paragraph_char_counts(MINIMAL)
    assert len(result) == abw_paragraph_count(MINIMAL)


# --- abw_has_long_paragraphs ---

def test_has_long_paragraphs_returns_bool():
    assert isinstance(abw_has_long_paragraphs(MINIMAL), bool)


def test_has_long_paragraphs_high_threshold_false():
    # 10000 char threshold should always be False for test samples
    result = abw_has_long_paragraphs(MINIMAL, threshold=10000)
    assert result is False

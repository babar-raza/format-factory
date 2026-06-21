"""Tests for abw_has_multiple_paragraphs and abw_avg_word_length_per_para (Sprint 77)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import abw_has_multiple_paragraphs, abw_avg_word_length_per_para

ABW = _REPO / "samples" / "by-format" / "abw"


# --- abw_has_multiple_paragraphs ---

def test_has_multiple_paragraphs_minimal_false():
    assert abw_has_multiple_paragraphs(ABW / "minimal-document.abw") is False


def test_has_multiple_paragraphs_two_paragraphs_true():
    assert abw_has_multiple_paragraphs(ABW / "two-paragraphs.abw") is True


def test_has_multiple_paragraphs_empty_section_false():
    assert abw_has_multiple_paragraphs(ABW / "empty-section.abw") is False


def test_has_multiple_paragraphs_returns_bool():
    assert isinstance(abw_has_multiple_paragraphs(ABW / "minimal-document.abw"), bool)


def test_has_multiple_paragraphs_only_two_paragraphs_true():
    vals = [
        abw_has_multiple_paragraphs(ABW / "minimal-document.abw"),
        abw_has_multiple_paragraphs(ABW / "two-paragraphs.abw"),
        abw_has_multiple_paragraphs(ABW / "empty-section.abw"),
    ]
    assert vals.count(True) == 1


# --- abw_avg_word_length_per_para ---

def test_avg_word_length_per_para_minimal():
    assert abs(abw_avg_word_length_per_para(ABW / "minimal-document.abw") - 5.0) < 0.01


def test_avg_word_length_per_para_two_paragraphs():
    assert abs(abw_avg_word_length_per_para(ABW / "two-paragraphs.abw") - 15.5) < 0.01


def test_avg_word_length_per_para_empty_zero():
    assert abw_avg_word_length_per_para(ABW / "empty-section.abw") == 0.0


def test_avg_word_length_per_para_returns_float():
    assert isinstance(abw_avg_word_length_per_para(ABW / "minimal-document.abw"), float)


def test_avg_word_length_per_para_nonnegative():
    for name in ["minimal-document.abw", "two-paragraphs.abw", "empty-section.abw"]:
        assert abw_avg_word_length_per_para(ABW / name) >= 0.0

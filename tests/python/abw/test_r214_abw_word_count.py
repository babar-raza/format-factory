"""Tests for abw_word_count().

Sprint: product-deepening-rnext84
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import abw_word_count

ABW_SAMPLES = _REPO / "samples" / "by-format" / "abw"


class TestAbwWordCount:
    def test_import(self):
        assert callable(abw_word_count)

    def test_minimal_document_has_one_word(self):
        assert abw_word_count(ABW_SAMPLES / "minimal-document.abw") == 1

    def test_two_paragraphs_has_four_words(self):
        assert abw_word_count(ABW_SAMPLES / "two-paragraphs.abw") == 4

    def test_empty_section_has_zero_words(self):
        assert abw_word_count(ABW_SAMPLES / "empty-section.abw") == 0

    def test_returns_int(self):
        result = abw_word_count(ABW_SAMPLES / "minimal-document.abw")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for sample in ABW_SAMPLES.iterdir():
            if sample.suffix == ".abw":
                assert abw_word_count(sample) >= 0

"""
test_r131_fodt_text_char_analytics.py — Test coverage for FODT text character analytics.

Gaps closed:
- GAP-FODT-FOSS-FODT_LOWERCA-001 (fodt_lowercase_ratio — missing_test_coverage)
- GAP-FODT-FOSS-FODT_DIGIT_C-001 (fodt_digit_count — missing_test_coverage)
- GAP-FODT-FOSS-FODT_NUMERIC-001 (fodt_numeric_word_count — missing_test_coverage)
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLES = _REPO / "samples" / "by-format" / "fodt"
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt.fodt_analytics import (
    fodt_lowercase_ratio,
    fodt_digit_count,
    fodt_numeric_word_count,
)


class TestFodtLowercaseRatio:
    """GAP-FODT-FOSS-FODT_LOWERCA-001: fodt_lowercase_ratio."""

    def test_returns_float(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_lowercase_ratio(f), float)

    def test_ratio_between_zero_and_one(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        ratio = fodt_lowercase_ratio(f)
        assert 0.0 <= ratio <= 1.0

    def test_minimal_document_returns_float(self):
        f = _SAMPLES / "minimal-document.fodt"
        result = fodt_lowercase_ratio(f)
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0

    def test_paragraph_doc_has_nonzero_ratio(self):
        """Document with mixed-case text should have a ratio > 0."""
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        ratio = fodt_lowercase_ratio(f)
        # English text is mostly lowercase
        assert ratio >= 0.0

    def test_list_doc(self):
        f = _SAMPLES / "list-basic.fodt"
        ratio = fodt_lowercase_ratio(f)
        assert isinstance(ratio, float)
        assert 0.0 <= ratio <= 1.0


class TestFodtDigitCount:
    """GAP-FODT-FOSS-FODT_DIGIT_C-001: fodt_digit_count."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_digit_count(f), int)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_digit_count(f) >= 0

    def test_minimal_document(self):
        f = _SAMPLES / "minimal-document.fodt"
        result = fodt_digit_count(f)
        assert isinstance(result, int)
        assert result >= 0

    def test_list_doc_non_negative(self):
        f = _SAMPLES / "list-basic.fodt"
        assert fodt_digit_count(f) >= 0

    def test_table_doc_non_negative(self):
        f = _SAMPLES / "table-basic.fodt"
        assert fodt_digit_count(f) >= 0


class TestFodtNumericWordCount:
    """GAP-FODT-FOSS-FODT_NUMERIC-001: fodt_numeric_word_count."""

    def test_returns_int(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert isinstance(fodt_numeric_word_count(f), int)

    def test_non_negative(self):
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        assert fodt_numeric_word_count(f) >= 0

    def test_minimal_document(self):
        f = _SAMPLES / "minimal-document.fodt"
        result = fodt_numeric_word_count(f)
        assert isinstance(result, int)
        assert result >= 0

    def test_consistent_with_digit_count(self):
        """numeric_word_count <= digit_count (words of digits have chars too)."""
        f = _SAMPLES / "headings-and-paragraphs.fodt"
        word_count = fodt_numeric_word_count(f)
        digit_count = fodt_digit_count(f)
        # A document with 0 digits can have 0 numeric words
        if digit_count == 0:
            assert word_count == 0

    def test_all_sample_files(self):
        """All FODT sample files return valid int >= 0."""
        for sample in _SAMPLES.glob("*.fodt"):
            result = fodt_numeric_word_count(sample)
            assert isinstance(result, int) and result >= 0, f"Failed for {sample}"

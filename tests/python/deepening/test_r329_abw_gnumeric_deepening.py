"""Sprint 119 — ABW (abw_chars_per_paragraph, abw_words_per_paragraph)
and Gnumeric (gnumeric_rows_per_sheet, gnumeric_non_string_cell_percentage).
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.abw.abw_codec import abw_chars_per_paragraph, abw_words_per_paragraph
from src.python.gnumeric.gnumeric_codec import gnumeric_rows_per_sheet, gnumeric_non_string_cell_percentage

ABW = _REPO / "samples" / "by-format" / "abw"
GNU = _REPO / "samples" / "by-format" / "gnumeric"


# ---------- abw_chars_per_paragraph ----------

class TestAbwCharsPerParagraph:
    def test_minimal_value(self):
        assert abs(abw_chars_per_paragraph(ABW / "minimal-document.abw") - 5.0) < 0.01

    def test_two_paragraphs_value(self):
        assert abs(abw_chars_per_paragraph(ABW / "two-paragraphs.abw") - 16.5) < 0.01

    def test_empty_section_value(self):
        assert abs(abw_chars_per_paragraph(ABW / "empty-section.abw") - 0.0) < 0.01

    def test_returns_float(self):
        assert isinstance(abw_chars_per_paragraph(ABW / "minimal-document.abw"), float)

    def test_non_negative(self):
        assert abw_chars_per_paragraph(ABW / "minimal-document.abw") >= 0.0


# ---------- abw_words_per_paragraph ----------

class TestAbwWordsPerParagraph:
    def test_minimal_value(self):
        assert abs(abw_words_per_paragraph(ABW / "minimal-document.abw") - 1.0) < 0.01

    def test_two_paragraphs_value(self):
        assert abs(abw_words_per_paragraph(ABW / "two-paragraphs.abw") - 2.0) < 0.01

    def test_empty_section_value(self):
        assert abs(abw_words_per_paragraph(ABW / "empty-section.abw") - 0.0) < 0.01

    def test_returns_float(self):
        assert isinstance(abw_words_per_paragraph(ABW / "minimal-document.abw"), float)

    def test_non_negative(self):
        assert abw_words_per_paragraph(ABW / "two-paragraphs.abw") >= 0.0


# ---------- gnumeric_rows_per_sheet ----------

class TestGnumericRowsPerSheet:
    def test_minimal_value(self):
        assert abs(gnumeric_rows_per_sheet(GNU / "minimal-spreadsheet.gnumeric") - 1.0) < 0.01

    def test_multi_cell_value(self):
        assert abs(gnumeric_rows_per_sheet(GNU / "multi-cell-basic.gnumeric") - 2.0) < 0.01

    def test_empty_sheet_value(self):
        assert abs(gnumeric_rows_per_sheet(GNU / "empty-sheet.gnumeric") - 0.0) < 0.01

    def test_returns_float(self):
        assert isinstance(gnumeric_rows_per_sheet(GNU / "minimal-spreadsheet.gnumeric"), float)

    def test_non_negative(self):
        assert gnumeric_rows_per_sheet(GNU / "multi-cell-basic.gnumeric") >= 0.0


# ---------- gnumeric_non_string_cell_percentage ----------

class TestGnumericNonStringCellPercentage:
    def test_minimal_value(self):
        assert abs(gnumeric_non_string_cell_percentage(GNU / "minimal-spreadsheet.gnumeric") - 0.0) < 0.1

    def test_multi_cell_value(self):
        assert abs(gnumeric_non_string_cell_percentage(GNU / "multi-cell-basic.gnumeric") - 25.0) < 0.1

    def test_empty_sheet_value(self):
        assert abs(gnumeric_non_string_cell_percentage(GNU / "empty-sheet.gnumeric") - 100.0) < 0.1

    def test_returns_float(self):
        assert isinstance(gnumeric_non_string_cell_percentage(GNU / "minimal-spreadsheet.gnumeric"), float)

    def test_range_valid(self):
        v = gnumeric_non_string_cell_percentage(GNU / "multi-cell-basic.gnumeric")
        assert 0.0 <= v <= 100.0

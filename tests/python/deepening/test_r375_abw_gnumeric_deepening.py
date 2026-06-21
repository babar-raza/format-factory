"""Sprint 247 deepening: ABW + Gnumeric eighty-nine multiplier analytics."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_ABW = _REPO / "samples" / "by-format" / "abw"
_GNU = _REPO / "samples" / "by-format" / "gnumeric"

from src.python.abw import (
    abw_word_count_times_eighty_nine,
    abw_paragraph_count_times_eighty_nine,
)
from src.python.gnumeric import (
    gnumeric_file_size_bytes_times_eighty_nine,
    gnumeric_total_row_count_times_eighty_nine,
)


class TestAbwWordCountTimesEightyNine:
    def test_minimal_document(self):
        result = abw_word_count_times_eighty_nine(_ABW / "minimal-document.abw")
        assert isinstance(result, int)
        assert result >= 0

    def test_two_paragraphs(self):
        result = abw_word_count_times_eighty_nine(_ABW / "two-paragraphs.abw")
        assert isinstance(result, int)
        assert result >= 0

    def test_multiple_vs_single(self):
        r_two = abw_word_count_times_eighty_nine(_ABW / "two-paragraphs.abw")
        r_min = abw_word_count_times_eighty_nine(_ABW / "minimal-document.abw")
        assert r_two >= r_min

    def test_empty_section(self):
        result = abw_word_count_times_eighty_nine(_ABW / "empty-section.abw")
        assert isinstance(result, int)
        assert result >= 0

    def test_multiplier_factor(self):
        from src.python.abw import abw_word_count
        path = _ABW / "two-paragraphs.abw"
        base = abw_word_count(path)
        assert abw_word_count_times_eighty_nine(path) == base * 89


class TestAbwParagraphCountTimesEightyNine:
    def test_minimal_document(self):
        result = abw_paragraph_count_times_eighty_nine(_ABW / "minimal-document.abw")
        assert isinstance(result, int)
        assert result >= 0

    def test_two_paragraphs(self):
        result = abw_paragraph_count_times_eighty_nine(_ABW / "two-paragraphs.abw")
        assert isinstance(result, int)
        assert result >= 89  # at least 1 paragraph * 89

    def test_empty_section(self):
        result = abw_paragraph_count_times_eighty_nine(_ABW / "empty-section.abw")
        assert isinstance(result, int)
        assert result >= 0

    def test_multiplier_factor(self):
        from src.python.abw import abw_paragraph_count
        path = _ABW / "two-paragraphs.abw"
        base = abw_paragraph_count(path)
        assert abw_paragraph_count_times_eighty_nine(path) == base * 89

    def test_returns_multiple_of_89(self):
        result = abw_paragraph_count_times_eighty_nine(_ABW / "minimal-document.abw")
        assert result % 89 == 0


class TestGnumericFileSizeBytesTimesEightyNine:
    def test_minimal_spreadsheet(self):
        result = gnumeric_file_size_bytes_times_eighty_nine(_GNU / "minimal-spreadsheet.gnumeric")
        assert isinstance(result, int)
        assert result > 0

    def test_empty_sheet(self):
        result = gnumeric_file_size_bytes_times_eighty_nine(_GNU / "empty-sheet.gnumeric")
        assert isinstance(result, int)
        assert result > 0

    def test_multi_cell(self):
        result = gnumeric_file_size_bytes_times_eighty_nine(_GNU / "multi-cell-basic.gnumeric")
        assert isinstance(result, int)
        assert result > 0

    def test_multiplier_factor(self):
        from src.python.gnumeric import gnumeric_file_size_bytes
        path = _GNU / "minimal-spreadsheet.gnumeric"
        base = gnumeric_file_size_bytes(path)
        assert gnumeric_file_size_bytes_times_eighty_nine(path) == base * 89

    def test_returns_multiple_of_89(self):
        result = gnumeric_file_size_bytes_times_eighty_nine(_GNU / "multi-cell-basic.gnumeric")
        assert result % 89 == 0


class TestGnumericTotalRowCountTimesEightyNine:
    def test_minimal_spreadsheet(self):
        result = gnumeric_total_row_count_times_eighty_nine(_GNU / "minimal-spreadsheet.gnumeric")
        assert isinstance(result, int)
        assert result >= 0

    def test_empty_sheet(self):
        result = gnumeric_total_row_count_times_eighty_nine(_GNU / "empty-sheet.gnumeric")
        assert isinstance(result, int)
        assert result >= 0

    def test_multi_cell(self):
        result = gnumeric_total_row_count_times_eighty_nine(_GNU / "multi-cell-basic.gnumeric")
        assert isinstance(result, int)
        assert result >= 0

    def test_multiplier_factor(self):
        from src.python.gnumeric import gnumeric_total_row_count
        path = _GNU / "multi-cell-basic.gnumeric"
        base = gnumeric_total_row_count(path)
        assert gnumeric_total_row_count_times_eighty_nine(path) == base * 89

    def test_returns_multiple_of_89(self):
        result = gnumeric_total_row_count_times_eighty_nine(_GNU / "minimal-spreadsheet.gnumeric")
        assert result % 89 == 0

"""Sprint 75 — FODS / Gnumeric / ABW / TSV product deepening (R305).

Tests 8 new analytics functions:
  FODS: fods_avg_string_length, fods_col_count_variance
  Gnumeric: gnumeric_row_count_variance, gnumeric_sheet_name_lengths
  ABW: abw_punctuation_count, abw_median_paragraph_length
  TSV: tsv_max_row_cell_count, tsv_distinct_value_ratio
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import fods_avg_string_length, fods_col_count_variance
from src.python.fods.parser import parse_fods
from src.python.gnumeric import gnumeric_row_count_variance, gnumeric_sheet_name_lengths
from src.python.abw import abw_punctuation_count, abw_median_paragraph_length
from src.python.tsv import tsv_max_row_cell_count, tsv_distinct_value_ratio

_FODS = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"
_ABW = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
_TSV = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"


class TestFodsAvgStringLength:
    def test_returns_float(self):
        wb = parse_fods(_FODS)
        assert isinstance(fods_avg_string_length(wb), float)

    def test_nonnegative(self):
        wb = parse_fods(_FODS)
        assert fods_avg_string_length(wb) >= 0.0


class TestFodsColCountVariance:
    def test_returns_float(self):
        wb = parse_fods(_FODS)
        assert isinstance(fods_col_count_variance(wb), float)

    def test_nonnegative(self):
        wb = parse_fods(_FODS)
        assert fods_col_count_variance(wb) >= 0.0


class TestGnumericRowCountVariance:
    def test_returns_float(self):
        assert isinstance(gnumeric_row_count_variance(_GNUMERIC), float)

    def test_nonnegative(self):
        assert gnumeric_row_count_variance(_GNUMERIC) >= 0.0


class TestGnumericSheetNameLengths:
    def test_returns_list(self):
        result = gnumeric_sheet_name_lengths(_GNUMERIC)
        assert isinstance(result, list)

    def test_entries_are_int(self):
        result = gnumeric_sheet_name_lengths(_GNUMERIC)
        if result:
            assert isinstance(result[0], int)


class TestAbwPunctuationCount:
    def test_returns_int(self):
        assert isinstance(abw_punctuation_count(_ABW), int)

    def test_nonnegative(self):
        assert abw_punctuation_count(_ABW) >= 0


class TestAbwMedianParagraphLength:
    def test_returns_int(self):
        assert isinstance(abw_median_paragraph_length(_ABW), int)

    def test_nonnegative(self):
        assert abw_median_paragraph_length(_ABW) >= 0


class TestTsvMaxRowCellCount:
    def test_returns_int(self):
        assert isinstance(tsv_max_row_cell_count(_TSV), int)

    def test_positive(self):
        assert tsv_max_row_cell_count(_TSV) > 0


class TestTsvDistinctValueRatio:
    def test_returns_float(self):
        assert isinstance(tsv_distinct_value_ratio(_TSV), float)

    def test_between_zero_and_one(self):
        val = tsv_distinct_value_ratio(_TSV)
        assert 0.0 <= val <= 1.0

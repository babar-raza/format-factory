"""Sprint 79 — FODS/GNUMERIC/ABW/TSV product deepening cycle 2."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods
from src.python.fods import fods_numeric_cell_ratio, fods_max_row_cell_count
from src.python.gnumeric import gnumeric_max_cell_value_length, gnumeric_is_multi_sheet
from src.python.abw import abw_longest_paragraph_words, abw_distinct_word_ratio
from src.python.tsv import tsv_empty_cell_ratio, tsv_column_value_variance

_FODS = _REPO / "samples" / "by-format" / "fods" / "valid" / "minimal-two-sheets.fods"
_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric"
_ABW = _REPO / "samples" / "by-format" / "abw"
_TSV = _REPO / "samples" / "by-format" / "tsv"


def _gnumeric_sample():
    candidates = list(_GNUMERIC.glob("*.gnumeric"))
    assert candidates, "No .gnumeric sample found"
    return candidates[0]


def _abw_sample():
    candidates = list(_ABW.glob("*.abw"))
    assert candidates, "No .abw sample found"
    return candidates[0]


def _tsv_sample():
    candidates = list(_TSV.glob("*.tsv"))
    assert candidates, "No .tsv sample found"
    return candidates[0]


class TestFodsNumericCellRatio:
    def test_returns_float(self):
        wb = parse_fods(_FODS)
        result = fods_numeric_cell_ratio(wb)
        assert isinstance(result, float)

    def test_between_zero_and_one(self):
        wb = parse_fods(_FODS)
        result = fods_numeric_cell_ratio(wb)
        assert 0.0 <= result <= 1.0


class TestFodsMaxRowCellCount:
    def test_returns_int(self):
        wb = parse_fods(_FODS)
        result = fods_max_row_cell_count(wb)
        assert isinstance(result, int)

    def test_non_negative(self):
        wb = parse_fods(_FODS)
        result = fods_max_row_cell_count(wb)
        assert result >= 0


class TestGnumericMaxCellValueLength:
    def test_returns_int(self):
        result = gnumeric_max_cell_value_length(_gnumeric_sample())
        assert isinstance(result, int)

    def test_non_negative(self):
        result = gnumeric_max_cell_value_length(_gnumeric_sample())
        assert result >= 0


class TestGnumericIsMultiSheet:
    def test_returns_bool(self):
        result = gnumeric_is_multi_sheet(_gnumeric_sample())
        assert isinstance(result, bool)


class TestAbwLongestParagraphWords:
    def test_returns_int(self):
        result = abw_longest_paragraph_words(_abw_sample())
        assert isinstance(result, int)

    def test_non_negative(self):
        result = abw_longest_paragraph_words(_abw_sample())
        assert result >= 0


class TestAbwDistinctWordRatio:
    def test_returns_float(self):
        result = abw_distinct_word_ratio(_abw_sample())
        assert isinstance(result, float)

    def test_between_zero_and_one(self):
        result = abw_distinct_word_ratio(_abw_sample())
        assert 0.0 <= result <= 1.0


class TestTsvEmptyCellRatio:
    def test_returns_float(self):
        result = tsv_empty_cell_ratio(_tsv_sample())
        assert isinstance(result, float)

    def test_between_zero_and_one(self):
        result = tsv_empty_cell_ratio(_tsv_sample())
        assert 0.0 <= result <= 1.0


class TestTsvColumnValueVariance:
    def test_returns_float(self):
        result = tsv_column_value_variance(_tsv_sample())
        assert isinstance(result, float)

    def test_non_negative(self):
        result = tsv_column_value_variance(_tsv_sample())
        assert result >= 0.0

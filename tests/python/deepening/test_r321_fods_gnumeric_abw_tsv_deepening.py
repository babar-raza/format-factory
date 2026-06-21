"""Sprint 91 — FODS/Gnumeric/ABW/TSV cycle 5: 8 new analytics functions."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.parser import parse_fods
from src.python.fods.neutral_model import fods_empty_row_ratio, fods_max_string_cell_length
from src.python.gnumeric.gnumeric_codec import gnumeric_avg_cells_per_row, gnumeric_has_formulas
from src.python.abw.abw_codec import abw_digit_count, abw_paragraph_density
from src.python.tsv.tsv_parser import tsv_max_column_length, tsv_empty_column_ratio

_FODS = _REPO / "samples" / "by-format" / "fods"
_GNUMERIC = _REPO / "samples" / "by-format" / "gnumeric"
_ABW = _REPO / "samples" / "by-format" / "abw"
_TSV = _REPO / "samples" / "by-format" / "tsv"


@pytest.fixture
def fods_workbook():
    sample = next(_FODS.glob("*.fods"))
    return parse_fods(str(sample))


@pytest.fixture
def gnumeric_sample():
    return next(_GNUMERIC.glob("*.gnumeric"))


@pytest.fixture
def abw_sample():
    return next(_ABW.glob("*.abw"))


@pytest.fixture
def tsv_sample():
    return next(_TSV.glob("*.tsv"))


# --- FODS ---
class TestFodsEmptyRowRatio:
    def test_returns_float(self, fods_workbook):
        result = fods_empty_row_ratio(fods_workbook)
        assert isinstance(result, float)

    def test_between_zero_and_one(self, fods_workbook):
        result = fods_empty_row_ratio(fods_workbook)
        assert 0.0 <= result <= 1.0


class TestFodsMaxStringCellLength:
    def test_returns_int(self, fods_workbook):
        result = fods_max_string_cell_length(fods_workbook)
        assert isinstance(result, int)

    def test_non_negative(self, fods_workbook):
        assert fods_max_string_cell_length(fods_workbook) >= 0


# --- Gnumeric ---
class TestGnumericAvgCellsPerRow:
    def test_returns_float(self, gnumeric_sample):
        result = gnumeric_avg_cells_per_row(gnumeric_sample)
        assert isinstance(result, float)

    def test_non_negative(self, gnumeric_sample):
        assert gnumeric_avg_cells_per_row(gnumeric_sample) >= 0.0


class TestGnumericHasFormulas:
    def test_returns_bool(self, gnumeric_sample):
        result = gnumeric_has_formulas(gnumeric_sample)
        assert isinstance(result, bool)

    def test_deterministic(self, gnumeric_sample):
        assert gnumeric_has_formulas(gnumeric_sample) == gnumeric_has_formulas(gnumeric_sample)


# --- ABW ---
class TestAbwDigitCount:
    def test_returns_int(self, abw_sample):
        result = abw_digit_count(abw_sample)
        assert isinstance(result, int)

    def test_non_negative(self, abw_sample):
        assert abw_digit_count(abw_sample) >= 0


class TestAbwParagraphDensity:
    def test_returns_float(self, abw_sample):
        result = abw_paragraph_density(abw_sample)
        assert isinstance(result, float)

    def test_non_negative(self, abw_sample):
        assert abw_paragraph_density(abw_sample) >= 0.0


# --- TSV ---
class TestTsvMaxColumnLength:
    def test_returns_int(self, tsv_sample):
        result = tsv_max_column_length(tsv_sample)
        assert isinstance(result, int)

    def test_non_negative(self, tsv_sample):
        assert tsv_max_column_length(tsv_sample) >= 0


class TestTsvEmptyColumnRatio:
    def test_returns_float(self, tsv_sample):
        result = tsv_empty_column_ratio(tsv_sample)
        assert isinstance(result, float)

    def test_between_zero_and_one(self, tsv_sample):
        result = tsv_empty_column_ratio(tsv_sample)
        assert 0.0 <= result <= 1.0

"""Sprint 115 — FODS/GNUMERIC/ABW/TSV cycle 11 product deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_empty_cell_ratio, fods_nonempty_cell_per_row
from src.python.fods.parser import parse_fods
from src.python.gnumeric.gnumeric_codec import gnumeric_cell_density_variance, gnumeric_has_formula_cells
from src.python.abw.abw_codec import abw_letter_ratio, abw_punctuation_ratio
from src.python.tsv.tsv_parser import tsv_field_uniqueness_ratio, tsv_longest_row_field_count

_FODS = next((_REPO / "samples" / "by-format" / "fods").glob("*.fods"))
_GNUMERIC = next((_REPO / "samples" / "by-format" / "gnumeric").glob("*.gnumeric"))
_ABW = next((_REPO / "samples" / "by-format" / "abw").glob("*.abw"))
_TSV = next((_REPO / "samples" / "by-format" / "tsv").glob("*.tsv"))


class TestFodsEmptyCellRatio:
    def test_returns_float(self):
        wb = parse_fods(_FODS)
        result = fods_empty_cell_ratio(wb)
        assert isinstance(result, float)

    def test_range_zero_to_one(self):
        wb = parse_fods(_FODS)
        result = fods_empty_cell_ratio(wb)
        assert 0.0 <= result <= 1.0

    def test_empty_workbook(self):
        assert fods_empty_cell_ratio({"sheets": []}) == 0.0

    def test_invalid_sheet_index(self):
        wb = parse_fods(_FODS)
        assert fods_empty_cell_ratio(wb, sheet_index=999) == 0.0


class TestFodsNonemptyCellPerRow:
    def test_returns_float(self):
        wb = parse_fods(_FODS)
        result = fods_nonempty_cell_per_row(wb)
        assert isinstance(result, float)

    def test_non_negative(self):
        wb = parse_fods(_FODS)
        assert fods_nonempty_cell_per_row(wb) >= 0.0

    def test_empty_workbook(self):
        assert fods_nonempty_cell_per_row({"sheets": []}) == 0.0

    def test_invalid_sheet_index(self):
        wb = parse_fods(_FODS)
        assert fods_nonempty_cell_per_row(wb, sheet_index=999) == 0.0


class TestGnumericCellDensityVariance:
    def test_returns_float(self):
        result = gnumeric_cell_density_variance(_GNUMERIC)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert gnumeric_cell_density_variance(_GNUMERIC) >= 0.0


class TestGnumericHasFormulaCells:
    def test_returns_bool(self):
        result = gnumeric_has_formula_cells(_GNUMERIC)
        assert isinstance(result, bool)


class TestAbwLetterRatio:
    def test_returns_float(self):
        result = abw_letter_ratio(_ABW)
        assert isinstance(result, float)

    def test_range_zero_to_one(self):
        result = abw_letter_ratio(_ABW)
        assert 0.0 <= result <= 1.0


class TestAbwPunctuationRatio:
    def test_returns_float(self):
        result = abw_punctuation_ratio(_ABW)
        assert isinstance(result, float)

    def test_range_zero_to_one(self):
        result = abw_punctuation_ratio(_ABW)
        assert 0.0 <= result <= 1.0


class TestTsvFieldUniquenessRatio:
    def test_returns_float(self):
        result = tsv_field_uniqueness_ratio(_TSV)
        assert isinstance(result, float)

    def test_range_zero_to_one(self):
        result = tsv_field_uniqueness_ratio(_TSV)
        assert 0.0 <= result <= 1.0


class TestTsvLongestRowFieldCount:
    def test_returns_int(self):
        result = tsv_longest_row_field_count(_TSV)
        assert isinstance(result, int)

    def test_positive(self):
        assert tsv_longest_row_field_count(_TSV) > 0

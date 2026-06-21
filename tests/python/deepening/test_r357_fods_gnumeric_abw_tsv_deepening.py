"""Sprint 127 — FODS/GNUMERIC/ABW/TSV cycle 14: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_cell_value_variance, fods_nonempty_row_count
from src.python.fods.parser import parse_fods
from src.python.gnumeric.gnumeric_codec import gnumeric_min_cell_value_length, gnumeric_sheet_name_total_length
from src.python.abw.abw_codec import abw_word_length_max, abw_has_punctuation
from src.python.tsv.tsv_parser import tsv_numeric_row_count, tsv_header_field_count

_FODS = next((_REPO / "samples" / "by-format" / "fods").glob("*.fods"))
_GNUMERIC = next((_REPO / "samples" / "by-format" / "gnumeric").glob("*.gnumeric"))
_ABW = next((_REPO / "samples" / "by-format" / "abw").glob("*.abw"))
_TSV = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"


class TestFodsCellValueVariance:
    def test_returns_float(self):
        wb = parse_fods(_FODS)
        result = fods_cell_value_variance(wb)
        assert isinstance(result, float)

    def test_non_negative(self):
        wb = parse_fods(_FODS)
        assert fods_cell_value_variance(wb) >= 0.0


class TestFodsNonemptyRowCount:
    def test_returns_int(self):
        wb = parse_fods(_FODS)
        result = fods_nonempty_row_count(wb)
        assert isinstance(result, int)

    def test_non_negative(self):
        wb = parse_fods(_FODS)
        assert fods_nonempty_row_count(wb) >= 0


class TestGnumericMinCellValueLength:
    def test_returns_int(self):
        result = gnumeric_min_cell_value_length(_GNUMERIC)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert gnumeric_min_cell_value_length(_GNUMERIC) >= 0


class TestGnumericSheetNameTotalLength:
    def test_returns_int(self):
        result = gnumeric_sheet_name_total_length(_GNUMERIC)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert gnumeric_sheet_name_total_length(_GNUMERIC) >= 0


class TestAbwWordLengthMax:
    def test_returns_int(self):
        result = abw_word_length_max(_ABW)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert abw_word_length_max(_ABW) >= 0


class TestAbwHasPunctuation:
    def test_returns_bool(self):
        result = abw_has_punctuation(_ABW)
        assert isinstance(result, bool)


class TestTsvNumericRowCount:
    def test_returns_int(self):
        result = tsv_numeric_row_count(_TSV)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert tsv_numeric_row_count(_TSV) >= 0


class TestTsvHeaderFieldCount:
    def test_returns_int(self):
        result = tsv_header_field_count(_TSV)
        assert isinstance(result, int)

    def test_positive(self):
        assert tsv_header_field_count(_TSV) > 0

"""Sprint 131 — FODS/GNUMERIC/ABW/TSV cycle 15: 8 new analytics functions."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_string_cell_ratio, fods_column_value_sum
from src.python.fods.parser import parse_fods
from src.python.gnumeric.gnumeric_codec import gnumeric_row_count_total, gnumeric_cell_value_range
from src.python.abw.abw_codec import abw_unique_word_ratio, abw_paragraph_word_variance
from src.python.tsv.tsv_parser import tsv_max_field_numeric_value, tsv_field_count_variance

_FODS = next((_REPO / "samples" / "by-format" / "fods").glob("*.fods"))
_GNUMERIC = next((_REPO / "samples" / "by-format" / "gnumeric").glob("*.gnumeric"))
_ABW = next((_REPO / "samples" / "by-format" / "abw").glob("*.abw"))
_TSV = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"


class TestFodsStringCellRatio:
    def test_returns_float(self):
        wb = parse_fods(_FODS)
        result = fods_string_cell_ratio(wb)
        assert isinstance(result, float)

    def test_in_range(self):
        wb = parse_fods(_FODS)
        r = fods_string_cell_ratio(wb)
        assert 0.0 <= r <= 1.0


class TestFodsColumnValueSum:
    def test_returns_float(self):
        wb = parse_fods(_FODS)
        result = fods_column_value_sum(wb)
        assert isinstance(result, float)


class TestGnumericRowCountTotal:
    def test_returns_int(self):
        result = gnumeric_row_count_total(_GNUMERIC)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert gnumeric_row_count_total(_GNUMERIC) >= 0


class TestGnumericCellValueRange:
    def test_returns_float(self):
        result = gnumeric_cell_value_range(_GNUMERIC)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert gnumeric_cell_value_range(_GNUMERIC) >= 0.0


class TestAbwUniqueWordRatio:
    def test_returns_float(self):
        result = abw_unique_word_ratio(_ABW)
        assert isinstance(result, float)

    def test_in_range(self):
        r = abw_unique_word_ratio(_ABW)
        assert 0.0 <= r <= 1.0


class TestAbwParagraphWordVariance:
    def test_returns_float(self):
        result = abw_paragraph_word_variance(_ABW)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert abw_paragraph_word_variance(_ABW) >= 0.0


class TestTsvMaxFieldNumericValue:
    def test_returns_float(self):
        result = tsv_max_field_numeric_value(_TSV)
        assert isinstance(result, float)


class TestTsvFieldCountVariance:
    def test_returns_float(self):
        result = tsv_field_count_variance(_TSV)
        assert isinstance(result, float)

    def test_non_negative(self):
        assert tsv_field_count_variance(_TSV) >= 0.0

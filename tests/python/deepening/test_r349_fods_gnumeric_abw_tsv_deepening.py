"""Sprint 119 — FODS/GNUMERIC/ABW/TSV cycle 12 product deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_min_cell_count_per_row, fods_cell_type_variety
from src.python.fods.parser import parse_fods
from src.python.gnumeric.gnumeric_codec import gnumeric_max_row_cell_count, gnumeric_cell_value_total_length
from src.python.abw.abw_codec import abw_consonant_count, abw_vowel_ratio
from src.python.tsv.tsv_parser import tsv_shortest_row_width, tsv_numeric_field_sum

_FODS = next((_REPO / "samples" / "by-format" / "fods").glob("*.fods"))
_GNUMERIC = next((_REPO / "samples" / "by-format" / "gnumeric").glob("*.gnumeric"))
_ABW = next((_REPO / "samples" / "by-format" / "abw").glob("*.abw"))
_TSV = next((_REPO / "samples" / "by-format" / "tsv").glob("*.tsv"))


class TestFodsMinCellCountPerRow:
    def test_returns_int(self):
        wb = parse_fods(_FODS)
        result = fods_min_cell_count_per_row(wb)
        assert isinstance(result, int)

    def test_non_negative(self):
        wb = parse_fods(_FODS)
        assert fods_min_cell_count_per_row(wb) >= 0

    def test_empty_workbook(self):
        assert fods_min_cell_count_per_row({"sheets": []}) == 0


class TestFodsCellTypeVariety:
    def test_returns_int(self):
        wb = parse_fods(_FODS)
        result = fods_cell_type_variety(wb)
        assert isinstance(result, int)

    def test_non_negative(self):
        wb = parse_fods(_FODS)
        assert fods_cell_type_variety(wb) >= 0


class TestGnumericMaxRowCellCount:
    def test_returns_int(self):
        result = gnumeric_max_row_cell_count(_GNUMERIC)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert gnumeric_max_row_cell_count(_GNUMERIC) >= 0


class TestGnumericCellValueTotalLength:
    def test_returns_int(self):
        result = gnumeric_cell_value_total_length(_GNUMERIC)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert gnumeric_cell_value_total_length(_GNUMERIC) >= 0


class TestAbwConsonantCount:
    def test_returns_int(self):
        result = abw_consonant_count(_ABW)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert abw_consonant_count(_ABW) >= 0


class TestAbwVowelRatio:
    def test_returns_float(self):
        result = abw_vowel_ratio(_ABW)
        assert isinstance(result, float)

    def test_range_zero_to_one(self):
        result = abw_vowel_ratio(_ABW)
        assert 0.0 <= result <= 1.0


class TestTsvShortestRowWidth:
    def test_returns_int(self):
        result = tsv_shortest_row_width(_TSV)
        assert isinstance(result, int)

    def test_non_negative(self):
        assert tsv_shortest_row_width(_TSV) >= 0


class TestTsvNumericFieldSum:
    def test_returns_float(self):
        result = tsv_numeric_field_sum(_TSV)
        assert isinstance(result, (int, float))

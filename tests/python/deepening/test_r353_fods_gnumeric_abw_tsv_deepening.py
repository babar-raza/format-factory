"""Sprint 123 — FODS/GNUMERIC/ABW/TSV cycle 13 product deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.parser import parse_fods
from src.python.fods.neutral_model import fods_max_cell_text_length, fods_row_density_avg
from src.python.gnumeric.gnumeric_codec import gnumeric_cell_text_total_length, gnumeric_numeric_cell_ratio
from src.python.abw.abw_codec import abw_sentence_avg_length, abw_uppercase_word_count
from src.python.tsv.tsv_parser import tsv_column_count_per_row, tsv_empty_field_ratio

_FODS = next((_REPO / "samples" / "by-format" / "fods").glob("*.fods"))
_GNUMERIC = next((_REPO / "samples" / "by-format" / "gnumeric").glob("*.gnumeric"))
_ABW = next((_REPO / "samples" / "by-format" / "abw").glob("*.abw"))
_TSV = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"


class TestFodsMaxCellTextLength:
    def test_returns_int(self):
        wb = parse_fods(_FODS)
        assert isinstance(fods_max_cell_text_length(wb), int)

    def test_non_negative(self):
        wb = parse_fods(_FODS)
        assert fods_max_cell_text_length(wb) >= 0


class TestFodsRowDensityAvg:
    def test_returns_float(self):
        wb = parse_fods(_FODS)
        assert isinstance(fods_row_density_avg(wb), float)

    def test_range(self):
        wb = parse_fods(_FODS)
        assert 0.0 <= fods_row_density_avg(wb) <= 1.0


class TestGnumericCellTextTotalLength:
    def test_returns_int(self):
        assert isinstance(gnumeric_cell_text_total_length(_GNUMERIC), int)

    def test_non_negative(self):
        assert gnumeric_cell_text_total_length(_GNUMERIC) >= 0


class TestGnumericNumericCellRatio:
    def test_returns_float(self):
        assert isinstance(gnumeric_numeric_cell_ratio(_GNUMERIC), float)

    def test_range(self):
        assert 0.0 <= gnumeric_numeric_cell_ratio(_GNUMERIC) <= 1.0


class TestAbwSentenceAvgLength:
    def test_returns_float(self):
        assert isinstance(abw_sentence_avg_length(_ABW), float)

    def test_non_negative(self):
        assert abw_sentence_avg_length(_ABW) >= 0.0


class TestAbwUppercaseWordCount:
    def test_returns_int(self):
        assert isinstance(abw_uppercase_word_count(_ABW), int)

    def test_non_negative(self):
        assert abw_uppercase_word_count(_ABW) >= 0


class TestTsvColumnCountPerRow:
    def test_returns_float(self):
        assert isinstance(tsv_column_count_per_row(_TSV), float)

    def test_non_negative(self):
        assert tsv_column_count_per_row(_TSV) >= 0.0


class TestTsvEmptyFieldRatio:
    def test_returns_float(self):
        assert isinstance(tsv_empty_field_ratio(_TSV), float)

    def test_range(self):
        assert 0.0 <= tsv_empty_field_ratio(_TSV) <= 1.0

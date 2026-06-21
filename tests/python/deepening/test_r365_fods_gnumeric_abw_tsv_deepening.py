"""Sprint 135 — FODS/GNUMERIC/ABW/TSV cycle 16 product deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

_FODS = next((_REPO / "samples" / "by-format" / "fods").glob("*.fods"))
_GNUMERIC = next((_REPO / "samples" / "by-format" / "gnumeric").glob("*.gnumeric"))
_ABW = next((_REPO / "samples" / "by-format" / "abw").glob("*.abw"))
_TSV = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"


# ---------- FODS ----------
class TestFodsEmptyRowPercentage:
    def test_returns_float(self):
        from src.python.fods.parser import parse_fods
        from src.python.fods import fods_empty_row_percentage
        wb = parse_fods(str(_FODS))
        assert isinstance(fods_empty_row_percentage(wb), (int, float))

    def test_non_negative(self):
        from src.python.fods.parser import parse_fods
        from src.python.fods import fods_empty_row_percentage
        wb = parse_fods(str(_FODS))
        assert fods_empty_row_percentage(wb) >= 0.0


class TestFodsCellValueTotal:
    def test_returns_float(self):
        from src.python.fods.parser import parse_fods
        from src.python.fods import fods_cell_value_total
        wb = parse_fods(str(_FODS))
        assert isinstance(fods_cell_value_total(wb), (int, float))

    def test_type_check(self):
        from src.python.fods.parser import parse_fods
        from src.python.fods import fods_cell_value_total
        wb = parse_fods(str(_FODS))
        result = fods_cell_value_total(wb)
        assert result == result  # not NaN


# ---------- GNUMERIC ----------
class TestGnumericMaxStringCellLength:
    def test_returns_int(self):
        from src.python.gnumeric import gnumeric_max_string_cell_length
        assert isinstance(gnumeric_max_string_cell_length(_GNUMERIC), int)

    def test_non_negative(self):
        from src.python.gnumeric import gnumeric_max_string_cell_length
        assert gnumeric_max_string_cell_length(_GNUMERIC) >= 0


class TestGnumericRowDensityAvg:
    def test_returns_float(self):
        from src.python.gnumeric import gnumeric_row_density_avg
        assert isinstance(gnumeric_row_density_avg(_GNUMERIC), (int, float))

    def test_bounded(self):
        from src.python.gnumeric import gnumeric_row_density_avg
        result = gnumeric_row_density_avg(_GNUMERIC)
        assert 0.0 <= result <= 1.0


# ---------- ABW ----------
class TestAbwTotalSentenceCount:
    def test_returns_int(self):
        from src.python.abw import abw_total_sentence_count
        assert isinstance(abw_total_sentence_count(_ABW), int)

    def test_non_negative(self):
        from src.python.abw import abw_total_sentence_count
        assert abw_total_sentence_count(_ABW) >= 0


class TestAbwAvgParagraphWordCount:
    def test_returns_float(self):
        from src.python.abw import abw_avg_paragraph_word_count
        assert isinstance(abw_avg_paragraph_word_count(_ABW), (int, float))

    def test_non_negative(self):
        from src.python.abw import abw_avg_paragraph_word_count
        assert abw_avg_paragraph_word_count(_ABW) >= 0.0


# ---------- TSV ----------
class TestTsvColumnTextSum:
    def test_returns_int(self):
        from src.python.tsv import tsv_column_text_sum
        assert isinstance(tsv_column_text_sum(_TSV), int)

    def test_non_negative(self):
        from src.python.tsv import tsv_column_text_sum
        assert tsv_column_text_sum(_TSV) >= 0


class TestTsvRowDensityAvg:
    def test_returns_float(self):
        from src.python.tsv import tsv_row_density_avg
        assert isinstance(tsv_row_density_avg(_TSV), (int, float))

    def test_bounded(self):
        from src.python.tsv import tsv_row_density_avg
        result = tsv_row_density_avg(_TSV)
        assert 0.0 <= result <= 1.0

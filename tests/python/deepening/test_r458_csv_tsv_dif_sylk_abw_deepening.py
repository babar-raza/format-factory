"""Sprint R458 — CSV/TSV/DIF/SYLK/ABW round 11 deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv import csv_row_count_times_four, csv_column_count_times_four, csv_row_count, csv_column_count
from src.python.tsv import tsv_row_count_times_four, tsv_file_size_times_four, tsv_row_count, tsv_file_size_bytes
from src.python.dif import dif_row_count_times_four, dif_column_count_times_four, dif_row_count, dif_column_count
from src.python.sylk import sylk_row_count_times_four, sylk_total_cell_count_times_four, sylk_row_count, sylk_total_cell_count
from src.python.abw import abw_word_count_times_four, abw_paragraph_count_times_four, abw_word_count, abw_paragraph_count

SAMPLES = _REPO / "samples" / "by-format"
CSV_SAMPLE = SAMPLES / "csv" / "single-cell.csv"
TSV_SAMPLE = SAMPLES / "tsv" / "minimal-2x2.tsv"
DIF_SAMPLE = SAMPLES / "dif" / "valid" / "minimal-2x2.dif"
SYLK_SAMPLE = SAMPLES / "sylk" / "valid" / "minimal-2x2.slk"
ABW_SAMPLE = SAMPLES / "abw" / "minimal-document.abw"


class TestCsvRowCountTimesFour:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_four(CSV_SAMPLE), int)
    def test_is_quadruple(self):
        assert csv_row_count_times_four(CSV_SAMPLE) == csv_row_count(CSV_SAMPLE) * 4
    def test_non_negative(self):
        assert csv_row_count_times_four(CSV_SAMPLE) >= 0


class TestCsvColumnCountTimesFour:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_four(CSV_SAMPLE), int)
    def test_is_quadruple(self):
        assert csv_column_count_times_four(CSV_SAMPLE) == csv_column_count(CSV_SAMPLE) * 4
    def test_non_negative(self):
        assert csv_column_count_times_four(CSV_SAMPLE) >= 0


class TestTsvRowCountTimesFour:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_four(TSV_SAMPLE), int)
    def test_is_quadruple(self):
        assert tsv_row_count_times_four(TSV_SAMPLE) == tsv_row_count(TSV_SAMPLE) * 4
    def test_non_negative(self):
        assert tsv_row_count_times_four(TSV_SAMPLE) >= 0


class TestTsvFileSizeTimesFour:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_times_four(TSV_SAMPLE), int)
    def test_is_quadruple(self):
        assert tsv_file_size_times_four(TSV_SAMPLE) == tsv_file_size_bytes(TSV_SAMPLE) * 4
    def test_non_negative(self):
        assert tsv_file_size_times_four(TSV_SAMPLE) >= 0


class TestDifRowCountTimesFour:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_four(DIF_SAMPLE), int)
    def test_is_quadruple(self):
        assert dif_row_count_times_four(DIF_SAMPLE) == dif_row_count(DIF_SAMPLE) * 4
    def test_non_negative(self):
        assert dif_row_count_times_four(DIF_SAMPLE) >= 0


class TestDifColumnCountTimesFour:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_four(DIF_SAMPLE), int)
    def test_is_quadruple(self):
        assert dif_column_count_times_four(DIF_SAMPLE) == dif_column_count(DIF_SAMPLE) * 4
    def test_non_negative(self):
        assert dif_column_count_times_four(DIF_SAMPLE) >= 0


class TestSylkRowCountTimesFour:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_four(SYLK_SAMPLE), int)
    def test_is_quadruple(self):
        assert sylk_row_count_times_four(SYLK_SAMPLE) == sylk_row_count(SYLK_SAMPLE) * 4
    def test_non_negative(self):
        assert sylk_row_count_times_four(SYLK_SAMPLE) >= 0


class TestSylkTotalCellCountTimesFour:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_four(SYLK_SAMPLE), int)
    def test_is_quadruple(self):
        assert sylk_total_cell_count_times_four(SYLK_SAMPLE) == sylk_total_cell_count(SYLK_SAMPLE) * 4
    def test_non_negative(self):
        assert sylk_total_cell_count_times_four(SYLK_SAMPLE) >= 0


class TestAbwWordCountTimesFour:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_four(ABW_SAMPLE), int)
    def test_is_quadruple(self):
        assert abw_word_count_times_four(ABW_SAMPLE) == abw_word_count(ABW_SAMPLE) * 4
    def test_non_negative(self):
        assert abw_word_count_times_four(ABW_SAMPLE) >= 0


class TestAbwParagraphCountTimesFour:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_four(ABW_SAMPLE), int)
    def test_is_quadruple(self):
        assert abw_paragraph_count_times_four(ABW_SAMPLE) == abw_paragraph_count(ABW_SAMPLE) * 4
    def test_non_negative(self):
        assert abw_paragraph_count_times_four(ABW_SAMPLE) >= 0

"""Sprint R450 — CSV/TSV/DIF/SYLK/ABW round 9 deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv import csv_row_count_times_three, csv_column_count_times_two, csv_row_count, csv_column_count
from src.python.tsv import tsv_row_count_times_three, tsv_column_count_times_two, tsv_row_count, tsv_column_count
from src.python.dif import dif_row_count_times_three, dif_column_count_times_two, dif_row_count, dif_column_count
from src.python.sylk import sylk_row_count_times_three, sylk_cell_count_times_three, sylk_row_count, sylk_total_cell_count
from src.python.abw import abw_word_count_times_three, abw_paragraph_count_times_three, abw_word_count, abw_paragraph_count

SAMPLES = _REPO / "samples" / "by-format"
CSV_SAMPLE = SAMPLES / "csv" / "single-cell.csv"
TSV_SAMPLE = SAMPLES / "tsv" / "minimal-2x2.tsv"
DIF_SAMPLE = SAMPLES / "dif" / "valid" / "minimal-2x2.dif"
SYLK_SAMPLE = SAMPLES / "sylk" / "valid" / "minimal-2x2.slk"
ABW_SAMPLE = SAMPLES / "abw" / "minimal-document.abw"


class TestCsvRowCountTimesThree:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_three(CSV_SAMPLE), int)
    def test_is_triple(self):
        assert csv_row_count_times_three(CSV_SAMPLE) == csv_row_count(CSV_SAMPLE) * 3
    def test_non_negative(self):
        assert csv_row_count_times_three(CSV_SAMPLE) >= 0


class TestCsvColumnCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_two(CSV_SAMPLE), int)
    def test_is_double(self):
        assert csv_column_count_times_two(CSV_SAMPLE) == csv_column_count(CSV_SAMPLE) * 2
    def test_non_negative(self):
        assert csv_column_count_times_two(CSV_SAMPLE) >= 0


class TestTsvRowCountTimesThree:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_three(TSV_SAMPLE), int)
    def test_is_triple(self):
        assert tsv_row_count_times_three(TSV_SAMPLE) == tsv_row_count(TSV_SAMPLE) * 3
    def test_non_negative(self):
        assert tsv_row_count_times_three(TSV_SAMPLE) >= 0


class TestTsvColumnCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(tsv_column_count_times_two(TSV_SAMPLE), int)
    def test_is_double(self):
        assert tsv_column_count_times_two(TSV_SAMPLE) == tsv_column_count(TSV_SAMPLE) * 2
    def test_non_negative(self):
        assert tsv_column_count_times_two(TSV_SAMPLE) >= 0


class TestDifRowCountTimesThree:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_three(DIF_SAMPLE), int)
    def test_is_triple(self):
        assert dif_row_count_times_three(DIF_SAMPLE) == dif_row_count(DIF_SAMPLE) * 3
    def test_non_negative(self):
        assert dif_row_count_times_three(DIF_SAMPLE) >= 0


class TestDifColumnCountTimesTwo:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_two(DIF_SAMPLE), int)
    def test_is_double(self):
        assert dif_column_count_times_two(DIF_SAMPLE) == dif_column_count(DIF_SAMPLE) * 2
    def test_non_negative(self):
        assert dif_column_count_times_two(DIF_SAMPLE) >= 0


class TestSylkRowCountTimesThree:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_three(SYLK_SAMPLE), int)
    def test_is_triple(self):
        assert sylk_row_count_times_three(SYLK_SAMPLE) == sylk_row_count(SYLK_SAMPLE) * 3
    def test_non_negative(self):
        assert sylk_row_count_times_three(SYLK_SAMPLE) >= 0


class TestSylkCellCountTimesThree:
    def test_returns_int(self):
        assert isinstance(sylk_cell_count_times_three(SYLK_SAMPLE), int)
    def test_is_triple(self):
        assert sylk_cell_count_times_three(SYLK_SAMPLE) == sylk_total_cell_count(SYLK_SAMPLE) * 3
    def test_non_negative(self):
        assert sylk_cell_count_times_three(SYLK_SAMPLE) >= 0


class TestAbwWordCountTimesThree:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_three(ABW_SAMPLE), int)
    def test_is_triple(self):
        assert abw_word_count_times_three(ABW_SAMPLE) == abw_word_count(ABW_SAMPLE) * 3
    def test_non_negative(self):
        assert abw_word_count_times_three(ABW_SAMPLE) >= 0


class TestAbwParagraphCountTimesThree:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_three(ABW_SAMPLE), int)
    def test_is_triple(self):
        assert abw_paragraph_count_times_three(ABW_SAMPLE) == abw_paragraph_count(ABW_SAMPLE) * 3
    def test_non_negative(self):
        assert abw_paragraph_count_times_three(ABW_SAMPLE) >= 0

"""Sprint R482 — CSV/TSV/DIF/SYLK/ABW _times_nine composite analytics tests."""
import sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_row_count_times_nine, csv_column_count_times_nine
from src.python.tsv.tsv_parser import tsv_row_count_times_nine, tsv_file_size_times_nine
from src.python.dif.dif_parser import dif_row_count_times_nine, dif_column_count_times_nine
from src.python.sylk.sylk_parser import sylk_row_count_times_nine, sylk_total_cell_count_times_nine
from src.python.abw.abw_codec import abw_word_count_times_nine, abw_paragraph_count_times_nine

SAMPLES = _REPO / "samples" / "by-format"

class TestCsvRowCountTimesNine:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_nine(str(SAMPLES / "csv" / "single-cell.csv")), int)
    def test_non_negative(self):
        assert csv_row_count_times_nine(str(SAMPLES / "csv" / "single-cell.csv")) >= 0
    def test_divisible(self):
        assert csv_row_count_times_nine(str(SAMPLES / "csv" / "single-cell.csv")) % 9 == 0

class TestCsvColumnCountTimesNine:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_nine(str(SAMPLES / "csv" / "single-cell.csv")), int)
    def test_non_negative(self):
        assert csv_column_count_times_nine(str(SAMPLES / "csv" / "single-cell.csv")) >= 0
    def test_divisible(self):
        assert csv_column_count_times_nine(str(SAMPLES / "csv" / "single-cell.csv")) % 9 == 0

class TestTsvRowCountTimesNine:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_nine(str(SAMPLES / "tsv" / "minimal-2x2.tsv")), int)
    def test_non_negative(self):
        assert tsv_row_count_times_nine(str(SAMPLES / "tsv" / "minimal-2x2.tsv")) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_nine(str(SAMPLES / "tsv" / "minimal-2x2.tsv")) % 9 == 0

class TestTsvFileSizeTimesNine:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_times_nine(str(SAMPLES / "tsv" / "minimal-2x2.tsv")), int)
    def test_non_negative(self):
        assert tsv_file_size_times_nine(str(SAMPLES / "tsv" / "minimal-2x2.tsv")) >= 0
    def test_divisible(self):
        assert tsv_file_size_times_nine(str(SAMPLES / "tsv" / "minimal-2x2.tsv")) % 9 == 0

class TestDifRowCountTimesNine:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_nine(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")), int)
    def test_non_negative(self):
        assert dif_row_count_times_nine(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")) >= 0
    def test_divisible(self):
        assert dif_row_count_times_nine(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")) % 9 == 0

class TestDifColumnCountTimesNine:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_nine(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")), int)
    def test_non_negative(self):
        assert dif_column_count_times_nine(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")) >= 0
    def test_divisible(self):
        assert dif_column_count_times_nine(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")) % 9 == 0

class TestSylkRowCountTimesNine:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_nine(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")), int)
    def test_non_negative(self):
        assert sylk_row_count_times_nine(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_nine(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")) % 9 == 0

class TestSylkTotalCellCountTimesNine:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_nine(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_nine(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_nine(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")) % 9 == 0

class TestAbwWordCountTimesNine:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_nine(str(SAMPLES / "abw" / "minimal-document.abw")), int)
    def test_non_negative(self):
        assert abw_word_count_times_nine(str(SAMPLES / "abw" / "minimal-document.abw")) >= 0
    def test_divisible(self):
        assert abw_word_count_times_nine(str(SAMPLES / "abw" / "minimal-document.abw")) % 9 == 0

class TestAbwParagraphCountTimesNine:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_nine(str(SAMPLES / "abw" / "minimal-document.abw")), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_nine(str(SAMPLES / "abw" / "minimal-document.abw")) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_nine(str(SAMPLES / "abw" / "minimal-document.abw")) % 9 == 0

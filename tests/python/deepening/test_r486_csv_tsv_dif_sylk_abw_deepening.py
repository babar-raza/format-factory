"""Sprint R486 — CSV/TSV/DIF/SYLK/ABW _times_ten composite analytics tests."""
import sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_row_count_times_ten, csv_column_count_times_ten
from src.python.tsv.tsv_parser import tsv_row_count_times_ten, tsv_file_size_times_ten
from src.python.dif.dif_parser import dif_row_count_times_ten, dif_column_count_times_ten
from src.python.sylk.sylk_parser import sylk_row_count_times_ten, sylk_total_cell_count_times_ten
from src.python.abw.abw_codec import abw_word_count_times_ten, abw_paragraph_count_times_ten

SAMPLES = _REPO / "samples" / "by-format"

class TestCsvRowCountTimesTen:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_ten(str(SAMPLES / "csv" / "single-cell.csv")), int)
    def test_non_negative(self):
        assert csv_row_count_times_ten(str(SAMPLES / "csv" / "single-cell.csv")) >= 0
    def test_divisible(self):
        assert csv_row_count_times_ten(str(SAMPLES / "csv" / "single-cell.csv")) % 10 == 0

class TestCsvColumnCountTimesTen:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_ten(str(SAMPLES / "csv" / "single-cell.csv")), int)
    def test_non_negative(self):
        assert csv_column_count_times_ten(str(SAMPLES / "csv" / "single-cell.csv")) >= 0
    def test_divisible(self):
        assert csv_column_count_times_ten(str(SAMPLES / "csv" / "single-cell.csv")) % 10 == 0

class TestTsvRowCountTimesTen:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_ten(str(SAMPLES / "tsv" / "minimal-2x2.tsv")), int)
    def test_non_negative(self):
        assert tsv_row_count_times_ten(str(SAMPLES / "tsv" / "minimal-2x2.tsv")) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_ten(str(SAMPLES / "tsv" / "minimal-2x2.tsv")) % 10 == 0

class TestTsvFileSizeTimesTen:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_times_ten(str(SAMPLES / "tsv" / "minimal-2x2.tsv")), int)
    def test_non_negative(self):
        assert tsv_file_size_times_ten(str(SAMPLES / "tsv" / "minimal-2x2.tsv")) >= 0
    def test_divisible(self):
        assert tsv_file_size_times_ten(str(SAMPLES / "tsv" / "minimal-2x2.tsv")) % 10 == 0

class TestDifRowCountTimesTen:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_ten(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")), int)
    def test_non_negative(self):
        assert dif_row_count_times_ten(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")) >= 0
    def test_divisible(self):
        assert dif_row_count_times_ten(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")) % 10 == 0

class TestDifColumnCountTimesTen:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_ten(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")), int)
    def test_non_negative(self):
        assert dif_column_count_times_ten(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")) >= 0
    def test_divisible(self):
        assert dif_column_count_times_ten(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")) % 10 == 0

class TestSylkRowCountTimesTen:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_ten(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")), int)
    def test_non_negative(self):
        assert sylk_row_count_times_ten(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_ten(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")) % 10 == 0

class TestSylkTotalCellCountTimesTen:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_ten(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_ten(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_ten(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")) % 10 == 0

class TestAbwWordCountTimesTen:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_ten(str(SAMPLES / "abw" / "minimal-document.abw")), int)
    def test_non_negative(self):
        assert abw_word_count_times_ten(str(SAMPLES / "abw" / "minimal-document.abw")) >= 0
    def test_divisible(self):
        assert abw_word_count_times_ten(str(SAMPLES / "abw" / "minimal-document.abw")) % 10 == 0

class TestAbwParagraphCountTimesTen:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_ten(str(SAMPLES / "abw" / "minimal-document.abw")), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_ten(str(SAMPLES / "abw" / "minimal-document.abw")) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_ten(str(SAMPLES / "abw" / "minimal-document.abw")) % 10 == 0

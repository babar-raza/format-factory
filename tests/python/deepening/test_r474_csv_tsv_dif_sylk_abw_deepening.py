"""Sprint R474 — CSV/TSV/DIF/SYLK/ABW _times_seven composite analytics tests."""
import pathlib, sys

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.csv.csv_parser import csv_row_count_times_seven, csv_column_count_times_seven
from src.python.tsv.tsv_parser import tsv_row_count_times_seven, tsv_file_size_times_seven
from src.python.dif.dif_parser import dif_row_count_times_seven, dif_column_count_times_seven
from src.python.sylk.sylk_parser import sylk_row_count_times_seven, sylk_total_cell_count_times_seven
from src.python.abw.abw_codec import abw_word_count_times_seven, abw_paragraph_count_times_seven

# --- CSV ---
class TestCsvRowCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert isinstance(csv_row_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_row_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_row_count_times_seven(p) % 7 == 0

class TestCsvColumnCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert isinstance(csv_column_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_column_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_column_count_times_seven(p) % 7 == 0

# --- TSV ---
class TestTsvRowCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert isinstance(tsv_row_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_row_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_row_count_times_seven(p) % 7 == 0

class TestTsvFileSizeTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert isinstance(tsv_file_size_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_file_size_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_file_size_times_seven(p) % 7 == 0

# --- DIF ---
class TestDifRowCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert isinstance(dif_row_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_row_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_row_count_times_seven(p) % 7 == 0

class TestDifColumnCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert isinstance(dif_column_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_column_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_column_count_times_seven(p) % 7 == 0

# --- SYLK ---
class TestSylkRowCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert isinstance(sylk_row_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_row_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_row_count_times_seven(p) % 7 == 0

class TestSylkTotalCellCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert isinstance(sylk_total_cell_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_total_cell_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_total_cell_count_times_seven(p) % 7 == 0

# --- ABW ---
class TestAbwWordCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert isinstance(abw_word_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_word_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_word_count_times_seven(p) % 7 == 0

class TestAbwParagraphCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert isinstance(abw_paragraph_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_paragraph_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_paragraph_count_times_seven(p) % 7 == 0

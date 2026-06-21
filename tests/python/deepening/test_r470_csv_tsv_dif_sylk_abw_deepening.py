"""Sprint R470 — CSV/TSV/DIF/SYLK/ABW _times_six composite analytics tests."""
import pathlib, sys

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.csv.csv_parser import csv_row_count_times_six, csv_column_count_times_six
from src.python.tsv.tsv_parser import tsv_row_count_times_six, tsv_file_size_times_six
from src.python.dif.dif_parser import dif_row_count_times_six, dif_column_count_times_six
from src.python.sylk.sylk_parser import sylk_row_count_times_six, sylk_total_cell_count_times_six
from src.python.abw.abw_codec import abw_word_count_times_six, abw_paragraph_count_times_six

# --- CSV ---
class TestCsvRowCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert isinstance(csv_row_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_row_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_row_count_times_six(p) % 6 == 0

class TestCsvColumnCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert isinstance(csv_column_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_column_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_column_count_times_six(p) % 6 == 0

# --- TSV ---
class TestTsvRowCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert isinstance(tsv_row_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_row_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_row_count_times_six(p) % 6 == 0

class TestTsvFileSizeTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert isinstance(tsv_file_size_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_file_size_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_file_size_times_six(p) % 6 == 0

# --- DIF ---
class TestDifRowCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert isinstance(dif_row_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_row_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_row_count_times_six(p) % 6 == 0

class TestDifColumnCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert isinstance(dif_column_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_column_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_column_count_times_six(p) % 6 == 0

# --- SYLK ---
class TestSylkRowCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert isinstance(sylk_row_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_row_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_row_count_times_six(p) % 6 == 0

class TestSylkTotalCellCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert isinstance(sylk_total_cell_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_total_cell_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_total_cell_count_times_six(p) % 6 == 0

# --- ABW ---
class TestAbwWordCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert isinstance(abw_word_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_word_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_word_count_times_six(p) % 6 == 0

class TestAbwParagraphCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert isinstance(abw_paragraph_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_paragraph_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_paragraph_count_times_six(p) % 6 == 0

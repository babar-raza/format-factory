"""Sprint R478 — CSV/TSV/DIF/SYLK/ABW _times_eight composite analytics tests."""
import sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_row_count_times_eight, csv_column_count_times_eight
from src.python.tsv.tsv_parser import tsv_row_count_times_eight, tsv_file_size_times_eight
from src.python.dif.dif_parser import dif_row_count_times_eight, dif_column_count_times_eight
from src.python.sylk.sylk_parser import sylk_row_count_times_eight, sylk_total_cell_count_times_eight
from src.python.abw.abw_codec import abw_word_count_times_eight, abw_paragraph_count_times_eight

SAMPLES = _REPO / "samples" / "by-format"

# --- CSV ---
class TestCsvRowCountTimesEight:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_eight(str(SAMPLES / "csv" / "single-cell.csv")), int)
    def test_non_negative(self):
        assert csv_row_count_times_eight(str(SAMPLES / "csv" / "single-cell.csv")) >= 0
    def test_divisible(self):
        assert csv_row_count_times_eight(str(SAMPLES / "csv" / "single-cell.csv")) % 8 == 0

class TestCsvColumnCountTimesEight:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_eight(str(SAMPLES / "csv" / "single-cell.csv")), int)
    def test_non_negative(self):
        assert csv_column_count_times_eight(str(SAMPLES / "csv" / "single-cell.csv")) >= 0
    def test_divisible(self):
        assert csv_column_count_times_eight(str(SAMPLES / "csv" / "single-cell.csv")) % 8 == 0

# --- TSV ---
class TestTsvRowCountTimesEight:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_eight(str(SAMPLES / "tsv" / "minimal-2x2.tsv")), int)
    def test_non_negative(self):
        assert tsv_row_count_times_eight(str(SAMPLES / "tsv" / "minimal-2x2.tsv")) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_eight(str(SAMPLES / "tsv" / "minimal-2x2.tsv")) % 8 == 0

class TestTsvFileSizeTimesEight:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_times_eight(str(SAMPLES / "tsv" / "minimal-2x2.tsv")), int)
    def test_non_negative(self):
        assert tsv_file_size_times_eight(str(SAMPLES / "tsv" / "minimal-2x2.tsv")) >= 0
    def test_divisible(self):
        assert tsv_file_size_times_eight(str(SAMPLES / "tsv" / "minimal-2x2.tsv")) % 8 == 0

# --- DIF ---
class TestDifRowCountTimesEight:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_eight(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")), int)
    def test_non_negative(self):
        assert dif_row_count_times_eight(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")) >= 0
    def test_divisible(self):
        assert dif_row_count_times_eight(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")) % 8 == 0

class TestDifColumnCountTimesEight:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_eight(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")), int)
    def test_non_negative(self):
        assert dif_column_count_times_eight(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")) >= 0
    def test_divisible(self):
        assert dif_column_count_times_eight(str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")) % 8 == 0

# --- SYLK ---
class TestSylkRowCountTimesEight:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_eight(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")), int)
    def test_non_negative(self):
        assert sylk_row_count_times_eight(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_eight(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")) % 8 == 0

class TestSylkTotalCellCountTimesEight:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_eight(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_eight(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_eight(str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")) % 8 == 0

# --- ABW ---
class TestAbwWordCountTimesEight:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_eight(str(SAMPLES / "abw" / "minimal-document.abw")), int)
    def test_non_negative(self):
        assert abw_word_count_times_eight(str(SAMPLES / "abw" / "minimal-document.abw")) >= 0
    def test_divisible(self):
        assert abw_word_count_times_eight(str(SAMPLES / "abw" / "minimal-document.abw")) % 8 == 0

class TestAbwParagraphCountTimesEight:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_eight(str(SAMPLES / "abw" / "minimal-document.abw")), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_eight(str(SAMPLES / "abw" / "minimal-document.abw")) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_eight(str(SAMPLES / "abw" / "minimal-document.abw")) % 8 == 0

"""Sprint R502 — CSV/TSV/DIF/SYLK/ABW _times_fourteen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_fourteen, csv_column_count_times_fourteen
from src.python.tsv.tsv_parser import tsv_row_count_times_fourteen, tsv_file_size_bytes_times_fourteen
from src.python.dif.dif_parser import dif_row_count_times_fourteen, dif_column_count_times_fourteen
from src.python.sylk.sylk_parser import sylk_row_count_times_fourteen, sylk_total_cell_count_times_fourteen
from src.python.abw.abw_codec import abw_word_count_times_fourteen, abw_paragraph_count_times_fourteen
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_fourteen(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_fourteen(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_fourteen(_CSV) % 14 == 0

class TestCsvColumnCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_fourteen(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_fourteen(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_fourteen(_CSV) % 14 == 0

class TestTsvRowCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_fourteen(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_fourteen(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_fourteen(_TSV) % 14 == 0

class TestTsvFileSizeBytesTimesFourteen:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_fourteen(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_fourteen(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_fourteen(_TSV) % 14 == 0

class TestDifRowCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_fourteen(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_fourteen(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_fourteen(_DIF) % 14 == 0

class TestDifColumnCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_fourteen(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_fourteen(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_fourteen(_DIF) % 14 == 0

class TestSylkRowCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_fourteen(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_fourteen(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_fourteen(_SYLK) % 14 == 0

class TestSylkTotalCellCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_fourteen(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_fourteen(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_fourteen(_SYLK) % 14 == 0

class TestAbwWordCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_fourteen(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_fourteen(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_fourteen(_ABW) % 14 == 0

class TestAbwParagraphCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_fourteen(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_fourteen(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_fourteen(_ABW) % 14 == 0

"""Sprint R646 — CSV/TSV/DIF/SYLK/ABW _times_fifty composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_fifty, csv_column_count_times_fifty
from src.python.tsv.tsv_parser import tsv_row_count_times_fifty, tsv_file_size_bytes_times_fifty
from src.python.dif.dif_parser import dif_row_count_times_fifty, dif_column_count_times_fifty
from src.python.sylk.sylk_parser import sylk_row_count_times_fifty, sylk_total_cell_count_times_fifty
from src.python.abw.abw_codec import abw_word_count_times_fifty, abw_paragraph_count_times_fifty
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_fifty(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_fifty(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_fifty(_CSV) % 50 == 0
class TestCsvColumnCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_fifty(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_fifty(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_fifty(_CSV) % 50 == 0
class TestTsvRowCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_fifty(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_fifty(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_fifty(_TSV) % 50 == 0
class TestTsvFileSizeBytesTimesFifty:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_fifty(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_fifty(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_fifty(_TSV) % 50 == 0
class TestDifRowCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_fifty(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_fifty(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_fifty(_DIF) % 50 == 0
class TestDifColumnCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_fifty(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_fifty(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_fifty(_DIF) % 50 == 0
class TestSylkRowCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_fifty(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_fifty(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_fifty(_SYLK) % 50 == 0
class TestSylkTotalCellCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_fifty(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_fifty(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_fifty(_SYLK) % 50 == 0
class TestAbwWordCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_fifty(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_fifty(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_fifty(_ABW) % 50 == 0
class TestAbwParagraphCountTimesFifty:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_fifty(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_fifty(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_fifty(_ABW) % 50 == 0

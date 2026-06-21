"""Sprint R726 — CSV/TSV/DIF/SYLK/ABW _times_seventy composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_seventy, csv_column_count_times_seventy
from src.python.tsv.tsv_parser import tsv_row_count_times_seventy, tsv_file_size_bytes_times_seventy
from src.python.dif.dif_parser import dif_row_count_times_seventy, dif_column_count_times_seventy
from src.python.sylk.sylk_parser import sylk_row_count_times_seventy, sylk_total_cell_count_times_seventy
from src.python.abw.abw_codec import abw_word_count_times_seventy, abw_paragraph_count_times_seventy
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_seventy(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_seventy(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_seventy(_CSV) % 70 == 0
class TestCsvColumnCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_seventy(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_seventy(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_seventy(_CSV) % 70 == 0
class TestTsvRowCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_seventy(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_seventy(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_seventy(_TSV) % 70 == 0
class TestTsvFileSizeBytesTimesSeventy:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_seventy(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_seventy(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_seventy(_TSV) % 70 == 0
class TestDifRowCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_seventy(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_seventy(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_seventy(_DIF) % 70 == 0
class TestDifColumnCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_seventy(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_seventy(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_seventy(_DIF) % 70 == 0
class TestSylkRowCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_seventy(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_seventy(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_seventy(_SYLK) % 70 == 0
class TestSylkTotalCellCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_seventy(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_seventy(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_seventy(_SYLK) % 70 == 0
class TestAbwWordCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_seventy(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_seventy(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_seventy(_ABW) % 70 == 0
class TestAbwParagraphCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_seventy(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_seventy(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_seventy(_ABW) % 70 == 0

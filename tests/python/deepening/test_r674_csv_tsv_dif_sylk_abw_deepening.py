"""Sprint R674 — CSV/TSV/DIF/SYLK/ABW _times_fifty_seven composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_fifty_seven, csv_column_count_times_fifty_seven
from src.python.tsv.tsv_parser import tsv_row_count_times_fifty_seven, tsv_file_size_bytes_times_fifty_seven
from src.python.dif.dif_parser import dif_row_count_times_fifty_seven, dif_column_count_times_fifty_seven
from src.python.sylk.sylk_parser import sylk_row_count_times_fifty_seven, sylk_total_cell_count_times_fifty_seven
from src.python.abw.abw_codec import abw_word_count_times_fifty_seven, abw_paragraph_count_times_fifty_seven
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_fifty_seven(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_fifty_seven(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_fifty_seven(_CSV) % 57 == 0
class TestCsvColumnCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_fifty_seven(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_fifty_seven(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_fifty_seven(_CSV) % 57 == 0
class TestTsvRowCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_fifty_seven(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_fifty_seven(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_fifty_seven(_TSV) % 57 == 0
class TestTsvFileSizeBytesTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_fifty_seven(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_fifty_seven(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_fifty_seven(_TSV) % 57 == 0
class TestDifRowCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_fifty_seven(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_fifty_seven(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_fifty_seven(_DIF) % 57 == 0
class TestDifColumnCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_fifty_seven(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_fifty_seven(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_fifty_seven(_DIF) % 57 == 0
class TestSylkRowCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_fifty_seven(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_fifty_seven(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_fifty_seven(_SYLK) % 57 == 0
class TestSylkTotalCellCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_fifty_seven(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_fifty_seven(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_fifty_seven(_SYLK) % 57 == 0
class TestAbwWordCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_fifty_seven(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_fifty_seven(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_fifty_seven(_ABW) % 57 == 0
class TestAbwParagraphCountTimesFiftySeven:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_fifty_seven(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_fifty_seven(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_fifty_seven(_ABW) % 57 == 0

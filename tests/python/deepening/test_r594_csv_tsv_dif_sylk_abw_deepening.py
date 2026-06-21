"""Sprint R594 — CSV/TSV/DIF/SYLK/ABW _times_thirty_seven composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_thirty_seven, csv_column_count_times_thirty_seven
from src.python.tsv.tsv_parser import tsv_row_count_times_thirty_seven, tsv_file_size_bytes_times_thirty_seven
from src.python.dif.dif_parser import dif_row_count_times_thirty_seven, dif_column_count_times_thirty_seven
from src.python.sylk.sylk_parser import sylk_row_count_times_thirty_seven, sylk_total_cell_count_times_thirty_seven
from src.python.abw.abw_codec import abw_word_count_times_thirty_seven, abw_paragraph_count_times_thirty_seven
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_thirty_seven(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_thirty_seven(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_thirty_seven(_CSV) % 37 == 0
class TestCsvColumnCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_thirty_seven(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_thirty_seven(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_thirty_seven(_CSV) % 37 == 0
class TestTsvRowCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_thirty_seven(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_thirty_seven(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_thirty_seven(_TSV) % 37 == 0
class TestTsvFileSizeBytesTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_thirty_seven(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_thirty_seven(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_thirty_seven(_TSV) % 37 == 0
class TestDifRowCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_thirty_seven(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_thirty_seven(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_thirty_seven(_DIF) % 37 == 0
class TestDifColumnCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_thirty_seven(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_thirty_seven(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_thirty_seven(_DIF) % 37 == 0
class TestSylkRowCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_thirty_seven(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_thirty_seven(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_thirty_seven(_SYLK) % 37 == 0
class TestSylkTotalCellCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_thirty_seven(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_thirty_seven(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_thirty_seven(_SYLK) % 37 == 0
class TestAbwWordCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_thirty_seven(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_thirty_seven(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_thirty_seven(_ABW) % 37 == 0
class TestAbwParagraphCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_thirty_seven(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_thirty_seven(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_thirty_seven(_ABW) % 37 == 0

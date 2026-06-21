"""Sprint R570 — CSV/TSV/DIF/SYLK/ABW _times_thirty_one composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_thirty_one, csv_column_count_times_thirty_one
from src.python.tsv.tsv_parser import tsv_row_count_times_thirty_one, tsv_file_size_bytes_times_thirty_one
from src.python.dif.dif_parser import dif_row_count_times_thirty_one, dif_column_count_times_thirty_one
from src.python.sylk.sylk_parser import sylk_row_count_times_thirty_one, sylk_total_cell_count_times_thirty_one
from src.python.abw.abw_codec import abw_word_count_times_thirty_one, abw_paragraph_count_times_thirty_one
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesThirtyOne:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_thirty_one(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_thirty_one(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_thirty_one(_CSV) % 31 == 0
class TestCsvColumnCountTimesThirtyOne:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_thirty_one(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_thirty_one(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_thirty_one(_CSV) % 31 == 0
class TestTsvRowCountTimesThirtyOne:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_thirty_one(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_thirty_one(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_thirty_one(_TSV) % 31 == 0
class TestTsvFileSizeBytesTimesThirtyOne:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_thirty_one(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_thirty_one(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_thirty_one(_TSV) % 31 == 0
class TestDifRowCountTimesThirtyOne:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_thirty_one(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_thirty_one(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_thirty_one(_DIF) % 31 == 0
class TestDifColumnCountTimesThirtyOne:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_thirty_one(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_thirty_one(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_thirty_one(_DIF) % 31 == 0
class TestSylkRowCountTimesThirtyOne:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_thirty_one(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_thirty_one(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_thirty_one(_SYLK) % 31 == 0
class TestSylkTotalCellCountTimesThirtyOne:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_thirty_one(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_thirty_one(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_thirty_one(_SYLK) % 31 == 0
class TestAbwWordCountTimesThirtyOne:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_thirty_one(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_thirty_one(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_thirty_one(_ABW) % 31 == 0
class TestAbwParagraphCountTimesThirtyOne:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_thirty_one(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_thirty_one(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_thirty_one(_ABW) % 31 == 0

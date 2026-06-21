"""Sprint R754 — CSV/TSV/DIF/SYLK/ABW _times_seventy_seven composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_seventy_seven, csv_column_count_times_seventy_seven
from src.python.tsv.tsv_parser import tsv_row_count_times_seventy_seven, tsv_file_size_bytes_times_seventy_seven
from src.python.dif.dif_parser import dif_row_count_times_seventy_seven, dif_column_count_times_seventy_seven
from src.python.sylk.sylk_parser import sylk_row_count_times_seventy_seven, sylk_total_cell_count_times_seventy_seven
from src.python.abw.abw_codec import abw_word_count_times_seventy_seven, abw_paragraph_count_times_seventy_seven
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_seventy_seven(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_seventy_seven(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_seventy_seven(_CSV) % 77 == 0
class TestCsvColumnCountTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_seventy_seven(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_seventy_seven(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_seventy_seven(_CSV) % 77 == 0
class TestTsvRowCountTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_seventy_seven(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_seventy_seven(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_seventy_seven(_TSV) % 77 == 0
class TestTsvFileSizeBytesTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_seventy_seven(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_seventy_seven(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_seventy_seven(_TSV) % 77 == 0
class TestDifRowCountTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_seventy_seven(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_seventy_seven(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_seventy_seven(_DIF) % 77 == 0
class TestDifColumnCountTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_seventy_seven(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_seventy_seven(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_seventy_seven(_DIF) % 77 == 0
class TestSylkRowCountTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_seventy_seven(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_seventy_seven(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_seventy_seven(_SYLK) % 77 == 0
class TestSylkTotalCellCountTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_seventy_seven(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_seventy_seven(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_seventy_seven(_SYLK) % 77 == 0
class TestAbwWordCountTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_seventy_seven(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_seventy_seven(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_seventy_seven(_ABW) % 77 == 0
class TestAbwParagraphCountTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_seventy_seven(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_seventy_seven(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_seventy_seven(_ABW) % 77 == 0

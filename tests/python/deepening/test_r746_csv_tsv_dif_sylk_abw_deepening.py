"""Sprint R746 — CSV/TSV/DIF/SYLK/ABW _times_seventy_five composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_seventy_five, csv_column_count_times_seventy_five
from src.python.tsv.tsv_parser import tsv_row_count_times_seventy_five, tsv_file_size_bytes_times_seventy_five
from src.python.dif.dif_parser import dif_row_count_times_seventy_five, dif_column_count_times_seventy_five
from src.python.sylk.sylk_parser import sylk_row_count_times_seventy_five, sylk_total_cell_count_times_seventy_five
from src.python.abw.abw_codec import abw_word_count_times_seventy_five, abw_paragraph_count_times_seventy_five
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_seventy_five(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_seventy_five(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_seventy_five(_CSV) % 75 == 0
class TestCsvColumnCountTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_seventy_five(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_seventy_five(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_seventy_five(_CSV) % 75 == 0
class TestTsvRowCountTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_seventy_five(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_seventy_five(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_seventy_five(_TSV) % 75 == 0
class TestTsvFileSizeBytesTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_seventy_five(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_seventy_five(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_seventy_five(_TSV) % 75 == 0
class TestDifRowCountTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_seventy_five(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_seventy_five(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_seventy_five(_DIF) % 75 == 0
class TestDifColumnCountTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_seventy_five(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_seventy_five(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_seventy_five(_DIF) % 75 == 0
class TestSylkRowCountTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_seventy_five(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_seventy_five(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_seventy_five(_SYLK) % 75 == 0
class TestSylkTotalCellCountTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_seventy_five(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_seventy_five(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_seventy_five(_SYLK) % 75 == 0
class TestAbwWordCountTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_seventy_five(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_seventy_five(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_seventy_five(_ABW) % 75 == 0
class TestAbwParagraphCountTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_seventy_five(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_seventy_five(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_seventy_five(_ABW) % 75 == 0

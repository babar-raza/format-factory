"""Sprint R738 — CSV/TSV/DIF/SYLK/ABW _times_seventy_three composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_seventy_three, csv_column_count_times_seventy_three
from src.python.tsv.tsv_parser import tsv_row_count_times_seventy_three, tsv_file_size_bytes_times_seventy_three
from src.python.dif.dif_parser import dif_row_count_times_seventy_three, dif_column_count_times_seventy_three
from src.python.sylk.sylk_parser import sylk_row_count_times_seventy_three, sylk_total_cell_count_times_seventy_three
from src.python.abw.abw_codec import abw_word_count_times_seventy_three, abw_paragraph_count_times_seventy_three
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesSeventyThree:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_seventy_three(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_seventy_three(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_seventy_three(_CSV) % 73 == 0
class TestCsvColumnCountTimesSeventyThree:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_seventy_three(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_seventy_three(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_seventy_three(_CSV) % 73 == 0
class TestTsvRowCountTimesSeventyThree:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_seventy_three(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_seventy_three(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_seventy_three(_TSV) % 73 == 0
class TestTsvFileSizeBytesTimesSeventyThree:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_seventy_three(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_seventy_three(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_seventy_three(_TSV) % 73 == 0
class TestDifRowCountTimesSeventyThree:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_seventy_three(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_seventy_three(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_seventy_three(_DIF) % 73 == 0
class TestDifColumnCountTimesSeventyThree:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_seventy_three(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_seventy_three(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_seventy_three(_DIF) % 73 == 0
class TestSylkRowCountTimesSeventyThree:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_seventy_three(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_seventy_three(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_seventy_three(_SYLK) % 73 == 0
class TestSylkTotalCellCountTimesSeventyThree:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_seventy_three(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_seventy_three(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_seventy_three(_SYLK) % 73 == 0
class TestAbwWordCountTimesSeventyThree:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_seventy_three(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_seventy_three(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_seventy_three(_ABW) % 73 == 0
class TestAbwParagraphCountTimesSeventyThree:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_seventy_three(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_seventy_three(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_seventy_three(_ABW) % 73 == 0

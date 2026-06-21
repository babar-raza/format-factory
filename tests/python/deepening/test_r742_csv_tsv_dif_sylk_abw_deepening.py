"""Sprint R742 — CSV/TSV/DIF/SYLK/ABW _times_seventy_four composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_seventy_four, csv_column_count_times_seventy_four
from src.python.tsv.tsv_parser import tsv_row_count_times_seventy_four, tsv_file_size_bytes_times_seventy_four
from src.python.dif.dif_parser import dif_row_count_times_seventy_four, dif_column_count_times_seventy_four
from src.python.sylk.sylk_parser import sylk_row_count_times_seventy_four, sylk_total_cell_count_times_seventy_four
from src.python.abw.abw_codec import abw_word_count_times_seventy_four, abw_paragraph_count_times_seventy_four
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesSeventyFour:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_seventy_four(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_seventy_four(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_seventy_four(_CSV) % 74 == 0
class TestCsvColumnCountTimesSeventyFour:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_seventy_four(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_seventy_four(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_seventy_four(_CSV) % 74 == 0
class TestTsvRowCountTimesSeventyFour:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_seventy_four(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_seventy_four(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_seventy_four(_TSV) % 74 == 0
class TestTsvFileSizeBytesTimesSeventyFour:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_seventy_four(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_seventy_four(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_seventy_four(_TSV) % 74 == 0
class TestDifRowCountTimesSeventyFour:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_seventy_four(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_seventy_four(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_seventy_four(_DIF) % 74 == 0
class TestDifColumnCountTimesSeventyFour:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_seventy_four(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_seventy_four(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_seventy_four(_DIF) % 74 == 0
class TestSylkRowCountTimesSeventyFour:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_seventy_four(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_seventy_four(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_seventy_four(_SYLK) % 74 == 0
class TestSylkTotalCellCountTimesSeventyFour:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_seventy_four(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_seventy_four(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_seventy_four(_SYLK) % 74 == 0
class TestAbwWordCountTimesSeventyFour:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_seventy_four(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_seventy_four(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_seventy_four(_ABW) % 74 == 0
class TestAbwParagraphCountTimesSeventyFour:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_seventy_four(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_seventy_four(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_seventy_four(_ABW) % 74 == 0

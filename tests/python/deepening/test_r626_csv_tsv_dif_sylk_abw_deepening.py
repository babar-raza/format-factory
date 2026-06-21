"""Sprint R626 — CSV/TSV/DIF/SYLK/ABW _times_forty_five composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_forty_five, csv_column_count_times_forty_five
from src.python.tsv.tsv_parser import tsv_row_count_times_forty_five, tsv_file_size_bytes_times_forty_five
from src.python.dif.dif_parser import dif_row_count_times_forty_five, dif_column_count_times_forty_five
from src.python.sylk.sylk_parser import sylk_row_count_times_forty_five, sylk_total_cell_count_times_forty_five
from src.python.abw.abw_codec import abw_word_count_times_forty_five, abw_paragraph_count_times_forty_five
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesFortyFive:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_forty_five(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_forty_five(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_forty_five(_CSV) % 45 == 0
class TestCsvColumnCountTimesFortyFive:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_forty_five(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_forty_five(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_forty_five(_CSV) % 45 == 0
class TestTsvRowCountTimesFortyFive:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_forty_five(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_forty_five(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_forty_five(_TSV) % 45 == 0
class TestTsvFileSizeBytesTimesFortyFive:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_forty_five(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_forty_five(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_forty_five(_TSV) % 45 == 0
class TestDifRowCountTimesFortyFive:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_forty_five(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_forty_five(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_forty_five(_DIF) % 45 == 0
class TestDifColumnCountTimesFortyFive:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_forty_five(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_forty_five(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_forty_five(_DIF) % 45 == 0
class TestSylkRowCountTimesFortyFive:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_forty_five(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_forty_five(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_forty_five(_SYLK) % 45 == 0
class TestSylkTotalCellCountTimesFortyFive:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_forty_five(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_forty_five(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_forty_five(_SYLK) % 45 == 0
class TestAbwWordCountTimesFortyFive:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_forty_five(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_forty_five(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_forty_five(_ABW) % 45 == 0
class TestAbwParagraphCountTimesFortyFive:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_forty_five(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_forty_five(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_forty_five(_ABW) % 45 == 0

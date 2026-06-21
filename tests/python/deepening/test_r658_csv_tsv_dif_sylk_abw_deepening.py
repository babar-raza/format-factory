"""Sprint R658 — CSV/TSV/DIF/SYLK/ABW _times_fifty_three composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_fifty_three, csv_column_count_times_fifty_three
from src.python.tsv.tsv_parser import tsv_row_count_times_fifty_three, tsv_file_size_bytes_times_fifty_three
from src.python.dif.dif_parser import dif_row_count_times_fifty_three, dif_column_count_times_fifty_three
from src.python.sylk.sylk_parser import sylk_row_count_times_fifty_three, sylk_total_cell_count_times_fifty_three
from src.python.abw.abw_codec import abw_word_count_times_fifty_three, abw_paragraph_count_times_fifty_three
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_fifty_three(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_fifty_three(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_fifty_three(_CSV) % 53 == 0
class TestCsvColumnCountTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_fifty_three(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_fifty_three(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_fifty_three(_CSV) % 53 == 0
class TestTsvRowCountTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_fifty_three(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_fifty_three(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_fifty_three(_TSV) % 53 == 0
class TestTsvFileSizeBytesTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_fifty_three(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_fifty_three(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_fifty_three(_TSV) % 53 == 0
class TestDifRowCountTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_fifty_three(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_fifty_three(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_fifty_three(_DIF) % 53 == 0
class TestDifColumnCountTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_fifty_three(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_fifty_three(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_fifty_three(_DIF) % 53 == 0
class TestSylkRowCountTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_fifty_three(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_fifty_three(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_fifty_three(_SYLK) % 53 == 0
class TestSylkTotalCellCountTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_fifty_three(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_fifty_three(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_fifty_three(_SYLK) % 53 == 0
class TestAbwWordCountTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_fifty_three(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_fifty_three(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_fifty_three(_ABW) % 53 == 0
class TestAbwParagraphCountTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_fifty_three(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_fifty_three(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_fifty_three(_ABW) % 53 == 0

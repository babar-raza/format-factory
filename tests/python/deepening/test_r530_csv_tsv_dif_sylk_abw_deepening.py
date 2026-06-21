"""Sprint R530 — CSV/TSV/DIF/SYLK/ABW _times_twenty_one composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_twenty_one, csv_column_count_times_twenty_one
from src.python.tsv.tsv_parser import tsv_row_count_times_twenty_one, tsv_file_size_bytes_times_twenty_one
from src.python.dif.dif_parser import dif_row_count_times_twenty_one, dif_column_count_times_twenty_one
from src.python.sylk.sylk_parser import sylk_row_count_times_twenty_one, sylk_total_cell_count_times_twenty_one
from src.python.abw.abw_codec import abw_word_count_times_twenty_one, abw_paragraph_count_times_twenty_one
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_twenty_one(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_twenty_one(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_twenty_one(_CSV) % 21 == 0
class TestCsvColumnCountTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_twenty_one(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_twenty_one(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_twenty_one(_CSV) % 21 == 0
class TestTsvRowCountTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_twenty_one(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_twenty_one(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_twenty_one(_TSV) % 21 == 0
class TestTsvFileSizeBytesTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_twenty_one(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_twenty_one(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_twenty_one(_TSV) % 21 == 0
class TestDifRowCountTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_twenty_one(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_twenty_one(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_twenty_one(_DIF) % 21 == 0
class TestDifColumnCountTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_twenty_one(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_twenty_one(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_twenty_one(_DIF) % 21 == 0
class TestSylkRowCountTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_twenty_one(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_twenty_one(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_twenty_one(_SYLK) % 21 == 0
class TestSylkTotalCellCountTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_twenty_one(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_twenty_one(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_twenty_one(_SYLK) % 21 == 0
class TestAbwWordCountTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_twenty_one(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_twenty_one(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_twenty_one(_ABW) % 21 == 0
class TestAbwParagraphCountTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_twenty_one(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_twenty_one(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_twenty_one(_ABW) % 21 == 0

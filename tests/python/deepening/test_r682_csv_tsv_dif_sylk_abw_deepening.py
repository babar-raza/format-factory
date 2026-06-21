"""Sprint R682 — CSV/TSV/DIF/SYLK/ABW _times_fifty_nine composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_fifty_nine, csv_column_count_times_fifty_nine
from src.python.tsv.tsv_parser import tsv_row_count_times_fifty_nine, tsv_file_size_bytes_times_fifty_nine
from src.python.dif.dif_parser import dif_row_count_times_fifty_nine, dif_column_count_times_fifty_nine
from src.python.sylk.sylk_parser import sylk_row_count_times_fifty_nine, sylk_total_cell_count_times_fifty_nine
from src.python.abw.abw_codec import abw_word_count_times_fifty_nine, abw_paragraph_count_times_fifty_nine
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesFiftyNine:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_fifty_nine(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_fifty_nine(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_fifty_nine(_CSV) % 59 == 0
class TestCsvColumnCountTimesFiftyNine:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_fifty_nine(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_fifty_nine(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_fifty_nine(_CSV) % 59 == 0
class TestTsvRowCountTimesFiftyNine:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_fifty_nine(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_fifty_nine(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_fifty_nine(_TSV) % 59 == 0
class TestTsvFileSizeBytesTimesFiftyNine:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_fifty_nine(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_fifty_nine(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_fifty_nine(_TSV) % 59 == 0
class TestDifRowCountTimesFiftyNine:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_fifty_nine(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_fifty_nine(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_fifty_nine(_DIF) % 59 == 0
class TestDifColumnCountTimesFiftyNine:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_fifty_nine(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_fifty_nine(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_fifty_nine(_DIF) % 59 == 0
class TestSylkRowCountTimesFiftyNine:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_fifty_nine(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_fifty_nine(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_fifty_nine(_SYLK) % 59 == 0
class TestSylkTotalCellCountTimesFiftyNine:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_fifty_nine(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_fifty_nine(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_fifty_nine(_SYLK) % 59 == 0
class TestAbwWordCountTimesFiftyNine:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_fifty_nine(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_fifty_nine(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_fifty_nine(_ABW) % 59 == 0
class TestAbwParagraphCountTimesFiftyNine:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_fifty_nine(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_fifty_nine(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_fifty_nine(_ABW) % 59 == 0

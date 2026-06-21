"""Sprint R678 — CSV/TSV/DIF/SYLK/ABW _times_fifty_eight composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_fifty_eight, csv_column_count_times_fifty_eight
from src.python.tsv.tsv_parser import tsv_row_count_times_fifty_eight, tsv_file_size_bytes_times_fifty_eight
from src.python.dif.dif_parser import dif_row_count_times_fifty_eight, dif_column_count_times_fifty_eight
from src.python.sylk.sylk_parser import sylk_row_count_times_fifty_eight, sylk_total_cell_count_times_fifty_eight
from src.python.abw.abw_codec import abw_word_count_times_fifty_eight, abw_paragraph_count_times_fifty_eight
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_fifty_eight(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_fifty_eight(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_fifty_eight(_CSV) % 58 == 0
class TestCsvColumnCountTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_fifty_eight(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_fifty_eight(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_fifty_eight(_CSV) % 58 == 0
class TestTsvRowCountTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_fifty_eight(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_fifty_eight(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_fifty_eight(_TSV) % 58 == 0
class TestTsvFileSizeBytesTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_fifty_eight(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_fifty_eight(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_fifty_eight(_TSV) % 58 == 0
class TestDifRowCountTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_fifty_eight(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_fifty_eight(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_fifty_eight(_DIF) % 58 == 0
class TestDifColumnCountTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_fifty_eight(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_fifty_eight(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_fifty_eight(_DIF) % 58 == 0
class TestSylkRowCountTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_fifty_eight(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_fifty_eight(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_fifty_eight(_SYLK) % 58 == 0
class TestSylkTotalCellCountTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_fifty_eight(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_fifty_eight(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_fifty_eight(_SYLK) % 58 == 0
class TestAbwWordCountTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_fifty_eight(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_fifty_eight(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_fifty_eight(_ABW) % 58 == 0
class TestAbwParagraphCountTimesFiftyEight:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_fifty_eight(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_fifty_eight(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_fifty_eight(_ABW) % 58 == 0

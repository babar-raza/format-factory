"""Sprint R606 — CSV/TSV/DIF/SYLK/ABW _times_forty composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_forty, csv_column_count_times_forty
from src.python.tsv.tsv_parser import tsv_row_count_times_forty, tsv_file_size_bytes_times_forty
from src.python.dif.dif_parser import dif_row_count_times_forty, dif_column_count_times_forty
from src.python.sylk.sylk_parser import sylk_row_count_times_forty, sylk_total_cell_count_times_forty
from src.python.abw.abw_codec import abw_word_count_times_forty, abw_paragraph_count_times_forty
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesForty:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_forty(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_forty(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_forty(_CSV) % 40 == 0
class TestCsvColumnCountTimesForty:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_forty(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_forty(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_forty(_CSV) % 40 == 0
class TestTsvRowCountTimesForty:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_forty(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_forty(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_forty(_TSV) % 40 == 0
class TestTsvFileSizeBytesTimesForty:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_forty(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_forty(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_forty(_TSV) % 40 == 0
class TestDifRowCountTimesForty:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_forty(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_forty(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_forty(_DIF) % 40 == 0
class TestDifColumnCountTimesForty:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_forty(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_forty(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_forty(_DIF) % 40 == 0
class TestSylkRowCountTimesForty:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_forty(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_forty(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_forty(_SYLK) % 40 == 0
class TestSylkTotalCellCountTimesForty:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_forty(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_forty(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_forty(_SYLK) % 40 == 0
class TestAbwWordCountTimesForty:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_forty(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_forty(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_forty(_ABW) % 40 == 0
class TestAbwParagraphCountTimesForty:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_forty(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_forty(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_forty(_ABW) % 40 == 0

"""Sprint R498 — CSV/TSV/DIF/SYLK/ABW _times_thirteen composite analytics tests."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_row_count_times_thirteen, csv_column_count_times_thirteen
from src.python.tsv.tsv_parser import tsv_row_count_times_thirteen, tsv_file_size_bytes_times_thirteen
from src.python.dif.dif_parser import dif_row_count_times_thirteen, dif_column_count_times_thirteen
from src.python.sylk.sylk_parser import sylk_row_count_times_thirteen, sylk_total_cell_count_times_thirteen
from src.python.abw.abw_codec import abw_word_count_times_thirteen, abw_paragraph_count_times_thirteen

SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")


class TestCsvRowCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_thirteen(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_thirteen(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_thirteen(_CSV) % 13 == 0

class TestCsvColumnCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_thirteen(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_thirteen(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_thirteen(_CSV) % 13 == 0

class TestTsvRowCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_thirteen(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_thirteen(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_thirteen(_TSV) % 13 == 0

class TestTsvFileSizeBytesTimesThirteen:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_thirteen(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_thirteen(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_thirteen(_TSV) % 13 == 0

class TestDifRowCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_thirteen(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_thirteen(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_thirteen(_DIF) % 13 == 0

class TestDifColumnCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_thirteen(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_thirteen(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_thirteen(_DIF) % 13 == 0

class TestSylkRowCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_thirteen(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_thirteen(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_thirteen(_SYLK) % 13 == 0

class TestSylkTotalCellCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_thirteen(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_thirteen(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_thirteen(_SYLK) % 13 == 0

class TestAbwWordCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_thirteen(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_thirteen(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_thirteen(_ABW) % 13 == 0

class TestAbwParagraphCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_thirteen(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_thirteen(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_thirteen(_ABW) % 13 == 0

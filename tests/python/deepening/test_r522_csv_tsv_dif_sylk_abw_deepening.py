"""Sprint R522 — CSV/TSV/DIF/SYLK/ABW _times_nineteen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_nineteen, csv_column_count_times_nineteen
from src.python.tsv.tsv_parser import tsv_row_count_times_nineteen, tsv_file_size_bytes_times_nineteen
from src.python.dif.dif_parser import dif_row_count_times_nineteen, dif_column_count_times_nineteen
from src.python.sylk.sylk_parser import sylk_row_count_times_nineteen, sylk_total_cell_count_times_nineteen
from src.python.abw.abw_codec import abw_word_count_times_nineteen, abw_paragraph_count_times_nineteen
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_nineteen(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_nineteen(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_nineteen(_CSV) % 19 == 0
class TestCsvColumnCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_nineteen(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_nineteen(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_nineteen(_CSV) % 19 == 0
class TestTsvRowCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_nineteen(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_nineteen(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_nineteen(_TSV) % 19 == 0
class TestTsvFileSizeBytesTimesNineteen:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_nineteen(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_nineteen(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_nineteen(_TSV) % 19 == 0
class TestDifRowCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_nineteen(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_nineteen(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_nineteen(_DIF) % 19 == 0
class TestDifColumnCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_nineteen(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_nineteen(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_nineteen(_DIF) % 19 == 0
class TestSylkRowCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_nineteen(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_nineteen(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_nineteen(_SYLK) % 19 == 0
class TestSylkTotalCellCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_nineteen(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_nineteen(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_nineteen(_SYLK) % 19 == 0
class TestAbwWordCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_nineteen(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_nineteen(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_nineteen(_ABW) % 19 == 0
class TestAbwParagraphCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_nineteen(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_nineteen(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_nineteen(_ABW) % 19 == 0

"""Sprint R506 — CSV/TSV/DIF/SYLK/ABW _times_fifteen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_fifteen, csv_column_count_times_fifteen
from src.python.tsv.tsv_parser import tsv_row_count_times_fifteen, tsv_file_size_bytes_times_fifteen
from src.python.dif.dif_parser import dif_row_count_times_fifteen, dif_column_count_times_fifteen
from src.python.sylk.sylk_parser import sylk_row_count_times_fifteen, sylk_total_cell_count_times_fifteen
from src.python.abw.abw_codec import abw_word_count_times_fifteen, abw_paragraph_count_times_fifteen
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_fifteen(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_fifteen(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_fifteen(_CSV) % 15 == 0

class TestCsvColumnCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_fifteen(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_fifteen(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_fifteen(_CSV) % 15 == 0

class TestTsvRowCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_fifteen(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_fifteen(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_fifteen(_TSV) % 15 == 0

class TestTsvFileSizeBytesTimesFifteen:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_fifteen(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_fifteen(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_fifteen(_TSV) % 15 == 0

class TestDifRowCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_fifteen(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_fifteen(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_fifteen(_DIF) % 15 == 0

class TestDifColumnCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_fifteen(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_fifteen(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_fifteen(_DIF) % 15 == 0

class TestSylkRowCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_fifteen(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_fifteen(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_fifteen(_SYLK) % 15 == 0

class TestSylkTotalCellCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_fifteen(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_fifteen(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_fifteen(_SYLK) % 15 == 0

class TestAbwWordCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_fifteen(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_fifteen(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_fifteen(_ABW) % 15 == 0

class TestAbwParagraphCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_fifteen(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_fifteen(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_fifteen(_ABW) % 15 == 0

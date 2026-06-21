"""Sprint R686 — CSV/TSV/DIF/SYLK/ABW _times_sixty composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_sixty, csv_column_count_times_sixty
from src.python.tsv.tsv_parser import tsv_row_count_times_sixty, tsv_file_size_bytes_times_sixty
from src.python.dif.dif_parser import dif_row_count_times_sixty, dif_column_count_times_sixty
from src.python.sylk.sylk_parser import sylk_row_count_times_sixty, sylk_total_cell_count_times_sixty
from src.python.abw.abw_codec import abw_word_count_times_sixty, abw_paragraph_count_times_sixty
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_sixty(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_sixty(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_sixty(_CSV) % 60 == 0
class TestCsvColumnCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_sixty(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_sixty(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_sixty(_CSV) % 60 == 0
class TestTsvRowCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_sixty(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_sixty(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_sixty(_TSV) % 60 == 0
class TestTsvFileSizeBytesTimesSixty:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_sixty(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_sixty(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_sixty(_TSV) % 60 == 0
class TestDifRowCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_sixty(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_sixty(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_sixty(_DIF) % 60 == 0
class TestDifColumnCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_sixty(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_sixty(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_sixty(_DIF) % 60 == 0
class TestSylkRowCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_sixty(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_sixty(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_sixty(_SYLK) % 60 == 0
class TestSylkTotalCellCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_sixty(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_sixty(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_sixty(_SYLK) % 60 == 0
class TestAbwWordCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_sixty(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_sixty(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_sixty(_ABW) % 60 == 0
class TestAbwParagraphCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_sixty(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_sixty(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_sixty(_ABW) % 60 == 0

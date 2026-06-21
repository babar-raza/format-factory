"""Sprint R526 — CSV/TSV/DIF/SYLK/ABW _times_twenty composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_twenty, csv_column_count_times_twenty
from src.python.tsv.tsv_parser import tsv_row_count_times_twenty, tsv_file_size_bytes_times_twenty
from src.python.dif.dif_parser import dif_row_count_times_twenty, dif_column_count_times_twenty
from src.python.sylk.sylk_parser import sylk_row_count_times_twenty, sylk_total_cell_count_times_twenty
from src.python.abw.abw_codec import abw_word_count_times_twenty, abw_paragraph_count_times_twenty
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_twenty(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_twenty(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_twenty(_CSV) % 20 == 0
class TestCsvColumnCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_twenty(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_twenty(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_twenty(_CSV) % 20 == 0
class TestTsvRowCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_twenty(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_twenty(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_twenty(_TSV) % 20 == 0
class TestTsvFileSizeBytesTimesTwenty:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_twenty(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_twenty(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_twenty(_TSV) % 20 == 0
class TestDifRowCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_twenty(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_twenty(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_twenty(_DIF) % 20 == 0
class TestDifColumnCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_twenty(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_twenty(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_twenty(_DIF) % 20 == 0
class TestSylkRowCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_twenty(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_twenty(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_twenty(_SYLK) % 20 == 0
class TestSylkTotalCellCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_twenty(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_twenty(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_twenty(_SYLK) % 20 == 0
class TestAbwWordCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_twenty(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_twenty(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_twenty(_ABW) % 20 == 0
class TestAbwParagraphCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_twenty(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_twenty(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_twenty(_ABW) % 20 == 0

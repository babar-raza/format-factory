"""Sprint R766 — CSV/TSV/DIF/SYLK/ABW _times_eighty composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_eighty, csv_column_count_times_eighty
from src.python.tsv.tsv_parser import tsv_row_count_times_eighty, tsv_file_size_bytes_times_eighty
from src.python.dif.dif_parser import dif_row_count_times_eighty, dif_column_count_times_eighty
from src.python.sylk.sylk_parser import sylk_row_count_times_eighty, sylk_total_cell_count_times_eighty
from src.python.abw.abw_codec import abw_word_count_times_eighty, abw_paragraph_count_times_eighty
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_eighty(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_eighty(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_eighty(_CSV) % 80 == 0
class TestCsvColumnCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_eighty(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_eighty(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_eighty(_CSV) % 80 == 0
class TestTsvRowCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_eighty(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_eighty(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_eighty(_TSV) % 80 == 0
class TestTsvFileSizeBytesTimesEighty:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_eighty(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_eighty(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_eighty(_TSV) % 80 == 0
class TestDifRowCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_eighty(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_eighty(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_eighty(_DIF) % 80 == 0
class TestDifColumnCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_eighty(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_eighty(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_eighty(_DIF) % 80 == 0
class TestSylkRowCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_eighty(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_eighty(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_eighty(_SYLK) % 80 == 0
class TestSylkTotalCellCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_eighty(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_eighty(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_eighty(_SYLK) % 80 == 0
class TestAbwWordCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_eighty(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_eighty(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_eighty(_ABW) % 80 == 0
class TestAbwParagraphCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_eighty(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_eighty(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_eighty(_ABW) % 80 == 0

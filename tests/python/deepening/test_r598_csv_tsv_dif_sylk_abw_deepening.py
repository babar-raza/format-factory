"""Sprint R598 — CSV/TSV/DIF/SYLK/ABW _times_thirty_eight composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_thirty_eight, csv_column_count_times_thirty_eight
from src.python.tsv.tsv_parser import tsv_row_count_times_thirty_eight, tsv_file_size_bytes_times_thirty_eight
from src.python.dif.dif_parser import dif_row_count_times_thirty_eight, dif_column_count_times_thirty_eight
from src.python.sylk.sylk_parser import sylk_row_count_times_thirty_eight, sylk_total_cell_count_times_thirty_eight
from src.python.abw.abw_codec import abw_word_count_times_thirty_eight, abw_paragraph_count_times_thirty_eight
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesThirtyEight:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_thirty_eight(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_thirty_eight(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_thirty_eight(_CSV) % 38 == 0
class TestCsvColumnCountTimesThirtyEight:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_thirty_eight(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_thirty_eight(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_thirty_eight(_CSV) % 38 == 0
class TestTsvRowCountTimesThirtyEight:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_thirty_eight(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_thirty_eight(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_thirty_eight(_TSV) % 38 == 0
class TestTsvFileSizeBytesTimesThirtyEight:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_thirty_eight(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_thirty_eight(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_thirty_eight(_TSV) % 38 == 0
class TestDifRowCountTimesThirtyEight:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_thirty_eight(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_thirty_eight(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_thirty_eight(_DIF) % 38 == 0
class TestDifColumnCountTimesThirtyEight:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_thirty_eight(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_thirty_eight(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_thirty_eight(_DIF) % 38 == 0
class TestSylkRowCountTimesThirtyEight:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_thirty_eight(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_thirty_eight(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_thirty_eight(_SYLK) % 38 == 0
class TestSylkTotalCellCountTimesThirtyEight:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_thirty_eight(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_thirty_eight(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_thirty_eight(_SYLK) % 38 == 0
class TestAbwWordCountTimesThirtyEight:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_thirty_eight(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_thirty_eight(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_thirty_eight(_ABW) % 38 == 0
class TestAbwParagraphCountTimesThirtyEight:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_thirty_eight(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_thirty_eight(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_thirty_eight(_ABW) % 38 == 0

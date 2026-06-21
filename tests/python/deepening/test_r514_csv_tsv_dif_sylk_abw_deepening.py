"""Sprint R514 — CSV/TSV/DIF/SYLK/ABW _times_seventeen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_seventeen, csv_column_count_times_seventeen
from src.python.tsv.tsv_parser import tsv_row_count_times_seventeen, tsv_file_size_bytes_times_seventeen
from src.python.dif.dif_parser import dif_row_count_times_seventeen, dif_column_count_times_seventeen
from src.python.sylk.sylk_parser import sylk_row_count_times_seventeen, sylk_total_cell_count_times_seventeen
from src.python.abw.abw_codec import abw_word_count_times_seventeen, abw_paragraph_count_times_seventeen
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_seventeen(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_seventeen(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_seventeen(_CSV) % 17 == 0
class TestCsvColumnCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_seventeen(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_seventeen(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_seventeen(_CSV) % 17 == 0
class TestTsvRowCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_seventeen(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_seventeen(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_seventeen(_TSV) % 17 == 0
class TestTsvFileSizeBytesTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_seventeen(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_seventeen(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_seventeen(_TSV) % 17 == 0
class TestDifRowCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_seventeen(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_seventeen(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_seventeen(_DIF) % 17 == 0
class TestDifColumnCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_seventeen(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_seventeen(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_seventeen(_DIF) % 17 == 0
class TestSylkRowCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_seventeen(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_seventeen(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_seventeen(_SYLK) % 17 == 0
class TestSylkTotalCellCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_seventeen(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_seventeen(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_seventeen(_SYLK) % 17 == 0
class TestAbwWordCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_seventeen(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_seventeen(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_seventeen(_ABW) % 17 == 0
class TestAbwParagraphCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_seventeen(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_seventeen(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_seventeen(_ABW) % 17 == 0

"""Sprint R510 — CSV/TSV/DIF/SYLK/ABW _times_sixteen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_sixteen, csv_column_count_times_sixteen
from src.python.tsv.tsv_parser import tsv_row_count_times_sixteen, tsv_file_size_bytes_times_sixteen
from src.python.dif.dif_parser import dif_row_count_times_sixteen, dif_column_count_times_sixteen
from src.python.sylk.sylk_parser import sylk_row_count_times_sixteen, sylk_total_cell_count_times_sixteen
from src.python.abw.abw_codec import abw_word_count_times_sixteen, abw_paragraph_count_times_sixteen
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_sixteen(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_sixteen(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_sixteen(_CSV) % 16 == 0
class TestCsvColumnCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_sixteen(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_sixteen(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_sixteen(_CSV) % 16 == 0
class TestTsvRowCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_sixteen(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_sixteen(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_sixteen(_TSV) % 16 == 0
class TestTsvFileSizeBytesTimesSixteen:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_sixteen(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_sixteen(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_sixteen(_TSV) % 16 == 0
class TestDifRowCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_sixteen(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_sixteen(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_sixteen(_DIF) % 16 == 0
class TestDifColumnCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_sixteen(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_sixteen(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_sixteen(_DIF) % 16 == 0
class TestSylkRowCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_sixteen(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_sixteen(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_sixteen(_SYLK) % 16 == 0
class TestSylkTotalCellCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_sixteen(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_sixteen(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_sixteen(_SYLK) % 16 == 0
class TestAbwWordCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_sixteen(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_sixteen(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_sixteen(_ABW) % 16 == 0
class TestAbwParagraphCountTimesSixteen:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_sixteen(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_sixteen(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_sixteen(_ABW) % 16 == 0

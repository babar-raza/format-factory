"""Sprint R518 — CSV/TSV/DIF/SYLK/ABW _times_eighteen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_eighteen, csv_column_count_times_eighteen
from src.python.tsv.tsv_parser import tsv_row_count_times_eighteen, tsv_file_size_bytes_times_eighteen
from src.python.dif.dif_parser import dif_row_count_times_eighteen, dif_column_count_times_eighteen
from src.python.sylk.sylk_parser import sylk_row_count_times_eighteen, sylk_total_cell_count_times_eighteen
from src.python.abw.abw_codec import abw_word_count_times_eighteen, abw_paragraph_count_times_eighteen
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_eighteen(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_eighteen(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_eighteen(_CSV) % 18 == 0
class TestCsvColumnCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_eighteen(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_eighteen(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_eighteen(_CSV) % 18 == 0
class TestTsvRowCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_eighteen(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_eighteen(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_eighteen(_TSV) % 18 == 0
class TestTsvFileSizeBytesTimesEighteen:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_eighteen(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_eighteen(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_eighteen(_TSV) % 18 == 0
class TestDifRowCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_eighteen(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_eighteen(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_eighteen(_DIF) % 18 == 0
class TestDifColumnCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_eighteen(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_eighteen(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_eighteen(_DIF) % 18 == 0
class TestSylkRowCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_eighteen(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_eighteen(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_eighteen(_SYLK) % 18 == 0
class TestSylkTotalCellCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_eighteen(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_eighteen(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_eighteen(_SYLK) % 18 == 0
class TestAbwWordCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_eighteen(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_eighteen(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_eighteen(_ABW) % 18 == 0
class TestAbwParagraphCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_eighteen(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_eighteen(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_eighteen(_ABW) % 18 == 0

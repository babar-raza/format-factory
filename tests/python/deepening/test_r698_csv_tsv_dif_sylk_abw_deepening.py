"""Sprint R698 — CSV/TSV/DIF/SYLK/ABW _times_sixty_three composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_sixty_three, csv_column_count_times_sixty_three
from src.python.tsv.tsv_parser import tsv_row_count_times_sixty_three, tsv_file_size_bytes_times_sixty_three
from src.python.dif.dif_parser import dif_row_count_times_sixty_three, dif_column_count_times_sixty_three
from src.python.sylk.sylk_parser import sylk_row_count_times_sixty_three, sylk_total_cell_count_times_sixty_three
from src.python.abw.abw_codec import abw_word_count_times_sixty_three, abw_paragraph_count_times_sixty_three
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesSixtyThree:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_sixty_three(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_sixty_three(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_sixty_three(_CSV) % 63 == 0
class TestCsvColumnCountTimesSixtyThree:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_sixty_three(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_sixty_three(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_sixty_three(_CSV) % 63 == 0
class TestTsvRowCountTimesSixtyThree:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_sixty_three(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_sixty_three(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_sixty_three(_TSV) % 63 == 0
class TestTsvFileSizeBytesTimesSixtyThree:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_sixty_three(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_sixty_three(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_sixty_three(_TSV) % 63 == 0
class TestDifRowCountTimesSixtyThree:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_sixty_three(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_sixty_three(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_sixty_three(_DIF) % 63 == 0
class TestDifColumnCountTimesSixtyThree:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_sixty_three(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_sixty_three(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_sixty_three(_DIF) % 63 == 0
class TestSylkRowCountTimesSixtyThree:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_sixty_three(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_sixty_three(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_sixty_three(_SYLK) % 63 == 0
class TestSylkTotalCellCountTimesSixtyThree:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_sixty_three(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_sixty_three(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_sixty_three(_SYLK) % 63 == 0
class TestAbwWordCountTimesSixtyThree:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_sixty_three(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_sixty_three(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_sixty_three(_ABW) % 63 == 0
class TestAbwParagraphCountTimesSixtyThree:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_sixty_three(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_sixty_three(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_sixty_three(_ABW) % 63 == 0

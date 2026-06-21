"""Sprint R694 — CSV/TSV/DIF/SYLK/ABW _times_sixty_two composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_sixty_two, csv_column_count_times_sixty_two
from src.python.tsv.tsv_parser import tsv_row_count_times_sixty_two, tsv_file_size_bytes_times_sixty_two
from src.python.dif.dif_parser import dif_row_count_times_sixty_two, dif_column_count_times_sixty_two
from src.python.sylk.sylk_parser import sylk_row_count_times_sixty_two, sylk_total_cell_count_times_sixty_two
from src.python.abw.abw_codec import abw_word_count_times_sixty_two, abw_paragraph_count_times_sixty_two
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_sixty_two(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_sixty_two(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_sixty_two(_CSV) % 62 == 0
class TestCsvColumnCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_sixty_two(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_sixty_two(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_sixty_two(_CSV) % 62 == 0
class TestTsvRowCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_sixty_two(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_sixty_two(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_sixty_two(_TSV) % 62 == 0
class TestTsvFileSizeBytesTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_sixty_two(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_sixty_two(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_sixty_two(_TSV) % 62 == 0
class TestDifRowCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_sixty_two(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_sixty_two(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_sixty_two(_DIF) % 62 == 0
class TestDifColumnCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_sixty_two(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_sixty_two(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_sixty_two(_DIF) % 62 == 0
class TestSylkRowCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_sixty_two(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_sixty_two(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_sixty_two(_SYLK) % 62 == 0
class TestSylkTotalCellCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_sixty_two(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_sixty_two(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_sixty_two(_SYLK) % 62 == 0
class TestAbwWordCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_sixty_two(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_sixty_two(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_sixty_two(_ABW) % 62 == 0
class TestAbwParagraphCountTimesSixtyTwo:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_sixty_two(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_sixty_two(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_sixty_two(_ABW) % 62 == 0

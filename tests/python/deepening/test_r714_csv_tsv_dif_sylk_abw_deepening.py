"""Sprint R714 — CSV/TSV/DIF/SYLK/ABW _times_sixty_seven composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_sixty_seven, csv_column_count_times_sixty_seven
from src.python.tsv.tsv_parser import tsv_row_count_times_sixty_seven, tsv_file_size_bytes_times_sixty_seven
from src.python.dif.dif_parser import dif_row_count_times_sixty_seven, dif_column_count_times_sixty_seven
from src.python.sylk.sylk_parser import sylk_row_count_times_sixty_seven, sylk_total_cell_count_times_sixty_seven
from src.python.abw.abw_codec import abw_word_count_times_sixty_seven, abw_paragraph_count_times_sixty_seven
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesSixtySeven:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_sixty_seven(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_sixty_seven(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_sixty_seven(_CSV) % 67 == 0
class TestCsvColumnCountTimesSixtySeven:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_sixty_seven(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_sixty_seven(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_sixty_seven(_CSV) % 67 == 0
class TestTsvRowCountTimesSixtySeven:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_sixty_seven(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_sixty_seven(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_sixty_seven(_TSV) % 67 == 0
class TestTsvFileSizeBytesTimesSixtySeven:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_sixty_seven(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_sixty_seven(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_sixty_seven(_TSV) % 67 == 0
class TestDifRowCountTimesSixtySeven:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_sixty_seven(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_sixty_seven(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_sixty_seven(_DIF) % 67 == 0
class TestDifColumnCountTimesSixtySeven:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_sixty_seven(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_sixty_seven(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_sixty_seven(_DIF) % 67 == 0
class TestSylkRowCountTimesSixtySeven:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_sixty_seven(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_sixty_seven(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_sixty_seven(_SYLK) % 67 == 0
class TestSylkTotalCellCountTimesSixtySeven:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_sixty_seven(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_sixty_seven(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_sixty_seven(_SYLK) % 67 == 0
class TestAbwWordCountTimesSixtySeven:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_sixty_seven(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_sixty_seven(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_sixty_seven(_ABW) % 67 == 0
class TestAbwParagraphCountTimesSixtySeven:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_sixty_seven(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_sixty_seven(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_sixty_seven(_ABW) % 67 == 0

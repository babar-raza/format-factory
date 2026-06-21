"""Sprint R794 — CSV/TSV/DIF/SYLK/ABW _times_eighty_seven composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_eighty_seven, csv_column_count_times_eighty_seven
from src.python.tsv.tsv_parser import tsv_row_count_times_eighty_seven, tsv_file_size_bytes_times_eighty_seven
from src.python.dif.dif_parser import dif_row_count_times_eighty_seven, dif_column_count_times_eighty_seven
from src.python.sylk.sylk_parser import sylk_row_count_times_eighty_seven, sylk_total_cell_count_times_eighty_seven
from src.python.abw.abw_codec import abw_word_count_times_eighty_seven, abw_paragraph_count_times_eighty_seven
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesEightySeven:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_eighty_seven(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_eighty_seven(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_eighty_seven(_CSV) % 87 == 0
class TestCsvColumnCountTimesEightySeven:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_eighty_seven(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_eighty_seven(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_eighty_seven(_CSV) % 87 == 0
class TestTsvRowCountTimesEightySeven:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_eighty_seven(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_eighty_seven(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_eighty_seven(_TSV) % 87 == 0
class TestTsvFileSizeBytesTimesEightySeven:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_eighty_seven(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_eighty_seven(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_eighty_seven(_TSV) % 87 == 0
class TestDifRowCountTimesEightySeven:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_eighty_seven(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_eighty_seven(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_eighty_seven(_DIF) % 87 == 0
class TestDifColumnCountTimesEightySeven:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_eighty_seven(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_eighty_seven(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_eighty_seven(_DIF) % 87 == 0
class TestSylkRowCountTimesEightySeven:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_eighty_seven(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_eighty_seven(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_eighty_seven(_SYLK) % 87 == 0
class TestSylkTotalCellCountTimesEightySeven:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_eighty_seven(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_eighty_seven(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_eighty_seven(_SYLK) % 87 == 0
class TestAbwWordCountTimesEightySeven:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_eighty_seven(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_eighty_seven(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_eighty_seven(_ABW) % 87 == 0
class TestAbwParagraphCountTimesEightySeven:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_eighty_seven(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_eighty_seven(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_eighty_seven(_ABW) % 87 == 0

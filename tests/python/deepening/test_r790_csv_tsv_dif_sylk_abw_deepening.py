"""Sprint R790 — CSV/TSV/DIF/SYLK/ABW _times_eighty_six composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import csv_row_count_times_eighty_six, csv_column_count_times_eighty_six
from src.python.tsv.tsv_parser import tsv_row_count_times_eighty_six, tsv_file_size_bytes_times_eighty_six
from src.python.dif.dif_parser import dif_row_count_times_eighty_six, dif_column_count_times_eighty_six
from src.python.sylk.sylk_parser import sylk_row_count_times_eighty_six, sylk_total_cell_count_times_eighty_six
from src.python.abw.abw_codec import abw_word_count_times_eighty_six, abw_paragraph_count_times_eighty_six
SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")

class TestCsvRowCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_eighty_six(_CSV), int)
    def test_non_negative(self):
        assert csv_row_count_times_eighty_six(_CSV) >= 0
    def test_divisible(self):
        assert csv_row_count_times_eighty_six(_CSV) % 86 == 0
class TestCsvColumnCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_eighty_six(_CSV), int)
    def test_non_negative(self):
        assert csv_column_count_times_eighty_six(_CSV) >= 0
    def test_divisible(self):
        assert csv_column_count_times_eighty_six(_CSV) % 86 == 0
class TestTsvRowCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_eighty_six(_TSV), int)
    def test_non_negative(self):
        assert tsv_row_count_times_eighty_six(_TSV) >= 0
    def test_divisible(self):
        assert tsv_row_count_times_eighty_six(_TSV) % 86 == 0
class TestTsvFileSizeBytesTimesEightySix:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_eighty_six(_TSV), int)
    def test_non_negative(self):
        assert tsv_file_size_bytes_times_eighty_six(_TSV) >= 0
    def test_divisible(self):
        assert tsv_file_size_bytes_times_eighty_six(_TSV) % 86 == 0
class TestDifRowCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_eighty_six(_DIF), int)
    def test_non_negative(self):
        assert dif_row_count_times_eighty_six(_DIF) >= 0
    def test_divisible(self):
        assert dif_row_count_times_eighty_six(_DIF) % 86 == 0
class TestDifColumnCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_eighty_six(_DIF), int)
    def test_non_negative(self):
        assert dif_column_count_times_eighty_six(_DIF) >= 0
    def test_divisible(self):
        assert dif_column_count_times_eighty_six(_DIF) % 86 == 0
class TestSylkRowCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_eighty_six(_SYLK), int)
    def test_non_negative(self):
        assert sylk_row_count_times_eighty_six(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_row_count_times_eighty_six(_SYLK) % 86 == 0
class TestSylkTotalCellCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_eighty_six(_SYLK), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_eighty_six(_SYLK) >= 0
    def test_divisible(self):
        assert sylk_total_cell_count_times_eighty_six(_SYLK) % 86 == 0
class TestAbwWordCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_eighty_six(_ABW), int)
    def test_non_negative(self):
        assert abw_word_count_times_eighty_six(_ABW) >= 0
    def test_divisible(self):
        assert abw_word_count_times_eighty_six(_ABW) % 86 == 0
class TestAbwParagraphCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_eighty_six(_ABW), int)
    def test_non_negative(self):
        assert abw_paragraph_count_times_eighty_six(_ABW) >= 0
    def test_divisible(self):
        assert abw_paragraph_count_times_eighty_six(_ABW) % 86 == 0

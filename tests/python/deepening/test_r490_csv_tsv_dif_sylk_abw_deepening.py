"""Sprint R490 — CSV/TSV/DIF/SYLK/ABW _times_eleven composite analytics tests."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_row_count_times_eleven, csv_column_count_times_eleven
from src.python.tsv.tsv_parser import tsv_row_count_times_eleven, tsv_file_size_bytes_times_eleven
from src.python.dif.dif_parser import dif_row_count_times_eleven, dif_column_count_times_eleven
from src.python.sylk.sylk_parser import sylk_row_count_times_eleven, sylk_total_cell_count_times_eleven
from src.python.abw.abw_codec import abw_word_count_times_eleven, abw_paragraph_count_times_eleven

SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")


class TestCsvRowCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_eleven(_CSV), int)

    def test_non_negative(self):
        assert csv_row_count_times_eleven(_CSV) >= 0

    def test_divisible(self):
        assert csv_row_count_times_eleven(_CSV) % 11 == 0


class TestCsvColumnCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_eleven(_CSV), int)

    def test_non_negative(self):
        assert csv_column_count_times_eleven(_CSV) >= 0

    def test_divisible(self):
        assert csv_column_count_times_eleven(_CSV) % 11 == 0


class TestTsvRowCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_eleven(_TSV), int)

    def test_non_negative(self):
        assert tsv_row_count_times_eleven(_TSV) >= 0

    def test_divisible(self):
        assert tsv_row_count_times_eleven(_TSV) % 11 == 0


class TestTsvFileSizeBytesTimesEleven:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_eleven(_TSV), int)

    def test_non_negative(self):
        assert tsv_file_size_bytes_times_eleven(_TSV) >= 0

    def test_divisible(self):
        assert tsv_file_size_bytes_times_eleven(_TSV) % 11 == 0


class TestDifRowCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_eleven(_DIF), int)

    def test_non_negative(self):
        assert dif_row_count_times_eleven(_DIF) >= 0

    def test_divisible(self):
        assert dif_row_count_times_eleven(_DIF) % 11 == 0


class TestDifColumnCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_eleven(_DIF), int)

    def test_non_negative(self):
        assert dif_column_count_times_eleven(_DIF) >= 0

    def test_divisible(self):
        assert dif_column_count_times_eleven(_DIF) % 11 == 0


class TestSylkRowCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_eleven(_SYLK), int)

    def test_non_negative(self):
        assert sylk_row_count_times_eleven(_SYLK) >= 0

    def test_divisible(self):
        assert sylk_row_count_times_eleven(_SYLK) % 11 == 0


class TestSylkTotalCellCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_eleven(_SYLK), int)

    def test_non_negative(self):
        assert sylk_total_cell_count_times_eleven(_SYLK) >= 0

    def test_divisible(self):
        assert sylk_total_cell_count_times_eleven(_SYLK) % 11 == 0


class TestAbwWordCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_eleven(_ABW), int)

    def test_non_negative(self):
        assert abw_word_count_times_eleven(_ABW) >= 0

    def test_divisible(self):
        assert abw_word_count_times_eleven(_ABW) % 11 == 0


class TestAbwParagraphCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_eleven(_ABW), int)

    def test_non_negative(self):
        assert abw_paragraph_count_times_eleven(_ABW) >= 0

    def test_divisible(self):
        assert abw_paragraph_count_times_eleven(_ABW) % 11 == 0

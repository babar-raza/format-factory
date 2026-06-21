"""Sprint R494 — CSV/TSV/DIF/SYLK/ABW _times_twelve composite analytics tests."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import csv_row_count_times_twelve, csv_column_count_times_twelve
from src.python.tsv.tsv_parser import tsv_row_count_times_twelve, tsv_file_size_bytes_times_twelve
from src.python.dif.dif_parser import dif_row_count_times_twelve, dif_column_count_times_twelve
from src.python.sylk.sylk_parser import sylk_row_count_times_twelve, sylk_total_cell_count_times_twelve
from src.python.abw.abw_codec import abw_word_count_times_twelve, abw_paragraph_count_times_twelve

SAMPLES = _REPO / "samples" / "by-format"
_CSV = str(SAMPLES / "csv" / "single-cell.csv")
_TSV = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
_DIF = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
_SYLK = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
_ABW = str(SAMPLES / "abw" / "minimal-document.abw")


class TestCsvRowCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(csv_row_count_times_twelve(_CSV), int)

    def test_non_negative(self):
        assert csv_row_count_times_twelve(_CSV) >= 0

    def test_divisible(self):
        assert csv_row_count_times_twelve(_CSV) % 12 == 0


class TestCsvColumnCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(csv_column_count_times_twelve(_CSV), int)

    def test_non_negative(self):
        assert csv_column_count_times_twelve(_CSV) >= 0

    def test_divisible(self):
        assert csv_column_count_times_twelve(_CSV) % 12 == 0


class TestTsvRowCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(tsv_row_count_times_twelve(_TSV), int)

    def test_non_negative(self):
        assert tsv_row_count_times_twelve(_TSV) >= 0

    def test_divisible(self):
        assert tsv_row_count_times_twelve(_TSV) % 12 == 0


class TestTsvFileSizeBytesTimesTwelve:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_bytes_times_twelve(_TSV), int)

    def test_non_negative(self):
        assert tsv_file_size_bytes_times_twelve(_TSV) >= 0

    def test_divisible(self):
        assert tsv_file_size_bytes_times_twelve(_TSV) % 12 == 0


class TestDifRowCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(dif_row_count_times_twelve(_DIF), int)

    def test_non_negative(self):
        assert dif_row_count_times_twelve(_DIF) >= 0

    def test_divisible(self):
        assert dif_row_count_times_twelve(_DIF) % 12 == 0


class TestDifColumnCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(dif_column_count_times_twelve(_DIF), int)

    def test_non_negative(self):
        assert dif_column_count_times_twelve(_DIF) >= 0

    def test_divisible(self):
        assert dif_column_count_times_twelve(_DIF) % 12 == 0


class TestSylkRowCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_twelve(_SYLK), int)

    def test_non_negative(self):
        assert sylk_row_count_times_twelve(_SYLK) >= 0

    def test_divisible(self):
        assert sylk_row_count_times_twelve(_SYLK) % 12 == 0


class TestSylkTotalCellCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_twelve(_SYLK), int)

    def test_non_negative(self):
        assert sylk_total_cell_count_times_twelve(_SYLK) >= 0

    def test_divisible(self):
        assert sylk_total_cell_count_times_twelve(_SYLK) % 12 == 0


class TestAbwWordCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(abw_word_count_times_twelve(_ABW), int)

    def test_non_negative(self):
        assert abw_word_count_times_twelve(_ABW) >= 0

    def test_divisible(self):
        assert abw_word_count_times_twelve(_ABW) % 12 == 0


class TestAbwParagraphCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(abw_paragraph_count_times_twelve(_ABW), int)

    def test_non_negative(self):
        assert abw_paragraph_count_times_twelve(_ABW) >= 0

    def test_divisible(self):
        assert abw_paragraph_count_times_twelve(_ABW) % 12 == 0

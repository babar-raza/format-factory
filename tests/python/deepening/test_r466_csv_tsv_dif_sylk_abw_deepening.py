"""Sprint R466 — CSV/TSV/DIF/SYLK/ABW round 13 deepening (_times_five)."""
import os, sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.csv.csv_parser import csv_row_count_times_five, csv_column_count_times_five
from src.python.tsv.tsv_parser import tsv_row_count_times_five, tsv_file_size_times_five
from src.python.dif.dif_parser import dif_row_count_times_five, dif_column_count_times_five
from src.python.sylk.sylk_parser import sylk_row_count_times_five, sylk_total_cell_count_times_five
from src.python.abw.abw_codec import abw_word_count_times_five, abw_paragraph_count_times_five


# --- CSV ---
class TestCsvRowCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert isinstance(csv_row_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_row_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_row_count_times_five(p) % 5 == 0


class TestCsvColumnCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert isinstance(csv_column_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_column_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_column_count_times_five(p) % 5 == 0


# --- TSV ---
class TestTsvRowCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert isinstance(tsv_row_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_row_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_row_count_times_five(p) % 5 == 0


class TestTsvFileSizeTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert isinstance(tsv_file_size_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_file_size_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_file_size_times_five(p) % 5 == 0


# --- DIF ---
class TestDifRowCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert isinstance(dif_row_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_row_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_row_count_times_five(p) % 5 == 0


class TestDifColumnCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert isinstance(dif_column_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_column_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_column_count_times_five(p) % 5 == 0


# --- SYLK ---
class TestSylkRowCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert isinstance(sylk_row_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_row_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_row_count_times_five(p) % 5 == 0


class TestSylkTotalCellCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert isinstance(sylk_total_cell_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_total_cell_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_total_cell_count_times_five(p) % 5 == 0


# --- ABW ---
class TestAbwWordCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert isinstance(abw_word_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_word_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_word_count_times_five(p) % 5 == 0


class TestAbwParagraphCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert isinstance(abw_paragraph_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_paragraph_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_paragraph_count_times_five(p) % 5 == 0

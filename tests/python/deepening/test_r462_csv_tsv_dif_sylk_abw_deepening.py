"""Sprint R462 — CSV/TSV/DIF/SYLK/ABW round 12 deepening (_times_four continued)."""
import os, sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.csv import csv_file_size_times_four, csv_total_field_count_times_four
from src.python.tsv import tsv_column_count_times_four, tsv_total_field_count_times_four
from src.python.dif import dif_file_size_times_four, dif_total_cell_count_times_four
from src.python.sylk import sylk_file_size_times_four, sylk_column_count_times_four
from src.python.abw import abw_file_size_times_four, abw_char_count_times_four


# --- CSV ---
class TestCsvFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert isinstance(csv_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_file_size_times_four(p) > 0


class TestCsvTotalFieldCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert isinstance(csv_total_field_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_total_field_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "csv" / "single-cell.csv")
        assert csv_total_field_count_times_four(p) % 4 == 0


# --- TSV ---
class TestTsvColumnCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert isinstance(tsv_column_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_column_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_column_count_times_four(p) % 4 == 0


class TestTsvTotalFieldCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert isinstance(tsv_total_field_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_total_field_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "tsv" / "minimal-2x2.tsv")
        assert tsv_total_field_count_times_four(p) % 4 == 0


# --- DIF ---
class TestDifFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert isinstance(dif_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_file_size_times_four(p) > 0


class TestDifTotalCellCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert isinstance(dif_total_cell_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_total_cell_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "dif" / "valid" / "minimal-2x2.dif")
        assert dif_total_cell_count_times_four(p) % 4 == 0


# --- SYLK ---
class TestSylkFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert isinstance(sylk_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_file_size_times_four(p) > 0


class TestSylkColumnCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert isinstance(sylk_column_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_column_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "sylk" / "valid" / "minimal-2x2.slk")
        assert sylk_column_count_times_four(p) % 4 == 0


# --- ABW ---
class TestAbwFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert isinstance(abw_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_file_size_times_four(p) > 0


class TestAbwCharCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert isinstance(abw_char_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_char_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "abw" / "minimal-document.abw")
        assert abw_char_count_times_four(p) % 4 == 0

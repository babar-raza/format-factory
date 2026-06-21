"""Sprint R446 — CSV/TSV/DIF/SYLK/ABW round 8 deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv import csv_file_size_times_two, csv_string_cell_count_squared, csv_file_size_bytes, csv_string_cell_count
from src.python.tsv import tsv_file_size_times_two, tsv_unique_value_count_squared, tsv_file_size_bytes, tsv_unique_value_count
from src.python.dif import dif_file_size_times_two, dif_unique_string_count_squared, dif_file_size_bytes, dif_unique_string_count
from src.python.sylk import sylk_file_size_times_two, sylk_unique_value_count_squared, sylk_file_size_bytes, sylk_unique_value_count
from src.python.abw import abw_file_size_times_two, abw_total_word_count_squared, abw_file_size_bytes, abw_total_word_count

SAMPLES = _REPO / "samples" / "by-format"
CSV_SAMPLE = SAMPLES / "csv" / "single-cell.csv"
TSV_SAMPLE = SAMPLES / "tsv" / "minimal-2x2.tsv"
DIF_SAMPLE = SAMPLES / "dif" / "valid" / "minimal-2x2.dif"
SYLK_SAMPLE = SAMPLES / "sylk" / "valid" / "minimal-2x2.slk"
ABW_SAMPLE = SAMPLES / "abw" / "minimal-document.abw"


# --- CSV: csv_file_size_times_two ---
class TestCsvFileSizeTimesTwo:
    def test_returns_int(self):
        assert isinstance(csv_file_size_times_two(CSV_SAMPLE), int)

    def test_is_double_file_size(self):
        assert csv_file_size_times_two(CSV_SAMPLE) == csv_file_size_bytes(CSV_SAMPLE) * 2

    def test_positive(self):
        assert csv_file_size_times_two(CSV_SAMPLE) > 0


# --- CSV: csv_string_cell_count_squared ---
class TestCsvStringCellCountSquared:
    def test_returns_int(self):
        assert isinstance(csv_string_cell_count_squared(CSV_SAMPLE), int)

    def test_is_square(self):
        sc = csv_string_cell_count(CSV_SAMPLE)
        assert csv_string_cell_count_squared(CSV_SAMPLE) == sc * sc

    def test_non_negative(self):
        assert csv_string_cell_count_squared(CSV_SAMPLE) >= 0


# --- TSV: tsv_file_size_times_two ---
class TestTsvFileSizeTimesTwo:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_times_two(TSV_SAMPLE), int)

    def test_is_double_file_size(self):
        assert tsv_file_size_times_two(TSV_SAMPLE) == tsv_file_size_bytes(TSV_SAMPLE) * 2

    def test_positive(self):
        assert tsv_file_size_times_two(TSV_SAMPLE) > 0


# --- TSV: tsv_unique_value_count_squared ---
class TestTsvUniqueValueCountSquared:
    def test_returns_int(self):
        assert isinstance(tsv_unique_value_count_squared(TSV_SAMPLE), int)

    def test_is_square(self):
        uv = tsv_unique_value_count(TSV_SAMPLE)
        assert tsv_unique_value_count_squared(TSV_SAMPLE) == uv * uv

    def test_non_negative(self):
        assert tsv_unique_value_count_squared(TSV_SAMPLE) >= 0


# --- DIF: dif_file_size_times_two ---
class TestDifFileSizeTimesTwo:
    def test_returns_int(self):
        assert isinstance(dif_file_size_times_two(DIF_SAMPLE), int)

    def test_is_double_file_size(self):
        assert dif_file_size_times_two(DIF_SAMPLE) == dif_file_size_bytes(DIF_SAMPLE) * 2

    def test_positive(self):
        assert dif_file_size_times_two(DIF_SAMPLE) > 0


# --- DIF: dif_unique_string_count_squared ---
class TestDifUniqueStringCountSquared:
    def test_returns_int(self):
        assert isinstance(dif_unique_string_count_squared(DIF_SAMPLE), int)

    def test_is_square(self):
        us = dif_unique_string_count(DIF_SAMPLE)
        assert dif_unique_string_count_squared(DIF_SAMPLE) == us * us

    def test_non_negative(self):
        assert dif_unique_string_count_squared(DIF_SAMPLE) >= 0


# --- SYLK: sylk_file_size_times_two ---
class TestSylkFileSizeTimesTwo:
    def test_returns_int(self):
        assert isinstance(sylk_file_size_times_two(SYLK_SAMPLE), int)

    def test_is_double_file_size(self):
        assert sylk_file_size_times_two(SYLK_SAMPLE) == sylk_file_size_bytes(SYLK_SAMPLE) * 2

    def test_positive(self):
        assert sylk_file_size_times_two(SYLK_SAMPLE) > 0


# --- SYLK: sylk_unique_value_count_squared ---
class TestSylkUniqueValueCountSquared:
    def test_returns_int(self):
        assert isinstance(sylk_unique_value_count_squared(SYLK_SAMPLE), int)

    def test_is_square(self):
        uv = sylk_unique_value_count(SYLK_SAMPLE)
        assert sylk_unique_value_count_squared(SYLK_SAMPLE) == uv * uv

    def test_non_negative(self):
        assert sylk_unique_value_count_squared(SYLK_SAMPLE) >= 0


# --- ABW: abw_file_size_times_two ---
class TestAbwFileSizeTimesTwo:
    def test_returns_int(self):
        assert isinstance(abw_file_size_times_two(ABW_SAMPLE), int)

    def test_is_double_file_size(self):
        assert abw_file_size_times_two(ABW_SAMPLE) == abw_file_size_bytes(ABW_SAMPLE) * 2

    def test_positive(self):
        assert abw_file_size_times_two(ABW_SAMPLE) > 0


# --- ABW: abw_total_word_count_squared ---
class TestAbwTotalWordCountSquared:
    def test_returns_int(self):
        assert isinstance(abw_total_word_count_squared(ABW_SAMPLE), int)

    def test_is_square(self):
        wc = abw_total_word_count(ABW_SAMPLE)
        assert abw_total_word_count_squared(ABW_SAMPLE) == wc * wc

    def test_non_negative(self):
        assert abw_total_word_count_squared(ABW_SAMPLE) >= 0

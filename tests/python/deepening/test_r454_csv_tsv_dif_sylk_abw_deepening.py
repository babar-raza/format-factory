"""Sprint R454 — CSV/TSV/DIF/SYLK/ABW round 10 deepening tests."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv import csv_file_size_times_three, csv_total_field_count_times_three, csv_file_size_bytes, csv_total_field_count
from src.python.tsv import tsv_file_size_times_three, tsv_column_count_times_three, tsv_file_size_bytes, tsv_column_count
from src.python.dif import dif_file_size_times_three, dif_total_cell_count_times_three, dif_file_size_bytes, dif_total_cell_count
from src.python.sylk import sylk_file_size_times_three, sylk_total_cell_count_times_three, sylk_file_size_bytes, sylk_total_cell_count
from src.python.abw import abw_file_size_times_three, abw_digit_count_times_three, abw_file_size_bytes, abw_digit_count

SAMPLES = _REPO / "samples" / "by-format"
CSV_SAMPLE = SAMPLES / "csv" / "single-cell.csv"
TSV_SAMPLE = SAMPLES / "tsv" / "minimal-2x2.tsv"
DIF_SAMPLE = SAMPLES / "dif" / "valid" / "minimal-2x2.dif"
SYLK_SAMPLE = SAMPLES / "sylk" / "valid" / "minimal-2x2.slk"
ABW_SAMPLE = SAMPLES / "abw" / "minimal-document.abw"


class TestCsvFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(csv_file_size_times_three(CSV_SAMPLE), int)
    def test_is_triple(self):
        assert csv_file_size_times_three(CSV_SAMPLE) == csv_file_size_bytes(CSV_SAMPLE) * 3
    def test_non_negative(self):
        assert csv_file_size_times_three(CSV_SAMPLE) >= 0


class TestCsvTotalFieldCountTimesThree:
    def test_returns_int(self):
        assert isinstance(csv_total_field_count_times_three(CSV_SAMPLE), int)
    def test_is_triple(self):
        assert csv_total_field_count_times_three(CSV_SAMPLE) == csv_total_field_count(CSV_SAMPLE) * 3
    def test_non_negative(self):
        assert csv_total_field_count_times_three(CSV_SAMPLE) >= 0


class TestTsvFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(tsv_file_size_times_three(TSV_SAMPLE), int)
    def test_is_triple(self):
        assert tsv_file_size_times_three(TSV_SAMPLE) == tsv_file_size_bytes(TSV_SAMPLE) * 3
    def test_non_negative(self):
        assert tsv_file_size_times_three(TSV_SAMPLE) >= 0


class TestTsvColumnCountTimesThree:
    def test_returns_int(self):
        assert isinstance(tsv_column_count_times_three(TSV_SAMPLE), int)
    def test_is_triple(self):
        assert tsv_column_count_times_three(TSV_SAMPLE) == tsv_column_count(TSV_SAMPLE) * 3
    def test_non_negative(self):
        assert tsv_column_count_times_three(TSV_SAMPLE) >= 0


class TestDifFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(dif_file_size_times_three(DIF_SAMPLE), int)
    def test_is_triple(self):
        assert dif_file_size_times_three(DIF_SAMPLE) == dif_file_size_bytes(DIF_SAMPLE) * 3
    def test_non_negative(self):
        assert dif_file_size_times_three(DIF_SAMPLE) >= 0


class TestDifTotalCellCountTimesThree:
    def test_returns_int(self):
        assert isinstance(dif_total_cell_count_times_three(DIF_SAMPLE), int)
    def test_is_triple(self):
        assert dif_total_cell_count_times_three(DIF_SAMPLE) == dif_total_cell_count(DIF_SAMPLE) * 3
    def test_non_negative(self):
        assert dif_total_cell_count_times_three(DIF_SAMPLE) >= 0


class TestSylkFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(sylk_file_size_times_three(SYLK_SAMPLE), int)
    def test_is_triple(self):
        assert sylk_file_size_times_three(SYLK_SAMPLE) == sylk_file_size_bytes(SYLK_SAMPLE) * 3
    def test_non_negative(self):
        assert sylk_file_size_times_three(SYLK_SAMPLE) >= 0


class TestSylkTotalCellCountTimesThree:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_three(SYLK_SAMPLE), int)
    def test_is_triple(self):
        assert sylk_total_cell_count_times_three(SYLK_SAMPLE) == sylk_total_cell_count(SYLK_SAMPLE) * 3
    def test_non_negative(self):
        assert sylk_total_cell_count_times_three(SYLK_SAMPLE) >= 0


class TestAbwFileSizeTimesThree:
    def test_returns_int(self):
        assert isinstance(abw_file_size_times_three(ABW_SAMPLE), int)
    def test_is_triple(self):
        assert abw_file_size_times_three(ABW_SAMPLE) == abw_file_size_bytes(ABW_SAMPLE) * 3
    def test_non_negative(self):
        assert abw_file_size_times_three(ABW_SAMPLE) >= 0


class TestAbwDigitCountTimesThree:
    def test_returns_int(self):
        assert isinstance(abw_digit_count_times_three(ABW_SAMPLE), int)
    def test_is_triple(self):
        assert abw_digit_count_times_three(ABW_SAMPLE) == abw_digit_count(ABW_SAMPLE) * 3
    def test_non_negative(self):
        assert abw_digit_count_times_three(ABW_SAMPLE) >= 0

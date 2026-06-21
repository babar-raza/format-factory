"""
Sprint ff-idempotent-spec-to-feature-swarm-20260617 — SYLK + TOML analytics deepening.
Tests for eighty_nine variants.
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk import sylk_row_count_times_eighty_nine, sylk_total_cell_count_times_eighty_nine
from src.python.toml import toml_file_size_bytes_times_eighty_nine, toml_string_value_count_times_eighty_nine

_SYLK_MIN = str(_REPO / "samples/by-format/sylk/valid/minimal-2x2.slk")
_SYLK_NUM = str(_REPO / "samples/by-format/sylk/valid/numeric-row.slk")
_TOML = str(_REPO / "samples/by-format/toml/minimal.toml")


class TestSylkRowCountTimesEightyNine:
    def test_returns_int(self):
        assert isinstance(sylk_row_count_times_eighty_nine(_SYLK_MIN), int)
    def test_non_negative(self):
        assert sylk_row_count_times_eighty_nine(_SYLK_MIN) >= 0
    def test_divisible_by_89(self):
        assert sylk_row_count_times_eighty_nine(_SYLK_MIN) % 89 == 0


class TestSylkTotalCellCountTimesEightyNine:
    def test_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_eighty_nine(_SYLK_MIN), int)
    def test_non_negative(self):
        assert sylk_total_cell_count_times_eighty_nine(_SYLK_MIN) >= 0
    def test_divisible_by_89(self):
        assert sylk_total_cell_count_times_eighty_nine(_SYLK_MIN) % 89 == 0
    def test_numeric_returns_int(self):
        assert isinstance(sylk_total_cell_count_times_eighty_nine(_SYLK_NUM), int)


class TestTomlFileSizeBytesTimesEightyNine:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_eighty_nine(_TOML), int)
    def test_positive(self):
        assert toml_file_size_bytes_times_eighty_nine(_TOML) > 0
    def test_divisible_by_89(self):
        assert toml_file_size_bytes_times_eighty_nine(_TOML) % 89 == 0


class TestTomlStringValueCountTimesEightyNine:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_eighty_nine(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_eighty_nine(_TOML) >= 0
    def test_divisible_by_89(self):
        assert toml_string_value_count_times_eighty_nine(_TOML) % 89 == 0

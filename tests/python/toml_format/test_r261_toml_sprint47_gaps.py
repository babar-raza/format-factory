"""Tests for TOML Sprint 47 gap closure.

Closes:
  GAP-TOML-FOSS-TOML_UNIQUE_-001  (Toml Unique Value Count)
  GAP-TOML-FOSS-TOML_FILE_SI-001  (Toml File Size Bytes)
  GAP-TOML-FOSS-TOML_MAX_KEY-001  (Toml Max Key Length)
  GAP-TOML-FOSS-TOML_AVG_VAL-001  (Toml Avg Value Length)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.toml import (
    toml_unique_value_count,
    toml_file_size_bytes,
    toml_max_key_length,
    toml_avg_value_length,
)

_DIR = _REPO / "samples" / "by-format" / "toml"
_MINIMAL = str(_DIR / "minimal.toml")


class TestTomlUniqueValueCount:
    def test_return_type(self):
        assert isinstance(toml_unique_value_count(_MINIMAL), int)

    def test_exact_5_for_minimal(self):
        assert toml_unique_value_count(_MINIMAL) == 5

    def test_positive(self):
        assert toml_unique_value_count(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert toml_unique_value_count(_MINIMAL) == toml_unique_value_count(_MINIMAL)


class TestTomlFileSizeBytes:
    def test_return_type(self):
        assert isinstance(toml_file_size_bytes(_MINIMAL), int)

    def test_exact_177_for_minimal(self):
        assert toml_file_size_bytes(_MINIMAL) == 177

    def test_positive(self):
        assert toml_file_size_bytes(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert toml_file_size_bytes(_MINIMAL) == toml_file_size_bytes(_MINIMAL)


class TestTomlMaxKeyLength:
    def test_return_type(self):
        assert isinstance(toml_max_key_length(_MINIMAL), int)

    def test_exact_8_for_minimal(self):
        assert toml_max_key_length(_MINIMAL) == 8

    def test_positive(self):
        assert toml_max_key_length(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert toml_max_key_length(_MINIMAL) == toml_max_key_length(_MINIMAL)


class TestTomlAvgValueLength:
    def test_return_type(self):
        assert isinstance(toml_avg_value_length(_MINIMAL), (int, float))

    def test_exact_23_4_for_minimal(self):
        assert toml_avg_value_length(_MINIMAL) == 23.4

    def test_positive(self):
        assert toml_avg_value_length(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert toml_avg_value_length(_MINIMAL) == toml_avg_value_length(_MINIMAL)

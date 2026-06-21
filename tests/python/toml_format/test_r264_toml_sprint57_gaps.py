"""Tests for TOML Sprint 57 gap closure.

Closes:
  GAP-TOML-FOSS-TOML_NULL_VA-001   (Toml Null Value Count)
  GAP-TOML-FOSS-TOML_DISTINC-001   (Toml Distinct Key Count)
  GAP-TOML-FOSS-TOML_AVG_NUM-001   (Toml Avg Numeric Value)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.toml import toml_null_value_count, toml_distinct_key_count, toml_avg_numeric_value

_DIR = _REPO / "samples" / "by-format" / "toml"
_MINIMAL = str(_DIR / "minimal.toml")


class TestTomlNullValueCount:
    def test_return_type(self):
        assert isinstance(toml_null_value_count(_MINIMAL), int)

    def test_zero_for_minimal(self):
        assert toml_null_value_count(_MINIMAL) == 0

    def test_zero_for_numeric_only(self, tmp_path):
        f = tmp_path / "nums.toml"
        f.write_text("a = 10\nb = 20\nc = 30\n")
        assert toml_null_value_count(str(f)) == 0

    def test_zero_for_empty(self, tmp_path):
        f = tmp_path / "empty.toml"
        f.write_text("")
        assert toml_null_value_count(str(f)) == 0

    def test_nonnegative(self):
        assert toml_null_value_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert toml_null_value_count(_MINIMAL) == toml_null_value_count(_MINIMAL)


class TestTomlDistinctKeyCount:
    def test_return_type(self):
        assert isinstance(toml_distinct_key_count(_MINIMAL), int)

    def test_exact_9_for_minimal(self):
        assert toml_distinct_key_count(_MINIMAL) == 9

    def test_exact_3_for_numeric(self, tmp_path):
        f = tmp_path / "nums.toml"
        f.write_text("a = 10\nb = 20\nc = 30\n")
        assert toml_distinct_key_count(str(f)) == 3

    def test_zero_for_empty(self, tmp_path):
        f = tmp_path / "empty.toml"
        f.write_text("")
        assert toml_distinct_key_count(str(f)) == 0

    def test_positive_for_minimal(self):
        assert toml_distinct_key_count(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert toml_distinct_key_count(_MINIMAL) == toml_distinct_key_count(_MINIMAL)


class TestTomlAvgNumericValue:
    def test_return_type(self):
        assert isinstance(toml_avg_numeric_value(_MINIMAL), (int, float))

    def test_exact_1_0_for_minimal(self):
        assert toml_avg_numeric_value(_MINIMAL) == 1.0

    def test_exact_20_0_for_numeric(self, tmp_path):
        f = tmp_path / "nums.toml"
        f.write_text("a = 10\nb = 20\nc = 30\n")
        assert toml_avg_numeric_value(str(f)) == 20.0

    def test_zero_for_empty(self, tmp_path):
        f = tmp_path / "empty.toml"
        f.write_text("")
        assert toml_avg_numeric_value(str(f)) == 0.0

    def test_nonnegative(self):
        assert toml_avg_numeric_value(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert toml_avg_numeric_value(_MINIMAL) == toml_avg_numeric_value(_MINIMAL)

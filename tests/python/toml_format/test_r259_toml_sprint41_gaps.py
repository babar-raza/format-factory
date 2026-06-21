"""Tests for TOML Sprint 41 gap closure.

Closes:
  GAP-TOML-FOSS-TOML_HAS_NU-001  (Toml Has Numeric Values)
  GAP-TOML-FOSS-TOML_AVG_LI-001  (Toml Avg List Length)
  GAP-TOML-FOSS-TOML_MAX_NU-001  (Toml Max Numeric Value)
  GAP-TOML-FOSS-TOML_MIN_NU-001  (Toml Min Numeric Value)
  GAP-TOML-FOSS-TOML_BOOL_R-001  (Toml Bool Ratio)
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.toml import (
    toml_avg_list_length,
    toml_bool_ratio,
    toml_has_numeric_values,
    toml_max_numeric_value,
    toml_min_numeric_value,
)


@pytest.fixture
def numeric_file(tmp_path):
    p = tmp_path / "numeric.toml"
    p.write_text("x = 42\ny = 7\n")
    return str(p)


@pytest.fixture
def no_numeric_file(tmp_path):
    p = tmp_path / "no_numeric.toml"
    p.write_text('name = "Alice"\ntitle = "Engineer"\n')
    return str(p)


@pytest.fixture
def list_file(tmp_path):
    p = tmp_path / "lists.toml"
    p.write_text("a = [1, 2, 3]\nb = [4, 5]\n")
    return str(p)


@pytest.fixture
def single_list_file(tmp_path):
    p = tmp_path / "single_list.toml"
    p.write_text("items = [10, 20, 30]\n")
    return str(p)


@pytest.fixture
def bool_file(tmp_path):
    p = tmp_path / "bools.toml"
    p.write_text('enabled = true\nname = "Alice"\ncount = 5\ndebug = false\n')
    return str(p)


@pytest.fixture
def bool_half_file(tmp_path):
    p = tmp_path / "bool_half.toml"
    p.write_text("active = true\ncount = 42\n")
    return str(p)


class TestTomlHasNumericValues:
    def test_return_type(self, numeric_file):
        assert isinstance(toml_has_numeric_values(numeric_file), bool)

    def test_true_for_numeric(self, numeric_file):
        assert toml_has_numeric_values(numeric_file) is True

    def test_false_for_no_numeric(self, no_numeric_file):
        assert toml_has_numeric_values(no_numeric_file) is False

    def test_consistent_across_calls(self, numeric_file):
        assert toml_has_numeric_values(numeric_file) == toml_has_numeric_values(numeric_file)


class TestTomlAvgListLength:
    def test_return_type(self, list_file):
        assert isinstance(toml_avg_list_length(list_file), float)

    def test_exact_2_5_for_list_file(self, list_file):
        assert toml_avg_list_length(list_file) == 2.5

    def test_exact_3_0_for_single_list(self, single_list_file):
        assert toml_avg_list_length(single_list_file) == 3.0

    def test_positive(self, list_file):
        assert toml_avg_list_length(list_file) > 0

    def test_consistent_across_calls(self, list_file):
        assert toml_avg_list_length(list_file) == toml_avg_list_length(list_file)


class TestTomlMaxNumericValue:
    def test_return_type(self, numeric_file):
        assert isinstance(toml_max_numeric_value(numeric_file), float)

    def test_exact_42_0_for_numeric(self, numeric_file):
        assert toml_max_numeric_value(numeric_file) == 42.0

    def test_consistent_across_calls(self, numeric_file):
        assert toml_max_numeric_value(numeric_file) == toml_max_numeric_value(numeric_file)


class TestTomlMinNumericValue:
    def test_return_type(self, numeric_file):
        assert isinstance(toml_min_numeric_value(numeric_file), float)

    def test_exact_7_0_for_numeric(self, numeric_file):
        assert toml_min_numeric_value(numeric_file) == 7.0

    def test_consistent_across_calls(self, numeric_file):
        assert toml_min_numeric_value(numeric_file) == toml_min_numeric_value(numeric_file)


class TestTomlBoolRatio:
    def test_return_type(self, bool_file):
        assert isinstance(toml_bool_ratio(bool_file), float)

    def test_exact_0_5_for_bool_half(self, bool_half_file):
        assert toml_bool_ratio(bool_half_file) == 0.5

    def test_nonnegative(self, bool_file):
        assert toml_bool_ratio(bool_file) >= 0.0

    def test_at_most_1(self, bool_file):
        assert toml_bool_ratio(bool_file) <= 1.0

    def test_consistent_across_calls(self, bool_file):
        assert toml_bool_ratio(bool_file) == toml_bool_ratio(bool_file)

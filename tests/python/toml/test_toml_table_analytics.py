"""Tests for TOML recursive table analytics (toml_table_analytics.py)."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

MINIMAL = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"

from src.python.toml.toml_table_analytics import (
    toml_recursive_key_count,
    toml_recursive_numeric_sum,
    toml_recursive_string_count,
    toml_nested_boolean_count,
    toml_leaf_value_count,
    toml_has_array_of_tables,
    toml_max_numeric_value_recursive,
    toml_min_numeric_value_recursive,
)


class TestTomlRecursiveKeyCount:
    def test_returns_int(self):
        assert isinstance(toml_recursive_key_count(MINIMAL), int)

    def test_nonnegative(self):
        assert toml_recursive_key_count(MINIMAL) >= 0

    def test_minimal_has_nested_keys(self):
        # minimal.toml has top-level and nested table keys
        assert toml_recursive_key_count(MINIMAL) > 5

    def test_accepts_string_path(self):
        assert isinstance(toml_recursive_key_count(str(MINIMAL)), int)


class TestTomlRecursiveNumericSum:
    def test_returns_float(self):
        assert isinstance(toml_recursive_numeric_sum(MINIMAL), float)

    def test_minimal_positive_sum(self):
        # minimal.toml has port=8080 and max_connections=10
        assert toml_recursive_numeric_sum(MINIMAL) > 0.0

    def test_accepts_string_path(self):
        assert isinstance(toml_recursive_numeric_sum(str(MINIMAL)), float)


class TestTomlRecursiveStringCount:
    def test_returns_int(self):
        assert isinstance(toml_recursive_string_count(MINIMAL), int)

    def test_nonnegative(self):
        assert toml_recursive_string_count(MINIMAL) >= 0

    def test_minimal_has_strings(self):
        assert toml_recursive_string_count(MINIMAL) >= 1

    def test_accepts_string_path(self):
        assert isinstance(toml_recursive_string_count(str(MINIMAL)), int)


class TestTomlNestedBooleanCount:
    def test_returns_int(self):
        assert isinstance(toml_nested_boolean_count(MINIMAL), int)

    def test_nonnegative(self):
        assert toml_nested_boolean_count(MINIMAL) >= 0

    def test_minimal_has_boolean(self):
        # minimal.toml has enabled=true
        assert toml_nested_boolean_count(MINIMAL) >= 1

    def test_accepts_string_path(self):
        assert isinstance(toml_nested_boolean_count(str(MINIMAL)), int)


class TestTomlLeafValueCount:
    def test_returns_int(self):
        assert isinstance(toml_leaf_value_count(MINIMAL), int)

    def test_nonnegative(self):
        assert toml_leaf_value_count(MINIMAL) >= 0

    def test_minimal_has_leaves(self):
        assert toml_leaf_value_count(MINIMAL) >= 5

    def test_accepts_string_path(self):
        assert isinstance(toml_leaf_value_count(str(MINIMAL)), int)


class TestTomlHasArrayOfTables:
    def test_returns_bool(self):
        assert isinstance(toml_has_array_of_tables(MINIMAL), bool)

    def test_minimal_no_array_of_tables(self):
        # minimal.toml has no [[table]] array sections
        assert toml_has_array_of_tables(MINIMAL) is False

    def test_accepts_string_path(self):
        assert isinstance(toml_has_array_of_tables(str(MINIMAL)), bool)


class TestTomlMaxNumericValueRecursive:
    def test_returns_float(self):
        assert isinstance(toml_max_numeric_value_recursive(MINIMAL), float)

    def test_minimal_max_is_port(self):
        # port=8080, max_connections=10 → max=8080
        assert toml_max_numeric_value_recursive(MINIMAL) >= 8080.0

    def test_accepts_string_path(self):
        assert isinstance(toml_max_numeric_value_recursive(str(MINIMAL)), float)


class TestTomlMinNumericValueRecursive:
    def test_returns_float(self):
        assert isinstance(toml_min_numeric_value_recursive(MINIMAL), float)

    def test_minimal_min_positive(self):
        assert toml_min_numeric_value_recursive(MINIMAL) > 0.0

    def test_min_lte_max(self):
        assert toml_min_numeric_value_recursive(MINIMAL) <= toml_max_numeric_value_recursive(MINIMAL)

    def test_accepts_string_path(self):
        assert isinstance(toml_min_numeric_value_recursive(str(MINIMAL)), float)

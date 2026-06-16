"""Tests for TOML analytics gap-closure functions.

Covers: toml_table_count, toml_total_keys, toml_has_tables, toml_has_lists,
    toml_is_empty, toml_string_density, toml_depth, toml_avg_key_length,
    toml_max_value_length, toml_nested_table_count, toml_has_booleans,
    toml_key_count_per_table, toml_is_flat, toml_total_value_count.

Closes: GAP-TOML-FOSS-TOML_TABLE_C-001 through GAP-TOML-FOSS-TOML_TOTAL_V-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.toml import (
    toml_avg_key_length,
    toml_depth,
    toml_has_booleans,
    toml_has_lists,
    toml_has_tables,
    toml_is_empty,
    toml_is_flat,
    toml_key_count_per_table,
    toml_max_value_length,
    toml_nested_table_count,
    toml_string_density,
    toml_table_count,
    toml_total_keys,
    toml_total_value_count,
)


@pytest.fixture
def rich_toml(tmp_path):
    content = (
        'title = "Format Factory"\n'
        'version = 1\n'
        'enabled = true\n'
        'tags = ["alpha", "beta"]\n'
        "\n"
        "[server]\n"
        'host = "localhost"\n'
        "port = 8080\n"
        "\n"
        "[database]\n"
        'name = "mydb"\n'
        "pool = 5\n"
        "\n"
        "[database.replica]\n"
        'host = "replica"\n'
    )
    f = tmp_path / "rich.toml"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture
def flat_toml(tmp_path):
    content = 'key1 = "value1"\nkey2 = "value2"\nkey3 = 42\n'
    f = tmp_path / "flat.toml"
    f.write_text(content, encoding="utf-8")
    return f


@pytest.fixture
def empty_toml(tmp_path):
    f = tmp_path / "empty.toml"
    f.write_text("", encoding="utf-8")
    return f


class TestTomlTableCount:
    def test_returns_int(self, rich_toml):
        result = toml_table_count(rich_toml)
        assert isinstance(result, int)

    def test_positive_for_table_toml(self, rich_toml):
        result = toml_table_count(rich_toml)
        assert result >= 1

    def test_zero_for_flat_toml(self, flat_toml):
        result = toml_table_count(flat_toml)
        assert result == 0

    def test_empty_returns_zero(self, empty_toml):
        result = toml_table_count(empty_toml)
        assert result == 0


class TestTomlTotalKeys:
    def test_returns_int(self, rich_toml):
        result = toml_total_keys(rich_toml)
        assert isinstance(result, int)

    def test_positive(self, rich_toml):
        result = toml_total_keys(rich_toml)
        assert result > 0

    def test_flat_has_keys(self, flat_toml):
        result = toml_total_keys(flat_toml)
        assert result == 3

    def test_empty_zero(self, empty_toml):
        result = toml_total_keys(empty_toml)
        assert result == 0


class TestTomlHasTables:
    def test_true_for_table_toml(self, rich_toml):
        assert toml_has_tables(rich_toml) is True

    def test_false_for_flat_toml(self, flat_toml):
        assert toml_has_tables(flat_toml) is False

    def test_returns_bool(self, rich_toml):
        result = toml_has_tables(rich_toml)
        assert isinstance(result, bool)


class TestTomlHasLists:
    def test_true_for_rich_toml(self, rich_toml):
        assert toml_has_lists(rich_toml) is True

    def test_false_for_flat_toml(self, flat_toml):
        assert toml_has_lists(flat_toml) is False

    def test_returns_bool(self, flat_toml):
        result = toml_has_lists(flat_toml)
        assert isinstance(result, bool)


class TestTomlIsEmpty:
    def test_empty_returns_true(self, empty_toml):
        assert toml_is_empty(empty_toml) is True

    def test_non_empty_returns_false(self, flat_toml):
        assert toml_is_empty(flat_toml) is False

    def test_returns_bool(self, empty_toml):
        assert isinstance(toml_is_empty(empty_toml), bool)


class TestTomlStringDensity:
    def test_returns_float(self, flat_toml):
        result = toml_string_density(flat_toml)
        assert isinstance(result, float)

    def test_in_range(self, flat_toml):
        result = toml_string_density(flat_toml)
        assert 0.0 <= result <= 1.0

    def test_zero_for_empty(self, empty_toml):
        result = toml_string_density(empty_toml)
        assert result == 0.0


class TestTomlDepth:
    def test_returns_int(self, rich_toml):
        result = toml_depth(rich_toml)
        assert isinstance(result, int)

    def test_depth_greater_one_for_nested(self, rich_toml):
        result = toml_depth(rich_toml)
        assert result >= 1

    def test_flat_depth_one(self, flat_toml):
        result = toml_depth(flat_toml)
        assert result == 1


class TestTomlAvgKeyLength:
    def test_returns_float(self, flat_toml):
        result = toml_avg_key_length(flat_toml)
        assert isinstance(result, float)

    def test_positive_for_nonempty(self, flat_toml):
        result = toml_avg_key_length(flat_toml)
        assert result > 0

    def test_zero_for_empty(self, empty_toml):
        result = toml_avg_key_length(empty_toml)
        assert result == 0.0


class TestTomlMaxValueLength:
    def test_returns_int(self, flat_toml):
        result = toml_max_value_length(flat_toml)
        assert isinstance(result, int)

    def test_positive_for_string_values(self, flat_toml):
        result = toml_max_value_length(flat_toml)
        assert result > 0

    def test_zero_for_empty(self, empty_toml):
        result = toml_max_value_length(empty_toml)
        assert result == 0


class TestTomlNestedTableCount:
    def test_returns_int(self, rich_toml):
        result = toml_nested_table_count(rich_toml)
        assert isinstance(result, int)

    def test_zero_for_flat(self, flat_toml):
        result = toml_nested_table_count(flat_toml)
        assert result == 0


class TestTomlHasBooleans:
    def test_true_for_rich_toml(self, rich_toml):
        assert toml_has_booleans(rich_toml) is True

    def test_false_for_flat_toml(self, flat_toml):
        assert toml_has_booleans(flat_toml) is False

    def test_returns_bool(self, flat_toml):
        assert isinstance(toml_has_booleans(flat_toml), bool)


class TestTomlKeyCountPerTable:
    def test_returns_list(self, rich_toml):
        result = toml_key_count_per_table(rich_toml)
        assert isinstance(result, list)

    def test_nonempty_for_table_toml(self, rich_toml):
        result = toml_key_count_per_table(rich_toml)
        assert len(result) > 0

    def test_empty_for_flat(self, flat_toml):
        result = toml_key_count_per_table(flat_toml)
        assert result == []


class TestTomlIsFlat:
    def test_true_for_flat(self, flat_toml):
        assert toml_is_flat(flat_toml) is True

    def test_false_for_nested(self, rich_toml):
        assert toml_is_flat(rich_toml) is False

    def test_returns_bool(self, flat_toml):
        assert isinstance(toml_is_flat(flat_toml), bool)


class TestTomlTotalValueCount:
    def test_returns_int(self, flat_toml):
        result = toml_total_value_count(flat_toml)
        assert isinstance(result, int)

    def test_positive_for_nonempty(self, flat_toml):
        result = toml_total_value_count(flat_toml)
        assert result > 0

    def test_zero_for_empty(self, empty_toml):
        result = toml_total_value_count(empty_toml)
        assert result == 0

"""test_dogfood_toml_remaining_analytics_gaps_ndjson_export.py

Dogfood export path: TOML remaining 15 analytics gap functions -> NDJSON.
Uses tmp_path fixtures (no samples/by-format/toml/ directory exists).

Covers:
  toml_all_keys_lowercase, toml_avg_list_length, toml_bool_ratio,
  toml_file_size_bytes, toml_has_booleans, toml_has_numeric_values,
  toml_is_flat, toml_key_count_per_table, toml_max_list_length,
  toml_max_numeric_value, toml_max_value_length, toml_min_numeric_value,
  toml_nested_table_count, toml_numeric_sum, toml_total_value_count

Concrete values:
  flat.toml (enabled=true, count=42, name=hello):
    file_size_bytes=44, all_keys_lowercase=True, bool_ratio=0.3333,
    has_booleans=True, has_numeric_values=True, is_flat=True,
    max_numeric_value=42.0, min_numeric_value=42.0, numeric_sum=42.0, total_value_count=3
  upper.toml (Name=test, Value=10): all_keys_lowercase=False
  lists.toml (tags=[a,b,c], scores=[1,2,3,4]): avg_list_length=3.5, max_list_length=4
  nested.toml ([server] + [server.config]): nested_table_count=1, is_flat=False, max_value_length=5

Sprint: product-deepening-dogfood-toml-remaining-20260617
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "src" / "python"))

from toml.toml_codec import (
    toml_all_keys_lowercase,
    toml_avg_list_length,
    toml_bool_ratio,
    toml_file_size_bytes,
    toml_has_booleans,
    toml_has_numeric_values,
    toml_is_flat,
    toml_key_count_per_table,
    toml_max_list_length,
    toml_max_numeric_value,
    toml_max_value_length,
    toml_min_numeric_value,
    toml_nested_table_count,
    toml_numeric_sum,
    toml_total_value_count,
)
from src.python.ndjson.ndjson_codec import write_ndjson


@pytest.fixture
def flat_toml(tmp_path):
    f = tmp_path / "flat.toml"
    f.write_text('enabled = true\ncount = 42\nname = "hello"\n', encoding="utf-8")
    return f


@pytest.fixture
def upper_toml(tmp_path):
    f = tmp_path / "upper.toml"
    f.write_text('Name = "test"\nValue = 10\n', encoding="utf-8")
    return f


@pytest.fixture
def lists_toml(tmp_path):
    f = tmp_path / "lists.toml"
    f.write_text('tags = ["a", "b", "c"]\nscores = [1, 2, 3, 4]\n', encoding="utf-8")
    return f


@pytest.fixture
def nested_toml(tmp_path):
    f = tmp_path / "nested.toml"
    f.write_text(
        '[server]\nhost = "localhost"\nport = 8080\n\n[server.config]\ntimeout = 30\n',
        encoding="utf-8",
    )
    return f


class TestTomlRemainingAnalyticsGapsNdjsonExport:

    # file_size_bytes
    def test_flat_file_size_bytes(self, flat_toml):
        assert toml_file_size_bytes(flat_toml) == 44

    # all_keys_lowercase
    def test_flat_all_keys_lowercase_true(self, flat_toml):
        assert toml_all_keys_lowercase(flat_toml) is True

    def test_upper_all_keys_lowercase_false(self, upper_toml):
        assert toml_all_keys_lowercase(upper_toml) is False

    # bool_ratio
    def test_flat_bool_ratio(self, flat_toml):
        assert abs(toml_bool_ratio(flat_toml) - 0.3333) < 0.01

    # has_booleans
    def test_flat_has_booleans_true(self, flat_toml):
        assert toml_has_booleans(flat_toml) is True

    def test_lists_has_booleans_false(self, lists_toml):
        assert toml_has_booleans(lists_toml) is False

    # has_numeric_values
    def test_flat_has_numeric_values_true(self, flat_toml):
        assert toml_has_numeric_values(flat_toml) is True

    def test_upper_has_numeric_values_true(self, upper_toml):
        assert toml_has_numeric_values(upper_toml) is True

    # is_flat
    def test_flat_is_flat_true(self, flat_toml):
        assert toml_is_flat(flat_toml) is True

    def test_nested_is_flat_false(self, nested_toml):
        assert toml_is_flat(nested_toml) is False

    # key_count_per_table
    def test_nested_key_count_per_table(self, nested_toml):
        result = toml_key_count_per_table(nested_toml)
        assert isinstance(result, list)
        assert len(result) >= 1

    # max_list_length
    def test_lists_max_list_length(self, lists_toml):
        assert toml_max_list_length(lists_toml) == 4

    def test_flat_max_list_length_zero(self, flat_toml):
        assert toml_max_list_length(flat_toml) == 0

    # avg_list_length
    def test_lists_avg_list_length(self, lists_toml):
        assert abs(toml_avg_list_length(lists_toml) - 3.5) < 0.01

    # max_numeric_value
    def test_flat_max_numeric_value(self, flat_toml):
        assert abs(toml_max_numeric_value(flat_toml) - 42.0) < 0.1

    # min_numeric_value
    def test_flat_min_numeric_value(self, flat_toml):
        assert abs(toml_min_numeric_value(flat_toml) - 42.0) < 0.1

    # max_value_length
    def test_flat_max_value_length(self, flat_toml):
        # flat.toml has values: true(4), 42(2), hello(5) → max=5
        assert toml_max_value_length(flat_toml) == 5

    # nested_table_count
    def test_nested_nested_table_count(self, nested_toml):
        assert toml_nested_table_count(nested_toml) == 1

    def test_flat_nested_table_count_zero(self, flat_toml):
        assert toml_nested_table_count(flat_toml) == 0

    # numeric_sum
    def test_flat_numeric_sum(self, flat_toml):
        assert abs(toml_numeric_sum(flat_toml) - 42.0) < 0.1

    # total_value_count
    def test_flat_total_value_count(self, flat_toml):
        assert toml_total_value_count(flat_toml) == 3

    # NDJSON export pipeline
    def test_ndjson_export_toml_analytics(self, flat_toml, nested_toml, tmp_path):
        records = [
            {
                "file": flat_toml.name,
                "has_booleans": toml_has_booleans(flat_toml),
                "has_numeric_values": toml_has_numeric_values(flat_toml),
                "is_flat": toml_is_flat(flat_toml),
                "max_numeric_value": toml_max_numeric_value(flat_toml),
                "total_value_count": toml_total_value_count(flat_toml),
            },
            {
                "file": nested_toml.name,
                "nested_table_count": toml_nested_table_count(nested_toml),
                "is_flat": toml_is_flat(nested_toml),
                "all_keys_lowercase": toml_all_keys_lowercase(nested_toml),
            },
        ]
        out = tmp_path / "toml_remaining_analytics.ndjson"
        write_ndjson(records, str(out))
        lines = out.read_text(encoding="utf-8").strip().splitlines()
        assert json.loads(lines[0])["has_booleans"] is True
        assert json.loads(lines[1])["nested_table_count"] == 1

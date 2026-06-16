"""Tests for ndjson_is_homogeneous, ndjson_unique_field_count, ndjson_min_numeric_value,
ndjson_has_string_fields (Sprint 39).

Closes:
  GAP-NDJSON-FOSS-NDJSON_IS_HO-001  (Ndjson Is Homogeneous)
  GAP-NDJSON-FOSS-NDJSON_UNIQU-001   (Ndjson Unique Field Count)
  GAP-NDJSON-FOSS-NDJSON_MAX_N-001   (Ndjson Max Numeric Value)
  GAP-NDJSON-FOSS-NDJSON_MIN_N-001   (Ndjson Min Numeric Value)
  GAP-NDJSON-FOSS-NDJSON_HAS_S-001   (Ndjson Has String Fields)
"""
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import (
    ndjson_has_string_fields,
    ndjson_is_homogeneous,
    ndjson_max_numeric_value,
    ndjson_min_numeric_value,
    ndjson_unique_field_count,
)


def _write(tmp_path, records, name="test.ndjson") -> str:
    p = tmp_path / name
    with open(p, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return str(p)


class TestNdjsonIsHomogeneous:
    def test_return_type(self, tmp_path):
        p = _write(tmp_path, [{"a": 1}])
        assert isinstance(ndjson_is_homogeneous(p), bool)

    def test_true_for_same_schema(self, tmp_path):
        # All records have same keys
        p = _write(tmp_path, [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}])
        assert ndjson_is_homogeneous(p) is True

    def test_false_for_different_schemas(self, tmp_path):
        # Records have different keys
        p = _write(tmp_path, [{"name": "Alice", "age": 30}, {"city": "NYC", "pop": 8000000}])
        assert ndjson_is_homogeneous(p) is False

    def test_true_for_single_record(self, tmp_path):
        p = _write(tmp_path, [{"x": 1, "y": 2}])
        assert ndjson_is_homogeneous(p) is True

    def test_true_three_records_same_keys(self, tmp_path):
        p = _write(tmp_path, [{"id": i, "val": i * 10} for i in range(3)])
        assert ndjson_is_homogeneous(p) is True

    def test_consistent_across_calls(self, tmp_path):
        p = _write(tmp_path, [{"a": 1}, {"a": 2}])
        assert ndjson_is_homogeneous(p) == ndjson_is_homogeneous(p)


class TestNdjsonUniqueFieldCount:
    def test_return_type(self, tmp_path):
        p = _write(tmp_path, [{"a": 1, "b": 2}])
        assert isinstance(ndjson_unique_field_count(p), int)

    def test_exact_2_for_two_unique_fields(self, tmp_path):
        # Records share same 2 keys
        p = _write(tmp_path, [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}])
        assert ndjson_unique_field_count(p) == 2

    def test_exact_4_for_mixed_records(self, tmp_path):
        # union of keys: name, age, city, pop
        p = _write(tmp_path, [{"name": "Alice", "age": 30}, {"city": "NYC", "pop": 8000000}])
        assert ndjson_unique_field_count(p) == 4

    def test_exact_1_for_single_field(self, tmp_path):
        p = _write(tmp_path, [{"x": 1}, {"x": 2}, {"x": 3}])
        assert ndjson_unique_field_count(p) == 1

    def test_nonnegative(self, tmp_path):
        p = _write(tmp_path, [{"a": 1}])
        assert ndjson_unique_field_count(p) >= 0

    def test_consistent_across_calls(self, tmp_path):
        p = _write(tmp_path, [{"a": 1, "b": 2}])
        assert ndjson_unique_field_count(p) == ndjson_unique_field_count(p)


class TestNdjsonMaxNumericValue:
    def test_exact_35_for_ages(self, tmp_path):
        p = _write(tmp_path, [{"name": "A", "age": 30}, {"name": "B", "age": 25}, {"name": "C", "age": 35}])
        assert ndjson_max_numeric_value(p) == 35

    def test_exact_100_for_single_record(self, tmp_path):
        p = _write(tmp_path, [{"a": 100, "b": 50}])
        assert ndjson_max_numeric_value(p) == 100

    def test_none_for_text_only(self, tmp_path):
        p = _write(tmp_path, [{"a": "hello"}])
        assert ndjson_max_numeric_value(p) is None

    def test_consistent_across_calls(self, tmp_path):
        p = _write(tmp_path, [{"x": 5}])
        assert ndjson_max_numeric_value(p) == ndjson_max_numeric_value(p)


class TestNdjsonMinNumericValue:
    def test_return_type_for_numeric_file(self, tmp_path):
        p = _write(tmp_path, [{"x": 10}])
        result = ndjson_min_numeric_value(p)
        assert isinstance(result, (int, float))

    def test_exact_25_for_ages(self, tmp_path):
        # min age from [30, 25, 35] = 25
        p = _write(tmp_path, [{"name": "A", "age": 30}, {"name": "B", "age": 25}, {"name": "C", "age": 35}])
        assert ndjson_min_numeric_value(p) == 25

    def test_exact_5_for_single_record(self, tmp_path):
        p = _write(tmp_path, [{"a": 10, "b": 5}])
        assert ndjson_min_numeric_value(p) == 5

    def test_none_for_text_only(self, tmp_path):
        p = _write(tmp_path, [{"a": "hello"}])
        assert ndjson_min_numeric_value(p) is None

    def test_none_for_empty(self, tmp_path):
        p = tmp_path / "empty.ndjson"
        p.write_text("")
        assert ndjson_min_numeric_value(str(p)) is None

    def test_min_less_or_equal_max(self, tmp_path):
        p = _write(tmp_path, [{"x": 10, "y": 20}, {"x": 5, "y": 30}])
        assert ndjson_min_numeric_value(p) <= ndjson_max_numeric_value(p)

    def test_consistent_across_calls(self, tmp_path):
        p = _write(tmp_path, [{"x": 5}])
        assert ndjson_min_numeric_value(p) == ndjson_min_numeric_value(p)


class TestNdjsonHasStringFields:
    def test_return_type(self, tmp_path):
        p = _write(tmp_path, [{"a": "hello"}])
        assert isinstance(ndjson_has_string_fields(p), bool)

    def test_true_for_string_values(self, tmp_path):
        p = _write(tmp_path, [{"name": "Alice", "age": 30}])
        assert ndjson_has_string_fields(p) is True

    def test_false_for_numeric_only(self, tmp_path):
        p = _write(tmp_path, [{"a": 1, "b": 2}])
        assert ndjson_has_string_fields(p) is False

    def test_true_all_string_fields(self, tmp_path):
        p = _write(tmp_path, [{"city": "NYC", "country": "US"}])
        assert ndjson_has_string_fields(p) is True

    def test_consistent_across_calls(self, tmp_path):
        p = _write(tmp_path, [{"a": "hello"}])
        assert ndjson_has_string_fields(p) == ndjson_has_string_fields(p)

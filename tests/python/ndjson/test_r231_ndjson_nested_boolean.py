"""Tests for ndjson_nested_field_count and ndjson_boolean_field_count.

Product deepening: NDJSON analytics — TC-H3-002-NDJSON / PDC-NDJSON-NESTED-BOOLEAN-001.
"""
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import (
    ndjson_nested_field_count,
    ndjson_boolean_field_count,
)


def _make_ndjson(tmp_path, name, records):
    path = tmp_path / f"{name}.ndjson"
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return path


class TestNdjsonNestedFieldCount:
    def test_no_nested(self, tmp_path):
        f = _make_ndjson(tmp_path, "flat", [{"a": 1, "b": "x"}])
        assert ndjson_nested_field_count(f) == 0

    def test_dict_value(self, tmp_path):
        f = _make_ndjson(tmp_path, "dict", [{"a": {"nested": 1}, "b": 2}])
        assert ndjson_nested_field_count(f) == 1

    def test_list_value(self, tmp_path):
        f = _make_ndjson(tmp_path, "list", [{"a": [1, 2], "b": "x"}])
        assert ndjson_nested_field_count(f) == 1

    def test_multiple_records(self, tmp_path):
        records = [
            {"a": {"n": 1}, "b": [1]},
            {"c": "flat", "d": {"n": 2}},
        ]
        f = _make_ndjson(tmp_path, "multi", records)
        assert ndjson_nested_field_count(f) == 3

    def test_empty_file(self, tmp_path):
        path = tmp_path / "empty.ndjson"
        path.write_text("")
        assert ndjson_nested_field_count(path) == 0

    def test_from_list(self):
        records = [{"a": [1]}, {"b": 2}]
        assert ndjson_nested_field_count(records) == 1

    def test_returns_int(self, tmp_path):
        f = _make_ndjson(tmp_path, "type", [{"a": 1}])
        assert isinstance(ndjson_nested_field_count(f), int)


class TestNdjsonBooleanFieldCount:
    def test_no_booleans(self, tmp_path):
        f = _make_ndjson(tmp_path, "nobool", [{"a": 1, "b": "x"}])
        assert ndjson_boolean_field_count(f) == 0

    def test_with_booleans(self, tmp_path):
        f = _make_ndjson(tmp_path, "bools", [{"a": True, "b": False, "c": 1}])
        assert ndjson_boolean_field_count(f) == 2

    def test_multiple_records(self, tmp_path):
        records = [{"a": True}, {"b": False}, {"c": "x"}]
        f = _make_ndjson(tmp_path, "multi2", records)
        assert ndjson_boolean_field_count(f) == 2

    def test_empty_file(self, tmp_path):
        path = tmp_path / "empty2.ndjson"
        path.write_text("")
        assert ndjson_boolean_field_count(path) == 0

    def test_from_list(self):
        records = [{"a": True, "b": True}]
        assert ndjson_boolean_field_count(records) == 2

    def test_returns_int(self, tmp_path):
        f = _make_ndjson(tmp_path, "type2", [{"a": 1}])
        assert isinstance(ndjson_boolean_field_count(f), int)

"""Tests for ndjson_has_nested_objects and ndjson_average_record_size.

Product deepening: NDJSON analytics — TC-H3-002-NDJSON / PDC-NDJSON-NESTED-AVGSIZE-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import write_ndjson, ndjson_has_nested_objects, ndjson_average_record_size


def _make_ndjson(tmp_path, name, records):
    p = tmp_path / f"{name}.ndjson"
    write_ndjson(records, str(p))
    return str(p)


class TestNdjsonHasNestedObjects:
    def test_flat_records(self, tmp_path):
        p = _make_ndjson(tmp_path, "flat", [{"a": 1, "b": "x"}, {"a": 2, "b": "y"}])
        assert ndjson_has_nested_objects(p) is False

    def test_nested_dict(self, tmp_path):
        p = _make_ndjson(tmp_path, "nested_dict", [{"a": 1, "b": {"c": 2}}])
        assert ndjson_has_nested_objects(p) is True

    def test_nested_list(self, tmp_path):
        p = _make_ndjson(tmp_path, "nested_list", [{"a": [1, 2, 3]}])
        assert ndjson_has_nested_objects(p) is True

    def test_empty_records(self, tmp_path):
        p = _make_ndjson(tmp_path, "empty", [])
        assert ndjson_has_nested_objects(p) is False

    def test_returns_bool(self, tmp_path):
        p = _make_ndjson(tmp_path, "type", [{"x": 1}])
        assert isinstance(ndjson_has_nested_objects(p), bool)

    def test_in_memory(self):
        records = [{"a": 1}, {"b": {"nested": True}}]
        assert ndjson_has_nested_objects(records) is True


class TestNdjsonAverageRecordSize:
    def test_uniform_records(self, tmp_path):
        p = _make_ndjson(tmp_path, "uniform", [{"a": 1, "b": 2}, {"c": 3, "d": 4}])
        result = ndjson_average_record_size(p)
        assert result == 2.0

    def test_different_sizes(self, tmp_path):
        p = _make_ndjson(tmp_path, "diff", [{"a": 1}, {"a": 1, "b": 2, "c": 3}])
        result = ndjson_average_record_size(p)
        assert result == 2.0

    def test_empty(self, tmp_path):
        p = _make_ndjson(tmp_path, "empty2", [])
        assert ndjson_average_record_size(p) == 0.0

    def test_returns_float(self, tmp_path):
        p = _make_ndjson(tmp_path, "ft", [{"a": 1}])
        assert isinstance(ndjson_average_record_size(p), float)

    def test_in_memory(self):
        records = [{"a": 1, "b": 2}, {"c": 3}]
        result = ndjson_average_record_size(records)
        assert result == 1.5

"""Tests for ndjson_has_null_fields and ndjson_max_numeric_value (Sprint 40)."""
import sys
import json
import tempfile
import os
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_has_null_fields, ndjson_max_numeric_value


def _write_ndjson(tmp_path, records) -> str:
    p = tmp_path / "test.ndjson"
    with open(p, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return str(p)


class TestNdjsonHasNullFields:
    def test_return_type(self, tmp_path):
        p = _write_ndjson(tmp_path, [{"a": 1}])
        assert isinstance(ndjson_has_null_fields(p), bool)

    def test_true_when_null_present(self, tmp_path):
        p = _write_ndjson(tmp_path, [{"a": 1, "b": None}, {"a": 2, "b": 3}])
        assert ndjson_has_null_fields(p) is True

    def test_false_when_no_null(self, tmp_path):
        p = _write_ndjson(tmp_path, [{"a": 1, "b": 2}, {"a": 3, "b": 4}])
        assert ndjson_has_null_fields(p) is False

    def test_true_all_null(self, tmp_path):
        p = _write_ndjson(tmp_path, [{"x": None}])
        assert ndjson_has_null_fields(p) is True

    def test_false_for_empty_file(self, tmp_path):
        p = tmp_path / "empty.ndjson"
        p.write_text("")
        assert ndjson_has_null_fields(str(p)) is False

    def test_false_for_text_values(self, tmp_path):
        p = _write_ndjson(tmp_path, [{"a": "hello", "b": "world"}])
        assert ndjson_has_null_fields(p) is False

    def test_consistent_across_calls(self, tmp_path):
        p = _write_ndjson(tmp_path, [{"a": None}])
        assert ndjson_has_null_fields(p) == ndjson_has_null_fields(p)


class TestNdjsonMaxNumericValue:
    def test_return_type_for_numeric_file(self, tmp_path):
        p = _write_ndjson(tmp_path, [{"x": 10}])
        result = ndjson_max_numeric_value(p)
        assert isinstance(result, (int, float))

    def test_exact_max_for_two_records(self, tmp_path):
        p = _write_ndjson(tmp_path, [{"x": 10, "y": 20}, {"x": 5, "y": 30}])
        assert ndjson_max_numeric_value(p) == 30

    def test_exact_max_single_record(self, tmp_path):
        p = _write_ndjson(tmp_path, [{"a": 42, "b": 15}])
        assert ndjson_max_numeric_value(p) == 42

    def test_none_for_text_only(self, tmp_path):
        p = _write_ndjson(tmp_path, [{"a": "hello", "b": "world"}])
        assert ndjson_max_numeric_value(p) is None

    def test_none_for_empty(self, tmp_path):
        p = tmp_path / "empty.ndjson"
        p.write_text("")
        assert ndjson_max_numeric_value(str(p)) is None

    def test_ignores_booleans(self, tmp_path):
        # booleans are excluded (True=1, False=0 in Python but we exclude them)
        p = _write_ndjson(tmp_path, [{"flag": True, "value": 100}])
        assert ndjson_max_numeric_value(p) == 100

    def test_consistent_across_calls(self, tmp_path):
        p = _write_ndjson(tmp_path, [{"x": 5}])
        assert ndjson_max_numeric_value(p) == ndjson_max_numeric_value(p)

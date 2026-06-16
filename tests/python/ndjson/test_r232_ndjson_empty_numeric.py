"""Tests for ndjson_empty_record_count and ndjson_numeric_field_count.

Product deepening: NDJSON analytics — PDC-NDJSON-EMPTY-NUMERIC-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson import write_ndjson, ndjson_empty_record_count, ndjson_numeric_field_count


def _make_ndjson(tmp_path, name, records):
    p = tmp_path / f"{name}.ndjson"
    write_ndjson(records, str(p))
    return str(p)


class TestNdjsonEmptyRecordCount:
    def test_no_empty(self, tmp_path):
        p = _make_ndjson(tmp_path, "full", [{"a": 1}, {"b": 2}])
        assert ndjson_empty_record_count(p) == 0

    def test_one_empty(self, tmp_path):
        p = _make_ndjson(tmp_path, "one_empty", [{}, {"a": 1}])
        assert ndjson_empty_record_count(p) == 1

    def test_all_empty(self, tmp_path):
        p = _make_ndjson(tmp_path, "all_empty", [{}, {}, {}])
        assert ndjson_empty_record_count(p) == 3

    def test_returns_int(self, tmp_path):
        p = _make_ndjson(tmp_path, "ft", [{"x": 1}])
        assert isinstance(ndjson_empty_record_count(p), int)

    def test_non_negative(self, tmp_path):
        p = _make_ndjson(tmp_path, "nn", [{"a": "b"}])
        assert ndjson_empty_record_count(p) >= 0


class TestNdjsonNumericFieldCount:
    def test_all_numeric(self, tmp_path):
        p = _make_ndjson(tmp_path, "allnum", [{"a": 1, "b": 2.5}])
        assert ndjson_numeric_field_count(p) == 2

    def test_mixed(self, tmp_path):
        p = _make_ndjson(tmp_path, "mixed", [{"a": 1, "b": "text"}])
        assert ndjson_numeric_field_count(p) == 1

    def test_no_numeric(self, tmp_path):
        p = _make_ndjson(tmp_path, "nonum", [{"a": "x", "b": "y"}])
        assert ndjson_numeric_field_count(p) == 0

    def test_returns_int(self, tmp_path):
        p = _make_ndjson(tmp_path, "ft2", [{"a": 1}])
        assert isinstance(ndjson_numeric_field_count(p), int)

    def test_booleans_not_counted(self, tmp_path):
        p = _make_ndjson(tmp_path, "bool_t", [{"a": True, "b": False, "c": 1}])
        assert ndjson_numeric_field_count(p) == 1

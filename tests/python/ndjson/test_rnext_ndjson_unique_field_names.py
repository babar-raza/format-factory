"""Tests for ndjson_unique_field_names function."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import ndjson_unique_field_names


def _write_ndjson(tmp_path, lines, name="test.ndjson"):
    p = tmp_path / name
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(p)


class TestNdjsonUniqueFieldNames:
    def test_single_record(self, tmp_path):
        path = _write_ndjson(tmp_path, ['{"a": 1, "b": 2}'])
        assert ndjson_unique_field_names(path) == ["a", "b"]

    def test_multiple_records_same_fields(self, tmp_path):
        path = _write_ndjson(tmp_path, ['{"x": 1}', '{"x": 2}'])
        assert ndjson_unique_field_names(path) == ["x"]

    def test_different_fields(self, tmp_path):
        path = _write_ndjson(tmp_path, ['{"a": 1}', '{"b": 2}', '{"c": 3}'])
        assert ndjson_unique_field_names(path) == ["a", "b", "c"]

    def test_overlapping_fields(self, tmp_path):
        path = _write_ndjson(tmp_path, ['{"a": 1, "b": 2}', '{"b": 3, "c": 4}'])
        assert ndjson_unique_field_names(path) == ["a", "b", "c"]

    def test_empty_file(self, tmp_path):
        path = _write_ndjson(tmp_path, [])
        assert ndjson_unique_field_names(path) == []

    def test_in_memory_list(self):
        records = [{"x": 1, "y": 2}, {"y": 3, "z": 4}]
        assert ndjson_unique_field_names(records) == ["x", "y", "z"]

    def test_return_type_is_list(self, tmp_path):
        path = _write_ndjson(tmp_path, ['{"k": 1}'])
        assert isinstance(ndjson_unique_field_names(path), list)

    def test_importable_from_package(self):
        from ndjson import ndjson_unique_field_names as fn
        assert callable(fn)

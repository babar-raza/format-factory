"""
test_rnext_ndjson_write_ndjson.py -- Dedicated test coverage for write_ndjson.

Gap: GAP-NDJSON-FOSS-WRITE_NDJSON-001 (missing_test_coverage)
Tests: basic write, round-trip, empty list, single record, multi-type, error handling.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import (
    write_ndjson,
    load_ndjson,
    NdjsonError,
)


class TestWriteNdjsonBasic:
    def test_creates_file(self, tmp_path):
        dest = tmp_path / "out.ndjson"
        write_ndjson([{"a": 1}], str(dest))
        assert dest.exists()

    def test_file_not_empty(self, tmp_path):
        dest = tmp_path / "out.ndjson"
        write_ndjson([{"a": 1}], str(dest))
        assert dest.stat().st_size > 0

    def test_single_record(self, tmp_path):
        dest = tmp_path / "single.ndjson"
        write_ndjson([{"key": "value"}], str(dest))
        lines = dest.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        assert json.loads(lines[0]) == {"key": "value"}

    def test_multiple_records(self, tmp_path):
        dest = tmp_path / "multi.ndjson"
        records = [{"i": i} for i in range(5)]
        write_ndjson(records, str(dest))
        lines = dest.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 5

    def test_each_line_valid_json(self, tmp_path):
        dest = tmp_path / "valid.ndjson"
        records = [{"a": 1}, {"b": "two"}, {"c": [3]}]
        write_ndjson(records, str(dest))
        lines = dest.read_text(encoding="utf-8").strip().split("\n")
        for line in lines:
            parsed = json.loads(line)
            assert isinstance(parsed, dict)


class TestWriteNdjsonRoundTrip:
    def test_write_then_load(self, tmp_path):
        dest = tmp_path / "rt.ndjson"
        records = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 2
        assert loaded[0]["name"] == "Alice"
        assert loaded[1]["age"] == 25

    def test_roundtrip_preserves_types(self, tmp_path):
        dest = tmp_path / "types.ndjson"
        records = [{"int": 42, "float": 3.14, "bool": True, "null": None, "str": "hi"}]
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert loaded[0]["int"] == 42
        assert loaded[0]["bool"] is True
        assert loaded[0]["null"] is None


class TestWriteNdjsonEdgeCases:
    def test_empty_list(self, tmp_path):
        dest = tmp_path / "empty.ndjson"
        write_ndjson([], str(dest))
        assert dest.exists()
        content = dest.read_text(encoding="utf-8").strip()
        assert content == ""

    def test_nested_objects(self, tmp_path):
        dest = tmp_path / "nested.ndjson"
        records = [{"a": {"b": {"c": 1}}}]
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert loaded[0]["a"]["b"]["c"] == 1

    def test_unicode_content(self, tmp_path):
        dest = tmp_path / "unicode.ndjson"
        records = [{"text": "caf\u00e9"}]
        write_ndjson(records, str(dest))
        loaded = load_ndjson(str(dest))
        assert loaded[0]["text"] == "caf\u00e9"

    def test_accepts_path_object(self, tmp_path):
        dest = tmp_path / "pathobj.ndjson"
        write_ndjson([{"ok": True}], dest)
        assert dest.exists()

    def test_overwrite_existing(self, tmp_path):
        dest = tmp_path / "overwrite.ndjson"
        write_ndjson([{"v": 1}], str(dest))
        write_ndjson([{"v": 2}], str(dest))
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 1
        assert loaded[0]["v"] == 2

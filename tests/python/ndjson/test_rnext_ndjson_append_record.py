"""
test_rnext_ndjson_append_record.py -- Dedicated test coverage for append_record.

Gap: GAP-NDJSON-FOSS-APPEND_RECOR-001 (missing_test_coverage)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import append_record, load_ndjson, write_ndjson


class TestAppendRecordBasic:
    def test_creates_file_if_missing(self, tmp_path):
        dest = tmp_path / "new.ndjson"
        append_record(str(dest), {"key": "val"})
        assert dest.exists()

    def test_appends_single_record(self, tmp_path):
        dest = tmp_path / "out.ndjson"
        append_record(str(dest), {"a": 1})
        lines = dest.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        assert json.loads(lines[0]) == {"a": 1}

    def test_appends_multiple_records(self, tmp_path):
        dest = tmp_path / "out.ndjson"
        append_record(str(dest), {"i": 1})
        append_record(str(dest), {"i": 2})
        append_record(str(dest), {"i": 3})
        lines = dest.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 3

    def test_append_to_existing_file(self, tmp_path):
        dest = tmp_path / "existing.ndjson"
        write_ndjson([{"pre": True}], str(dest))
        append_record(str(dest), {"post": True})
        loaded = load_ndjson(str(dest))
        assert len(loaded) == 2
        assert loaded[0]["pre"] is True
        assert loaded[1]["post"] is True

    def test_append_preserves_prior_content(self, tmp_path):
        dest = tmp_path / "preserve.ndjson"
        write_ndjson([{"x": 1}, {"x": 2}], str(dest))
        append_record(str(dest), {"x": 3})
        loaded = load_ndjson(str(dest))
        assert loaded[0]["x"] == 1
        assert loaded[2]["x"] == 3


class TestAppendRecordEdgeCases:
    def test_append_nested_object(self, tmp_path):
        dest = tmp_path / "nested.ndjson"
        append_record(str(dest), {"a": {"b": [1, 2]}})
        loaded = load_ndjson(str(dest))
        assert loaded[0]["a"]["b"] == [1, 2]

    def test_append_unicode(self, tmp_path):
        dest = tmp_path / "uni.ndjson"
        append_record(str(dest), {"text": "caf\u00e9"})
        loaded = load_ndjson(str(dest))
        assert loaded[0]["text"] == "caf\u00e9"

    def test_append_null_value(self, tmp_path):
        dest = tmp_path / "null.ndjson"
        append_record(str(dest), {"v": None})
        loaded = load_ndjson(str(dest))
        assert loaded[0]["v"] is None

    def test_accepts_path_object(self, tmp_path):
        dest = tmp_path / "pathobj.ndjson"
        append_record(dest, {"ok": True})
        assert dest.exists()

"""Python NdjsonDocument.append_record() + save_to_file() + to_ndjson() roundtrip tests.

Sprint: FOSS-NDJSON-MUTATION-001 (run_id: d301c4faf016 next sprint)
Validates PQ-029 parity: Python NdjsonDocument gains same mutation API as .NET.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from ndjson.models import NdjsonDocument


# ─────────────────────────────────────────────────────────────────────────────
# append_record
# ─────────────────────────────────────────────────────────────────────────────

class TestAppendRecord:
    def test_append_increases_record_count(self):
        doc = NdjsonDocument([{"id": 1}])
        assert doc.record_count == 1
        doc.append_record({"id": 2})
        assert doc.record_count == 2

    def test_append_value_accessible(self):
        doc = NdjsonDocument([{"x": 10}])
        doc.append_record({"x": 99})
        assert doc.get_record(1) == {"x": 99}

    def test_append_none_raises(self):
        from ndjson.exceptions import NdjsonError
        doc = NdjsonDocument([])
        with pytest.raises(NdjsonError):
            doc.append_record(None)

    def test_append_multiple_records(self):
        doc = NdjsonDocument([])
        doc.append_record({"k": "v1"})
        doc.append_record({"k": "v2"})
        doc.append_record({"k": "v3"})
        assert doc.record_count == 3

    def test_append_list_record(self):
        doc = NdjsonDocument([])
        doc.append_record([1, 2, 3])
        assert doc.record_count == 1
        assert doc.get_record(0) == [1, 2, 3]

    def test_append_scalar_record(self):
        doc = NdjsonDocument([])
        doc.append_record(42)
        assert doc.get_record(0) == 42


# ─────────────────────────────────────────────────────────────────────────────
# to_ndjson
# ─────────────────────────────────────────────────────────────────────────────

class TestToNdjson:
    def test_empty_document_produces_empty_string(self):
        doc = NdjsonDocument([])
        assert doc.to_ndjson() == ""

    def test_single_record_lf_terminated(self):
        doc = NdjsonDocument([{"a": 1}])
        result = doc.to_ndjson()
        assert result.endswith("\n")
        parsed = json.loads(result.strip())
        assert parsed == {"a": 1}

    def test_multiple_records_each_on_own_line(self):
        doc = NdjsonDocument([{"n": 1}, {"n": 2}])
        lines = doc.to_ndjson().splitlines()
        assert len(lines) == 2
        assert json.loads(lines[0]) == {"n": 1}
        assert json.loads(lines[1]) == {"n": 2}


# ─────────────────────────────────────────────────────────────────────────────
# save_to_file
# ─────────────────────────────────────────────────────────────────────────────

class TestSaveToFile:
    def test_save_creates_file(self, tmp_path):
        doc = NdjsonDocument([{"a": 1}])
        path = tmp_path / "out.ndjson"
        doc.save_to_file(path)
        assert path.exists()

    def test_save_empty_path_raises(self):
        from ndjson.exceptions import NdjsonError
        doc = NdjsonDocument([])
        with pytest.raises(NdjsonError):
            doc.save_to_file("")

    def test_save_creates_parent_dirs(self, tmp_path):
        doc = NdjsonDocument([{"x": 1}])
        nested = tmp_path / "a" / "b" / "out.ndjson"
        doc.save_to_file(nested)
        assert nested.exists()


# ─────────────────────────────────────────────────────────────────────────────
# Roundtrip: append_record → save_to_file → from_file → assert
# ─────────────────────────────────────────────────────────────────────────────

class TestAppendRoundtrip:
    def test_roundtrip_preserves_appended_record(self, tmp_path):
        doc = NdjsonDocument([{"name": "Alice", "score": 90}])
        doc.append_record({"name": "Bob", "score": 75})
        assert doc.record_count == 2

        path = tmp_path / "roundtrip.ndjson"
        doc.save_to_file(path)

        doc2 = NdjsonDocument.from_file(path)
        assert doc2.record_count == 2
        names = [doc2.get_field(i, "name") for i in range(2)]
        assert "Alice" in names
        assert "Bob" in names

    def test_roundtrip_multiple_appends(self, tmp_path):
        doc = NdjsonDocument([])
        doc.append_record({"k": "v1"})
        doc.append_record({"k": "v2"})
        doc.append_record({"k": "v3"})

        path = tmp_path / "multi.ndjson"
        doc.save_to_file(path)

        doc2 = NdjsonDocument.from_file(path)
        assert doc2.record_count == 3
        values = [doc2.get_field(i, "k") for i in range(3)]
        assert values == ["v1", "v2", "v3"]

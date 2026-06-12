"""
tests/python/ndjson/test_r123_ndjson_append_filter.py

Sprint: FORMAT-FACTORY-EXPANDED-STANDING-MULTI-LANE-PRODUCT-FIRST-MEGA-TRAIN-001
TC-NDJSON-APPEND: append_record()
TC-NDJSON-FILTER: filter_records()
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    append_record,
    filter_records,
    write_ndjson,
    load_ndjson,
)


def _tmp() -> Path:
    return Path(tempfile.mktemp(suffix=".ndjson"))


_SAMPLE_RECORDS = [
    {"id": 1, "name": "Alice", "role": "admin"},
    {"id": 2, "name": "Bob", "role": "user"},
    {"id": 3, "name": "Carol", "role": "user"},
    {"id": 4, "name": "Dave", "role": "admin"},
]


class TestAppendRecord:
    def test_creates_file(self):
        out = _tmp()
        try:
            append_record(out, {"x": 1})
            assert out.exists()
        finally:
            out.unlink(missing_ok=True)

    def test_appends_to_existing(self):
        out = _tmp()
        try:
            write_ndjson([{"a": 1}], out)
            append_record(out, {"b": 2})
            records = load_ndjson(out)
            assert len(records) == 2
            assert records[0] == {"a": 1}
            assert records[1] == {"b": 2}
        finally:
            out.unlink(missing_ok=True)

    def test_creates_new_file(self):
        out = _tmp()
        try:
            assert not out.exists()
            append_record(out, {"new": True})
            assert out.exists()
            records = load_ndjson(out)
            assert records == [{"new": True}]
        finally:
            out.unlink(missing_ok=True)

    def test_multiple_appends(self):
        out = _tmp()
        try:
            for i in range(5):
                append_record(out, {"i": i})
            records = load_ndjson(out)
            assert len(records) == 5
            assert records[4] == {"i": 4}
        finally:
            out.unlink(missing_ok=True)

    def test_accepts_string_path(self):
        out = _tmp()
        try:
            append_record(str(out), {"x": 1})
            assert out.exists()
        finally:
            out.unlink(missing_ok=True)

    def test_appended_line_is_valid_json(self):
        out = _tmp()
        try:
            append_record(out, {"key": "value", "num": 42})
            lines = [l.strip() for l in out.read_text().splitlines() if l.strip()]
            assert len(lines) == 1
            parsed = json.loads(lines[0])
            assert parsed == {"key": "value", "num": 42}
        finally:
            out.unlink(missing_ok=True)

    def test_unicode_value(self):
        out = _tmp()
        try:
            append_record(out, {"name": "Zoë — café"})
            content = out.read_text(encoding="utf-8")
            assert "Zoë" in content
        finally:
            out.unlink(missing_ok=True)

    def test_non_dict_record(self):
        out = _tmp()
        try:
            append_record(out, [1, 2, 3])
            records = load_ndjson(out)
            assert records == [[1, 2, 3]]
        finally:
            out.unlink(missing_ok=True)

    def test_null_record(self):
        out = _tmp()
        try:
            append_record(out, None)
            records = load_ndjson(out)
            assert records == [None]
        finally:
            out.unlink(missing_ok=True)

    def test_file_ends_with_newline(self):
        out = _tmp()
        try:
            append_record(out, {"x": 1})
            assert out.read_text().endswith("\n")
        finally:
            out.unlink(missing_ok=True)


class TestFilterRecords:
    def _write_sample(self, path: Path) -> None:
        write_ndjson(_SAMPLE_RECORDS, path)

    def test_returns_list(self):
        out = _tmp()
        try:
            self._write_sample(out)
            result = filter_records(out, "role", "admin")
            assert isinstance(result, list)
        finally:
            out.unlink(missing_ok=True)

    def test_filter_by_role(self):
        out = _tmp()
        try:
            self._write_sample(out)
            result = filter_records(out, "role", "admin")
            assert len(result) == 2
            assert all(r["role"] == "admin" for r in result)
        finally:
            out.unlink(missing_ok=True)

    def test_filter_by_id(self):
        out = _tmp()
        try:
            self._write_sample(out)
            result = filter_records(out, "id", 2)
            assert len(result) == 1
            assert result[0]["name"] == "Bob"
        finally:
            out.unlink(missing_ok=True)

    def test_no_match_returns_empty(self):
        out = _tmp()
        try:
            self._write_sample(out)
            result = filter_records(out, "role", "superuser")
            assert result == []
        finally:
            out.unlink(missing_ok=True)

    def test_non_dict_records_excluded(self):
        out = _tmp()
        try:
            write_ndjson([{"x": 1}, [1, 2], "hello", {"x": 2}], out)
            result = filter_records(out, "x", 1)
            assert len(result) == 1
            assert result[0] == {"x": 1}
        finally:
            out.unlink(missing_ok=True)

    def test_accepts_bytes(self):
        out = _tmp()
        try:
            self._write_sample(out)
            result = filter_records(out.read_bytes(), "role", "user")
            assert len(result) == 2
        finally:
            out.unlink(missing_ok=True)

    def test_empty_source(self):
        result = filter_records(b"", "key", "val")
        assert result == []

    def test_package_import(self):
        import sys
        sys.path.insert(0, str(_REPO))
        from src.python.ndjson import append_record as ap, filter_records as fr
        assert callable(ap)
        assert callable(fr)

    def test_in_all(self):
        import sys
        sys.path.insert(0, str(_REPO))
        import src.python.ndjson as ndjson_pkg
        assert "append_record" in ndjson_pkg.__all__
        assert "filter_records" in ndjson_pkg.__all__

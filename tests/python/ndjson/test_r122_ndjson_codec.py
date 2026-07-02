"""
tests/python/ndjson/test_r122_ndjson_codec.py

Sprint: FORMAT-FACTORY-STANDING-MULTI-LANE-PRODUCT-FIRST-MEGA-TRAIN-001
Lane 7: NDJSON format kickstart
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import probe_ndjson, load_ndjson, write_ndjson, get_record_count, NdjsonParseError


_SIMPLE_NDJSON = b'{"id":1,"name":"Alice"}\n{"id":2,"name":"Bob"}\n'
_NDJSON_NUMBERS = b'1\n2\n3\n'
_NDJSON_MIXED = b'{"x":1}\n[1,2,3]\n"hello"\ntrue\n42\n'
_BAD_JSON = b'{"ok":true}\nnot valid json\n'
_EMPTY = b''


def _tmp() -> Path:
    return Path(tempfile.mktemp(suffix=".ndjson"))


class TestProbeNdjson:
    def test_valid_ndjson_true(self):
        assert probe_ndjson(_SIMPLE_NDJSON) is True

    def test_numbers_ndjson_true(self):
        assert probe_ndjson(_NDJSON_NUMBERS) is True

    def test_invalid_returns_false(self):
        assert probe_ndjson(b"not json at all!!!") is False

    def test_empty_returns_false(self):
        assert probe_ndjson(_EMPTY) is False

    def test_returns_bool(self):
        assert isinstance(probe_ndjson(_SIMPLE_NDJSON), bool)

    def test_does_not_raise(self):
        probe_ndjson(b"\xff\xfe\xfd garbage")
        probe_ndjson(b"")
        assert 1 == 1  # no exception is the assertion

    def test_mixed_types_true(self):
        assert probe_ndjson(_NDJSON_MIXED) is True


class TestLoadNdjson:
    def test_returns_list(self):
        result = load_ndjson(_SIMPLE_NDJSON)
        assert isinstance(result, list)

    def test_correct_count(self):
        result = load_ndjson(_SIMPLE_NDJSON)
        assert len(result) == 2

    def test_first_record(self):
        result = load_ndjson(_SIMPLE_NDJSON)
        assert result[0]["name"] == "Alice"

    def test_second_record(self):
        result = load_ndjson(_SIMPLE_NDJSON)
        assert result[1]["id"] == 2

    def test_empty_lines_skipped(self):
        data = b'{"a":1}\n\n\n{"b":2}\n'
        result = load_ndjson(data)
        assert len(result) == 2

    def test_numbers_loaded(self):
        result = load_ndjson(_NDJSON_NUMBERS)
        assert result == [1, 2, 3]

    def test_mixed_types(self):
        result = load_ndjson(_NDJSON_MIXED)
        assert isinstance(result[0], dict)
        assert isinstance(result[1], list)
        assert result[2] == "hello"
        assert result[3] is True
        assert result[4] == 42

    def test_invalid_line_raises(self):
        try:
            load_ndjson(_BAD_JSON)
            assert 1 == 0, "Expected NdjsonParseError"

        except NdjsonParseError:
            pass

    def test_empty_returns_empty_list(self):
        result = load_ndjson(_EMPTY)
        assert result == []

    def test_accepts_path(self):
        out = _tmp()
        try:
            out.write_bytes(_SIMPLE_NDJSON)
            result = load_ndjson(out)
            assert len(result) == 2
        finally:
            out.unlink(missing_ok=True)


class TestWriteNdjson:
    def test_creates_file(self):
        out = _tmp()
        try:
            write_ndjson([{"x": 1}], out)
            assert out.exists()
        finally:
            out.unlink(missing_ok=True)

    def test_single_record(self):
        out = _tmp()
        try:
            write_ndjson([{"id": 1}], out)
            line = out.read_text().strip()
            assert json.loads(line) == {"id": 1}
        finally:
            out.unlink(missing_ok=True)

    def test_multiple_records(self):
        out = _tmp()
        try:
            write_ndjson([{"a": 1}, {"b": 2}], out)
            lines = [l for l in out.read_text().splitlines() if l.strip()]
            assert len(lines) == 2
        finally:
            out.unlink(missing_ok=True)

    def test_file_ends_with_newline(self):
        out = _tmp()
        try:
            write_ndjson([{"x": 1}], out)
            assert out.read_text().endswith("\n")
        finally:
            out.unlink(missing_ok=True)

    def test_empty_list_produces_empty_file(self):
        out = _tmp()
        try:
            write_ndjson([], out)
            assert out.read_text() == ""
        finally:
            out.unlink(missing_ok=True)

    def test_accepts_string_path(self):
        out = _tmp()
        try:
            write_ndjson([{"x": 1}], str(out))
            assert out.exists()
        finally:
            out.unlink(missing_ok=True)

    def test_unicode_in_values(self):
        out = _tmp()
        try:
            write_ndjson([{"name": "héllo wörld"}], out)
            content = out.read_text(encoding="utf-8")
            assert "héllo wörld" in content
        finally:
            out.unlink(missing_ok=True)

    def test_various_types(self):
        out = _tmp()
        records = [{"x": 1}, [1, 2, 3], "hello", True, 42, None]
        try:
            write_ndjson(records, out)
            loaded = load_ndjson(out)
            assert loaded[0] == {"x": 1}
            assert loaded[1] == [1, 2, 3]
            assert loaded[2] == "hello"
            assert loaded[3] is True
            assert loaded[4] == 42
            assert loaded[5] is None
        finally:
            out.unlink(missing_ok=True)


class TestNdjsonRoundtrip:
    def test_full_roundtrip(self):
        records = [
            {"id": 1, "name": "Alice", "score": 95.5},
            {"id": 2, "name": "Bob", "score": 88.0},
            {"id": 3, "name": "Carol", "score": 91.2},
        ]
        out = _tmp()
        try:
            write_ndjson(records, out)
            loaded = load_ndjson(out)
            assert loaded == records
        finally:
            out.unlink(missing_ok=True)

    def test_record_count(self):
        out = _tmp()
        records = [{"i": i} for i in range(10)]
        try:
            write_ndjson(records, out)
            assert get_record_count(out) == 10
        finally:
            out.unlink(missing_ok=True)

    def test_probe_after_write(self):
        out = _tmp()
        try:
            write_ndjson([{"x": 1}], out)
            assert probe_ndjson(out) is True
        finally:
            out.unlink(missing_ok=True)

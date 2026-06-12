"""Tests for NDJSON count_records().

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-2-001
"""
from __future__ import annotations

import sys
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

from src.python.ndjson.ndjson_codec import count_records, get_record_count


THREE_RECORDS = b'{"a": 1}\n{"b": 2}\n{"c": 3}\n'
MIXED_TYPES = b'"string"\n42\ntrue\nnull\n[1,2]\n{"key":"val"}\n'
WITH_BLANKS = b'{"a": 1}\n\n{"b": 2}\n   \n{"c": 3}\n'


class TestCountRecords:
    def test_basic_count(self):
        assert count_records(THREE_RECORDS) == 3

    def test_empty_source(self):
        assert count_records(b"") == 0

    def test_blank_lines_excluded(self):
        assert count_records(WITH_BLANKS) == 3

    def test_mixed_types_counted(self):
        assert count_records(MIXED_TYPES) == 6

    def test_single_record(self):
        assert count_records(b'{"x": 1}\n') == 1

    def test_returns_int(self):
        result = count_records(THREE_RECORDS)
        assert isinstance(result, int)

    def test_file_source(self, tmp_path):
        f = tmp_path / "data.ndjson"
        f.write_bytes(THREE_RECORDS)
        assert count_records(f) == 3

    def test_string_content(self):
        content = '{"a":1}\n{"b":2}\n'
        assert count_records(content) == 2

    def test_consistent_with_get_record_count(self):
        assert count_records(THREE_RECORDS) == get_record_count(THREE_RECORDS)
        assert count_records(MIXED_TYPES) == get_record_count(MIXED_TYPES)
        assert count_records(b"") == get_record_count(b"")

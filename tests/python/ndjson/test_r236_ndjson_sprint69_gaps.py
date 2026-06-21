"""Tests for NDJSON Sprint 69 gap closure.

Closes:
  GAP-NDJSON-FOSS-NDJSON_MAX_R-001   (Ndjson Max Record Key Count)
"""
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_max_record_key_count


class TestNdjsonMaxRecordKeyCount:
    def test_return_type(self, tmp_path):
        f = tmp_path / "t.ndjson"
        f.write_bytes((json.dumps({"a": 1}) + "\n").encode())
        assert isinstance(ndjson_max_record_key_count(str(f)), int)

    def test_exact_3_for_long_short(self, tmp_path):
        f = tmp_path / "ls.ndjson"
        f.write_bytes(
            (json.dumps({"a": 1, "b": 2, "c": 3}) + "\n" + json.dumps({"a": 1}) + "\n").encode()
        )
        assert ndjson_max_record_key_count(str(f)) == 3

    def test_exact_2_for_two_keys(self, tmp_path):
        f = tmp_path / "two.ndjson"
        f.write_bytes((json.dumps({"x": 1, "y": 2}) + "\n").encode())
        assert ndjson_max_record_key_count(str(f)) == 2

    def test_exact_1_for_one_key(self, tmp_path):
        f = tmp_path / "one.ndjson"
        f.write_bytes((json.dumps({"z": 1}) + "\n").encode())
        assert ndjson_max_record_key_count(str(f)) == 1

    def test_zero_for_empty(self, tmp_path):
        f = tmp_path / "empty.ndjson"
        f.write_text("")
        assert ndjson_max_record_key_count(str(f)) == 0

    def test_consistent_across_calls(self, tmp_path):
        f = tmp_path / "c.ndjson"
        f.write_bytes((json.dumps({"a": 1, "b": 2}) + "\n").encode())
        assert ndjson_max_record_key_count(str(f)) == ndjson_max_record_key_count(str(f))

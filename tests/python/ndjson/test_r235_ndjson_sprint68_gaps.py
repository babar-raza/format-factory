"""Tests for NDJSON Sprint 68 gap closure.

Closes:
  GAP-NDJSON-FOSS-NDJSON_DICT_-001   (Ndjson Dict Field Total)
"""
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_dict_field_total


class TestNdjsonDictFieldTotal:
    def test_return_type(self, tmp_path):
        f = tmp_path / "t.ndjson"
        f.write_bytes((json.dumps({"a": 1}) + "\n").encode())
        assert isinstance(ndjson_dict_field_total(str(f)), int)

    def test_exact_4_for_two_records(self, tmp_path):
        f = tmp_path / "two.ndjson"
        f.write_bytes(
            (json.dumps({"a": 1, "b": 2}) + "\n" + json.dumps({"a": 3, "c": 4}) + "\n").encode()
        )
        assert ndjson_dict_field_total(str(f)) == 4

    def test_exact_1_for_single(self, tmp_path):
        f = tmp_path / "single.ndjson"
        f.write_bytes((json.dumps({"x": 1}) + "\n").encode())
        assert ndjson_dict_field_total(str(f)) == 1

    def test_zero_for_empty(self, tmp_path):
        f = tmp_path / "empty.ndjson"
        f.write_text("")
        assert ndjson_dict_field_total(str(f)) == 0

    def test_nonnegative(self, tmp_path):
        f = tmp_path / "n.ndjson"
        f.write_bytes((json.dumps({"a": 1}) + "\n").encode())
        assert ndjson_dict_field_total(str(f)) >= 0

    def test_consistent_across_calls(self, tmp_path):
        f = tmp_path / "c.ndjson"
        f.write_bytes((json.dumps({"a": 1, "b": 2}) + "\n").encode())
        assert ndjson_dict_field_total(str(f)) == ndjson_dict_field_total(str(f))

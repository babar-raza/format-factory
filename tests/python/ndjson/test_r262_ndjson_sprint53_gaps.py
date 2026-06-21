"""Tests for NDJSON Sprint 53 gap closure.

Closes:
  GAP-NDJSON-FOSS-NDJSON_MAX_L-001  (Ndjson Max List Length)
"""
import sys
import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_max_list_length


class TestNdjsonMaxListLength:
    def test_return_type(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text(json.dumps({"a": [1, 2, 3]}) + "\n")
        assert isinstance(ndjson_max_list_length(str(f)), int)

    def test_exact_3_for_list_of_3(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text(json.dumps({"a": [1, 2, 3], "b": [4, 5]}) + "\n")
        assert ndjson_max_list_length(str(f)) == 3

    def test_zero_for_no_lists(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text(json.dumps({"x": 1, "y": "hello"}) + "\n")
        assert ndjson_max_list_length(str(f)) == 0

    def test_max_across_records(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text(
            json.dumps({"a": [1, 2, 3]}) + "\n"
            + json.dumps({"a": [6]}) + "\n"
        )
        assert ndjson_max_list_length(str(f)) == 3

    def test_nonnegative(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text(json.dumps({"x": 1}) + "\n")
        assert ndjson_max_list_length(str(f)) >= 0

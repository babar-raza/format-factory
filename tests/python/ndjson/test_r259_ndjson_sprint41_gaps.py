"""Tests for NDJSON Sprint 41 gap closure.

Closes:
  GAP-NDJSON-FOSS-NDJSON_AVG_-001  (Ndjson Avg Record Depth)
  GAP-NDJSON-FOSS-NDJSON_NON-001  (Ndjson Nonempty Record Count)
  GAP-NDJSON-FOSS-NDJSON_MAX-001  (Ndjson Max Key Count)
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_avg_record_depth, ndjson_max_key_count, ndjson_nonempty_record_count


@pytest.fixture
def flat_two_records_file(tmp_path):
    p = tmp_path / "flat_two.ndjson"
    p.write_text(
        json.dumps({"a": 1, "b": 2, "c": 3}) + "\n"
        + json.dumps({"x": 4}) + "\n"
    )
    return str(p)


@pytest.fixture
def three_records_file(tmp_path):
    p = tmp_path / "three.ndjson"
    p.write_text(
        json.dumps({"a": 1, "b": 2, "c": 3}) + "\n"
        + json.dumps({"x": 4}) + "\n"
        + json.dumps({"y": 5, "z": 6}) + "\n"
    )
    return str(p)


@pytest.fixture
def single_flat_file(tmp_path):
    p = tmp_path / "single.ndjson"
    p.write_text(json.dumps({"key1": "v1", "key2": "v2", "key3": "v3", "key4": "v4"}) + "\n")
    return str(p)


class TestNdjsonAvgRecordDepth:
    def test_return_type(self, flat_two_records_file):
        assert isinstance(ndjson_avg_record_depth(flat_two_records_file), float)

    def test_exact_1_0_for_flat_records(self, flat_two_records_file):
        assert ndjson_avg_record_depth(flat_two_records_file) == 1.0

    def test_positive(self, flat_two_records_file):
        assert ndjson_avg_record_depth(flat_two_records_file) > 0

    def test_consistent_across_calls(self, flat_two_records_file):
        assert ndjson_avg_record_depth(flat_two_records_file) == ndjson_avg_record_depth(flat_two_records_file)


class TestNdjsonNonemptyRecordCount:
    def test_return_type(self, flat_two_records_file):
        assert isinstance(ndjson_nonempty_record_count(flat_two_records_file), int)

    def test_exact_2_for_two_records(self, flat_two_records_file):
        assert ndjson_nonempty_record_count(flat_two_records_file) == 2

    def test_exact_3_for_three_records(self, three_records_file):
        assert ndjson_nonempty_record_count(three_records_file) == 3

    def test_positive(self, flat_two_records_file):
        assert ndjson_nonempty_record_count(flat_two_records_file) > 0

    def test_consistent_across_calls(self, flat_two_records_file):
        assert ndjson_nonempty_record_count(flat_two_records_file) == ndjson_nonempty_record_count(flat_two_records_file)


class TestNdjsonMaxKeyCount:
    def test_return_type(self, flat_two_records_file):
        assert isinstance(ndjson_max_key_count(flat_two_records_file), int)

    def test_exact_3_for_three_records(self, three_records_file):
        assert ndjson_max_key_count(three_records_file) == 3

    def test_exact_4_for_single_flat(self, single_flat_file):
        assert ndjson_max_key_count(single_flat_file) == 4

    def test_positive(self, flat_two_records_file):
        assert ndjson_max_key_count(flat_two_records_file) > 0

    def test_consistent_across_calls(self, three_records_file):
        assert ndjson_max_key_count(three_records_file) == ndjson_max_key_count(three_records_file)

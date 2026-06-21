"""Tests for NDJSON Sprint 41 batch 2 gap closure.

Closes:
  GAP-NDJSON-FOSS-NDJSON_AVG_K-001  (Ndjson Avg Key Count)
  GAP-NDJSON-FOSS-NDJSON_DISTI-001  (Ndjson Distinct Key Count)
  GAP-NDJSON-FOSS-NDJSON_BOOL_-001  (Ndjson Bool Field Count)
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_avg_key_count, ndjson_bool_field_count, ndjson_distinct_key_count


@pytest.fixture
def mixed_file(tmp_path):
    p = tmp_path / "mixed.ndjson"
    p.write_text(
        json.dumps({"a": 1, "b": True, "c": 3}) + "\n"
        + json.dumps({"a": 4, "d": 5}) + "\n"
    )
    return str(p)


@pytest.fixture
def single_record_file(tmp_path):
    p = tmp_path / "single.ndjson"
    p.write_text(json.dumps({"x": 1, "y": 2, "z": 3}) + "\n")
    return str(p)


class TestNdjsonAvgKeyCount:
    def test_return_type(self, mixed_file):
        assert isinstance(ndjson_avg_key_count(mixed_file), float)

    def test_exact_2_5_for_mixed(self, mixed_file):
        assert ndjson_avg_key_count(mixed_file) == 2.5

    def test_exact_3_0_for_single_record(self, single_record_file):
        assert ndjson_avg_key_count(single_record_file) == 3.0

    def test_positive(self, mixed_file):
        assert ndjson_avg_key_count(mixed_file) > 0

    def test_consistent_across_calls(self, mixed_file):
        assert ndjson_avg_key_count(mixed_file) == ndjson_avg_key_count(mixed_file)


class TestNdjsonDistinctKeyCount:
    def test_return_type(self, mixed_file):
        assert isinstance(ndjson_distinct_key_count(mixed_file), int)

    def test_exact_4_for_mixed(self, mixed_file):
        assert ndjson_distinct_key_count(mixed_file) == 4

    def test_exact_3_for_single_record(self, single_record_file):
        assert ndjson_distinct_key_count(single_record_file) == 3

    def test_positive(self, mixed_file):
        assert ndjson_distinct_key_count(mixed_file) > 0

    def test_consistent_across_calls(self, mixed_file):
        assert ndjson_distinct_key_count(mixed_file) == ndjson_distinct_key_count(mixed_file)


class TestNdjsonBoolFieldCount:
    def test_return_type(self, mixed_file):
        assert isinstance(ndjson_bool_field_count(mixed_file), int)

    def test_exact_1_for_mixed(self, mixed_file):
        assert ndjson_bool_field_count(mixed_file) == 1

    def test_zero_for_single_record(self, single_record_file):
        assert ndjson_bool_field_count(single_record_file) == 0

    def test_nonnegative(self, mixed_file):
        assert ndjson_bool_field_count(mixed_file) >= 0

    def test_consistent_across_calls(self, mixed_file):
        assert ndjson_bool_field_count(mixed_file) == ndjson_bool_field_count(mixed_file)

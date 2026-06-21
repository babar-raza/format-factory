"""Tests for NDJSON Sprint 47 gap closure.

Closes:
  GAP-NDJSON-FOSS-NDJSON_HAS_A-001  (Ndjson Has All Same Keys)
  GAP-NDJSON-FOSS-NDJSON_ARRAY-001  (Ndjson Array Field Count)
"""
import sys
import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_has_all_same_keys, ndjson_array_field_count


@pytest.fixture
def same_keys_file(tmp_path):
    f = tmp_path / "same_keys.ndjson"
    f.write_text('{"a":1,"b":2}\n{"a":3,"b":4}\n')
    return str(f)


@pytest.fixture
def diff_keys_file(tmp_path):
    f = tmp_path / "diff_keys.ndjson"
    f.write_text('{"a":1,"b":2}\n{"a":3,"c":4}\n')
    return str(f)


@pytest.fixture
def array_file(tmp_path):
    f = tmp_path / "arrays.ndjson"
    f.write_text('{"a":[1,2],"b":3}\n{"a":[4,5,6],"b":7}\n')
    return str(f)


@pytest.fixture
def no_array_file(tmp_path):
    f = tmp_path / "no_arrays.ndjson"
    f.write_text('{"a":1,"b":2}\n{"a":3,"b":4}\n')
    return str(f)


class TestNdjsonHasAllSameKeys:
    def test_return_type(self, same_keys_file):
        assert isinstance(ndjson_has_all_same_keys(same_keys_file), bool)

    def test_true_when_all_records_have_same_keys(self, same_keys_file):
        assert ndjson_has_all_same_keys(same_keys_file) is True

    def test_false_when_keys_differ(self, diff_keys_file):
        assert ndjson_has_all_same_keys(diff_keys_file) is False

    def test_consistent_across_calls(self, same_keys_file):
        assert ndjson_has_all_same_keys(same_keys_file) == ndjson_has_all_same_keys(same_keys_file)


class TestNdjsonArrayFieldCount:
    def test_return_type(self, array_file):
        assert isinstance(ndjson_array_field_count(array_file), int)

    def test_exact_2_for_array_file(self, array_file):
        assert ndjson_array_field_count(array_file) == 2

    def test_zero_for_no_array_file(self, no_array_file):
        assert ndjson_array_field_count(no_array_file) == 0

    def test_nonnegative(self, array_file):
        assert ndjson_array_field_count(array_file) >= 0

    def test_consistent_across_calls(self, array_file):
        assert ndjson_array_field_count(array_file) == ndjson_array_field_count(array_file)

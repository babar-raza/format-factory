"""Tests for NDJSON gap closure (Sprint 40).

Closes:
  GAP-NDJSON-FOSS-NDJSON_AVG_N-001   (Ndjson Avg Numeric Value)
  GAP-NDJSON-FOSS-NDJSON_MIN_R-001   (Ndjson Min Record Size)
  GAP-NDJSON-FOSS-NDJSON_HAS_L-001   (Ndjson Has Lists)
  GAP-NDJSON-FOSS-NDJSON_SCHEM-001   (Ndjson Schema Consistency)
  GAP-NDJSON-FOSS-NDJSON_TOTAL-001   (Ndjson Total Numeric Sum)
  GAP-NDJSON-FOSS-NDJSON_IS_SI-001   (Ndjson Is Single Record)
  GAP-NDJSON-FOSS-NDJSON_STRIN-001   (Ndjson String Density)
  GAP-NDJSON-FOSS-NDJSON_AVG_L-001   (Ndjson Avg List Length)
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import (
    ndjson_avg_list_length,
    ndjson_avg_numeric_value,
    ndjson_has_lists,
    ndjson_is_single_record,
    ndjson_min_record_size,
    ndjson_schema_consistency,
    ndjson_string_density,
    ndjson_total_numeric_sum,
)


@pytest.fixture
def nums_file(tmp_path):
    """3-record file: [{name, age}, {name, age}, {name, age}]"""
    path = tmp_path / "nums.ndjson"
    records = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Carol", "age": 35},
    ]
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return str(path)


@pytest.fixture
def lists_file(tmp_path):
    """2-record file with list fields"""
    path = tmp_path / "lists.ndjson"
    records = [
        {"items": [1, 2, 3], "val": 10},
        {"items": [4, 5], "val": 20},
    ]
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return str(path)


@pytest.fixture
def single_file(tmp_path):
    """1-record file"""
    path = tmp_path / "single.ndjson"
    path.write_text(json.dumps({"x": 1}) + "\n")
    return str(path)


class TestNdjsonAvgNumericValue:
    def test_return_type(self, nums_file):
        assert isinstance(ndjson_avg_numeric_value(nums_file), float)

    def test_exact_30_0_for_3_record_file(self, nums_file):
        # ages: 30, 25, 35 -> avg = 30.0
        assert ndjson_avg_numeric_value(nums_file) == 30.0

    def test_nonnegative(self, nums_file):
        assert ndjson_avg_numeric_value(nums_file) >= 0.0

    def test_consistent_across_calls(self, nums_file):
        assert ndjson_avg_numeric_value(nums_file) == ndjson_avg_numeric_value(nums_file)


class TestNdjsonMinRecordSize:
    def test_return_type(self, nums_file):
        assert isinstance(ndjson_min_record_size(nums_file), int)

    def test_exact_26_for_3_record_file(self, nums_file):
        # smallest record JSON length
        assert ndjson_min_record_size(nums_file) == 26

    def test_positive(self, nums_file):
        assert ndjson_min_record_size(nums_file) >= 1

    def test_consistent_across_calls(self, nums_file):
        assert ndjson_min_record_size(nums_file) == ndjson_min_record_size(nums_file)


class TestNdjsonHasLists:
    def test_return_type(self, nums_file):
        assert isinstance(ndjson_has_lists(nums_file), bool)

    def test_false_for_no_list_fields(self, nums_file):
        assert ndjson_has_lists(nums_file) is False

    def test_true_for_list_fields(self, lists_file):
        assert ndjson_has_lists(lists_file) is True

    def test_consistent_across_calls(self, nums_file):
        assert ndjson_has_lists(nums_file) == ndjson_has_lists(nums_file)


class TestNdjsonSchemaConsistency:
    def test_return_type(self, nums_file):
        assert isinstance(ndjson_schema_consistency(nums_file), float)

    def test_exact_1_0_for_homogeneous(self, nums_file):
        # all records have same keys -> 1.0
        assert ndjson_schema_consistency(nums_file) == 1.0

    def test_between_0_and_1(self, nums_file):
        v = ndjson_schema_consistency(nums_file)
        assert 0.0 <= v <= 1.0

    def test_consistent_across_calls(self, nums_file):
        assert ndjson_schema_consistency(nums_file) == ndjson_schema_consistency(nums_file)


class TestNdjsonTotalNumericSum:
    def test_return_type(self, nums_file):
        assert isinstance(ndjson_total_numeric_sum(nums_file), float)

    def test_exact_90_0_for_3_record_file(self, nums_file):
        # 30 + 25 + 35 = 90
        assert ndjson_total_numeric_sum(nums_file) == 90.0

    def test_nonnegative(self, nums_file):
        assert ndjson_total_numeric_sum(nums_file) >= 0.0

    def test_consistent_across_calls(self, nums_file):
        assert ndjson_total_numeric_sum(nums_file) == ndjson_total_numeric_sum(nums_file)


class TestNdjsonIsSingleRecord:
    def test_return_type(self, single_file):
        assert isinstance(ndjson_is_single_record(single_file), bool)

    def test_true_for_single_record(self, single_file):
        assert ndjson_is_single_record(single_file) is True

    def test_false_for_multi_record(self, nums_file):
        assert ndjson_is_single_record(nums_file) is False

    def test_consistent_across_calls(self, single_file):
        assert ndjson_is_single_record(single_file) == ndjson_is_single_record(single_file)


class TestNdjsonStringDensity:
    def test_return_type(self, nums_file):
        assert isinstance(ndjson_string_density(nums_file), float)

    def test_exact_0_5_for_3_record_file(self, nums_file):
        # each record: 1 string field, 1 numeric field -> 0.5
        assert ndjson_string_density(nums_file) == 0.5

    def test_between_0_and_1(self, nums_file):
        v = ndjson_string_density(nums_file)
        assert 0.0 <= v <= 1.0

    def test_consistent_across_calls(self, nums_file):
        assert ndjson_string_density(nums_file) == ndjson_string_density(nums_file)


class TestNdjsonAvgListLength:
    def test_return_type(self, nums_file):
        assert isinstance(ndjson_avg_list_length(nums_file), float)

    def test_zero_for_no_list_fields(self, nums_file):
        assert ndjson_avg_list_length(nums_file) == 0.0

    def test_exact_2_5_for_list_fields(self, lists_file):
        # [1,2,3] length 3, [4,5] length 2 -> avg 2.5
        assert ndjson_avg_list_length(lists_file) == 2.5

    def test_nonnegative(self, nums_file):
        assert ndjson_avg_list_length(nums_file) >= 0.0

    def test_consistent_across_calls(self, lists_file):
        assert ndjson_avg_list_length(lists_file) == ndjson_avg_list_length(lists_file)

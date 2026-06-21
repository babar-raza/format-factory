"""Tests for NDJSON Sprint 56 gap closure.

Closes:
  GAP-NDJSON-FOSS-NDJSON_NULL_-001   (Ndjson Null Ratio)
  GAP-NDJSON-FOSS-NDJSON_OBJEC-001   (Ndjson Object Field Variance)
"""
import sys
import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_null_ratio, ndjson_object_field_variance


class TestNdjsonNullRatio:
    def test_return_type(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text(json.dumps({"a": None, "b": 1}) + "\n")
        assert isinstance(ndjson_null_ratio(str(f)), (int, float))

    def test_exact_0_5_for_half_null(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text(
            json.dumps({"a": None, "b": 1, "c": None}) + "\n"
            + json.dumps({"a": 1, "b": None, "c": 3}) + "\n"
        )
        assert ndjson_null_ratio(str(f)) == 0.5

    def test_zero_for_no_nulls(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text(json.dumps({"a": 1, "b": 2}) + "\n")
        assert ndjson_null_ratio(str(f)) == 0.0

    def test_in_range_0_to_1(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text(json.dumps({"x": None}) + "\n")
        assert 0.0 <= ndjson_null_ratio(str(f)) <= 1.0

    def test_consistent_across_calls(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text(json.dumps({"a": 1}) + "\n")
        assert ndjson_null_ratio(str(f)) == ndjson_null_ratio(str(f))


class TestNdjsonObjectFieldVariance:
    def test_return_type(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text(json.dumps({"a": 1, "b": 2}) + "\n")
        assert isinstance(ndjson_object_field_variance(str(f)), (int, float))

    def test_zero_for_uniform_fields(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text(
            json.dumps({"a": None, "b": 1, "c": None}) + "\n"
            + json.dumps({"a": 1, "b": None, "c": 3}) + "\n"
        )
        assert ndjson_object_field_variance(str(f)) == 0.0

    def test_nonzero_for_varying_fields(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text(
            json.dumps({"a": 1}) + "\n"
            + json.dumps({"a": 2, "b": 3}) + "\n"
        )
        assert ndjson_object_field_variance(str(f)) == 0.25

    def test_nonnegative(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text(json.dumps({"a": 1}) + "\n")
        assert ndjson_object_field_variance(str(f)) >= 0

    def test_consistent_across_calls(self, tmp_path):
        f = tmp_path / "data.jsonl"
        f.write_text(json.dumps({"a": 1, "b": 2}) + "\n")
        assert ndjson_object_field_variance(str(f)) == ndjson_object_field_variance(str(f))

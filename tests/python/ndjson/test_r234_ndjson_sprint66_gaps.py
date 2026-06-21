"""Tests for NDJSON Sprint 66 gap closure.

Closes:
  GAP-NDJSON-FOSS-NDJSON_VALUE-001   (Ndjson Value Variance)
  GAP-NDJSON-FOSS-NDJSON_FILE_-001   (Ndjson File Size Bytes)
  GAP-NDJSON-FOSS-NDJSON_KEY_C-001   (Ndjson Key Count Variance)
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_value_variance, ndjson_file_size_bytes, ndjson_key_count_variance


class TestNdjsonValueVariance:
    def test_return_type(self, tmp_path):
        f = tmp_path / "v.ndjson"
        f.write_text(json.dumps({"a": 1}) + "\n" + json.dumps({"a": 3}) + "\n")
        assert isinstance(ndjson_value_variance(str(f)), (int, float))

    def test_exact_1_25_for_uniform(self, tmp_path):
        f = tmp_path / "u.ndjson"
        f.write_text(
            json.dumps({"a": 1, "b": 2}) + "\n" + json.dumps({"a": 3, "b": 4}) + "\n"
        )
        assert ndjson_value_variance(str(f)) == pytest.approx(1.25)

    def test_zero_for_single(self, tmp_path):
        f = tmp_path / "s.ndjson"
        f.write_text(json.dumps({"x": 100}) + "\n")
        assert ndjson_value_variance(str(f)) == 0.0

    def test_nonnegative(self, tmp_path):
        f = tmp_path / "n.ndjson"
        f.write_text(json.dumps({"a": 1}) + "\n")
        assert ndjson_value_variance(str(f)) >= 0.0

    def test_consistent_across_calls(self, tmp_path):
        f = tmp_path / "c.ndjson"
        f.write_text(json.dumps({"a": 1, "b": 2}) + "\n")
        assert ndjson_value_variance(str(f)) == ndjson_value_variance(str(f))


class TestNdjsonFileSizeBytes:
    def test_return_type(self, tmp_path):
        f = tmp_path / "s.ndjson"
        f.write_text(json.dumps({"a": 1}) + "\n")
        assert isinstance(ndjson_file_size_bytes(str(f)), int)

    def test_exact_for_uniform(self, tmp_path):
        f = tmp_path / "u.ndjson"
        content = (json.dumps({"a": 1, "b": 2}) + "\n" + json.dumps({"a": 3, "b": 4}) + "\n").encode()
        f.write_bytes(content)
        assert ndjson_file_size_bytes(str(f)) == len(content)

    def test_exact_for_single(self, tmp_path):
        f = tmp_path / "s.ndjson"
        content = (json.dumps({"x": 100}) + "\n").encode()
        f.write_bytes(content)
        assert ndjson_file_size_bytes(str(f)) == len(content)

    def test_positive(self, tmp_path):
        f = tmp_path / "p.ndjson"
        f.write_text(json.dumps({"a": 1}) + "\n")
        assert ndjson_file_size_bytes(str(f)) > 0

    def test_consistent_across_calls(self, tmp_path):
        f = tmp_path / "c.ndjson"
        f.write_text(json.dumps({"a": 1}) + "\n")
        assert ndjson_file_size_bytes(str(f)) == ndjson_file_size_bytes(str(f))


class TestNdjsonKeyCountVariance:
    def test_return_type(self, tmp_path):
        f = tmp_path / "k.ndjson"
        f.write_text(json.dumps({"a": 1}) + "\n")
        assert isinstance(ndjson_key_count_variance(str(f)), (int, float))

    def test_zero_for_uniform_key_count(self, tmp_path):
        f = tmp_path / "u.ndjson"
        f.write_text(
            json.dumps({"a": 1, "b": 2}) + "\n" + json.dumps({"c": 3, "d": 4}) + "\n"
        )
        assert ndjson_key_count_variance(str(f)) == 0.0

    def test_exact_0_25_for_mixed_key_count(self, tmp_path):
        f = tmp_path / "m.ndjson"
        f.write_text(
            json.dumps({"a": 1}) + "\n" + json.dumps({"b": "hello", "c": True}) + "\n"
        )
        assert ndjson_key_count_variance(str(f)) == pytest.approx(0.25)

    def test_nonnegative(self, tmp_path):
        f = tmp_path / "n.ndjson"
        f.write_text(json.dumps({"a": 1}) + "\n")
        assert ndjson_key_count_variance(str(f)) >= 0.0

    def test_consistent_across_calls(self, tmp_path):
        f = tmp_path / "c.ndjson"
        f.write_text(json.dumps({"a": 1, "b": 2}) + "\n")
        assert ndjson_key_count_variance(str(f)) == ndjson_key_count_variance(str(f))

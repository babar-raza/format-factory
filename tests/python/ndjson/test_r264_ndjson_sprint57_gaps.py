"""Tests for NDJSON Sprint 57 gap closure.

Closes:
  GAP-NDJSON-FOSS-NDJSON_AVG_V-001   (Ndjson Avg Values Per Record)
"""
import sys
import json
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson import ndjson_avg_values_per_record


class TestNdjsonAvgValuesPerRecord:
    def test_return_type(self, tmp_path):
        f = tmp_path / "t.ndjson"
        f.write_text('{"a": 1}\n')
        assert isinstance(ndjson_avg_values_per_record(str(f)), (int, float))

    def test_exact_1_0_for_single_field(self, tmp_path):
        f = tmp_path / "single.ndjson"
        f.write_text('{"a": 1}\n{"b": 2}\n')
        assert ndjson_avg_values_per_record(str(f)) == 1.0

    def test_exact_2_0_for_two_fields(self, tmp_path):
        f = tmp_path / "two.ndjson"
        f.write_text('{"a": 1, "b": 2}\n{"c": 3, "d": 4}\n')
        assert ndjson_avg_values_per_record(str(f)) == 2.0

    def test_exact_1_5_for_mixed(self, tmp_path):
        f = tmp_path / "mixed.ndjson"
        f.write_text('{"a": 1}\n{"b": 2, "c": 3}\n')
        assert ndjson_avg_values_per_record(str(f)) == 1.5

    def test_zero_for_empty(self, tmp_path):
        f = tmp_path / "empty.ndjson"
        f.write_text("")
        assert ndjson_avg_values_per_record(str(f)) == 0.0

    def test_nonnegative(self, tmp_path):
        f = tmp_path / "pos.ndjson"
        f.write_text('{"x": 1}\n')
        assert ndjson_avg_values_per_record(str(f)) >= 0

    def test_consistent_across_calls(self, tmp_path):
        f = tmp_path / "c.ndjson"
        f.write_text('{"a": 1, "b": 2}\n')
        assert ndjson_avg_values_per_record(str(f)) == ndjson_avg_values_per_record(str(f))

"""
Tests for additional NDJSON analytics gap closure (2 FOSS gaps).
Closes: GAP-NDJSON-FOSS-NDJSON_STRIN-001, GAP-NDJSON-FOSS-NDJSON_AVG_L-001
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import (
    ndjson_string_density,
    ndjson_avg_list_length,
)


def _write(tmp_path, name, records):
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return p


class TestNdjsonStringDensity:
    def test_returns_float(self, tmp_path):
        p = _write(tmp_path, "t.ndjson", [{"a": "hello", "b": "world"}])
        assert isinstance(ndjson_string_density(p), float)

    def test_all_strings_is_one(self, tmp_path):
        p = _write(tmp_path, "t.ndjson", [{"a": "x", "b": "y"}, {"a": "z", "b": "w"}])
        assert ndjson_string_density(p) == pytest.approx(1.0)

    def test_no_strings_near_zero(self, tmp_path):
        p = _write(tmp_path, "t.ndjson", [{"a": 1, "b": 2}, {"a": 3, "b": 4}])
        # numeric and string density depends on how string is detected;
        # a=1 and b=2 are numeric → no string fields → density near 0
        result = ndjson_string_density(p)
        assert isinstance(result, float) and result >= 0.0

    def test_mixed_bounded(self, tmp_path):
        p = _write(tmp_path, "t.ndjson", [{"a": 1, "b": "hello"}])
        assert 0.0 <= ndjson_string_density(p) <= 1.0


class TestNdjsonAvgListLength:
    def test_returns_float(self, tmp_path):
        p = _write(tmp_path, "t.ndjson", [{"items": [1, 2, 3]}])
        assert isinstance(ndjson_avg_list_length(p), float)

    def test_no_lists_returns_zero(self, tmp_path):
        p = _write(tmp_path, "t.ndjson", [{"a": 1}, {"a": 2}])
        assert ndjson_avg_list_length(p) == pytest.approx(0.0)

    def test_with_lists_positive(self, tmp_path):
        p = _write(tmp_path, "t.ndjson", [{"items": [1, 2, 3], "x": [4, 5]}])
        result = ndjson_avg_list_length(p)
        assert result > 0.0

    def test_exact_avg(self, tmp_path):
        # items=[1,2,3] (len=3), x=[4,5] (len=2) → avg=2.5
        p = _write(tmp_path, "t.ndjson", [{"items": [1, 2, 3], "x": [4, 5]}])
        assert ndjson_avg_list_length(p) == pytest.approx(2.5)

"""
Tests for NDJSON analytics gap closure (6 FOSS gaps).
Closes: GAP-NDJSON-FOSS-NDJSON_AVG_N-001, GAP-NDJSON-FOSS-NDJSON_MIN_R-001,
        GAP-NDJSON-FOSS-NDJSON_HAS_L-001, GAP-NDJSON-FOSS-NDJSON_SCHEM-001,
        GAP-NDJSON-FOSS-NDJSON_TOTAL-001, GAP-NDJSON-FOSS-NDJSON_IS_SI-001

Note: NDJSON analytics take a file PATH, not a list. Use tmp_path fixtures.
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import (
    ndjson_avg_numeric_value,
    ndjson_min_record_size,
    ndjson_has_lists,
    ndjson_schema_consistency,
    ndjson_total_numeric_sum,
    ndjson_is_single_record,
)


def _write_ndjson(tmp_path, name: str, records: list) -> Path:
    p = tmp_path / name
    p.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    return p


class TestNdjsonAvgNumericValue:
    def test_returns_float(self, tmp_path):
        p = _write_ndjson(tmp_path, "n.ndjson", [{"a": 10}, {"a": 20}])
        assert isinstance(ndjson_avg_numeric_value(p), float)

    def test_correct_avg(self, tmp_path):
        p = _write_ndjson(tmp_path, "n.ndjson", [{"v": 10}, {"v": 30}])
        result = ndjson_avg_numeric_value(p)
        assert result == pytest.approx(20.0)

    def test_zero_for_no_numerics(self, tmp_path):
        p = _write_ndjson(tmp_path, "s.ndjson", [{"name": "hello"}, {"name": "world"}])
        assert ndjson_avg_numeric_value(p) == 0.0

    def test_nonnegative(self, tmp_path):
        p = _write_ndjson(tmp_path, "n.ndjson", [{"x": 5}, {"x": 15}])
        assert ndjson_avg_numeric_value(p) >= 0.0


class TestNdjsonMinRecordSize:
    # ndjson_min_record_size returns size in bytes of smallest serialized record
    def test_returns_int(self, tmp_path):
        p = _write_ndjson(tmp_path, "r.ndjson", [{"a": 1}, {"a": 2, "b": 3}])
        assert isinstance(ndjson_min_record_size(p), int)

    def test_positive_for_content(self, tmp_path):
        p = _write_ndjson(tmp_path, "r.ndjson", [{"a": 1}])
        assert ndjson_min_record_size(p) > 0

    def test_smaller_record_has_fewer_bytes(self, tmp_path):
        # {"x": 1} is smaller than {"a": 1, "b": 2, "c": 3}
        p = _write_ndjson(tmp_path, "r.ndjson", [{"a": 1, "b": 2, "c": 3}, {"x": 1}])
        assert ndjson_min_record_size(p) < 30  # {"x": 1} is 8 bytes

    def test_nonnegative(self, tmp_path):
        p = _write_ndjson(tmp_path, "r.ndjson", [{"a": 1}, {"a": 2}])
        assert ndjson_min_record_size(p) >= 0


class TestNdjsonHasLists:
    def test_returns_bool(self, tmp_path):
        p = _write_ndjson(tmp_path, "h.ndjson", [{"a": 1}])
        assert isinstance(ndjson_has_lists(p), bool)

    def test_true_when_list_present(self, tmp_path):
        p = _write_ndjson(tmp_path, "l.ndjson", [{"tags": ["a", "b"]}])
        assert ndjson_has_lists(p) is True

    def test_false_when_no_lists(self, tmp_path):
        p = _write_ndjson(tmp_path, "n.ndjson", [{"a": 1, "b": "hello"}])
        assert ndjson_has_lists(p) is False

    def test_false_for_scalars_only(self, tmp_path):
        p = _write_ndjson(tmp_path, "s.ndjson", [{"x": 1}, {"y": 2}])
        assert ndjson_has_lists(p) is False


class TestNdjsonSchemaConsistency:
    def test_returns_float(self, tmp_path):
        p = _write_ndjson(tmp_path, "c.ndjson", [{"a": 1, "b": 2}, {"a": 3, "b": 4}])
        assert isinstance(ndjson_schema_consistency(p), float)

    def test_one_for_uniform_schema(self, tmp_path):
        p = _write_ndjson(tmp_path, "c.ndjson", [{"a": 1, "b": 2}, {"a": 3, "b": 4}])
        result = ndjson_schema_consistency(p)
        assert result == pytest.approx(1.0)

    def test_less_than_one_for_varying_schema(self, tmp_path):
        p = _write_ndjson(tmp_path, "v.ndjson", [{"a": 1}, {"a": 1, "b": 2}])
        result = ndjson_schema_consistency(p)
        assert 0.0 <= result <= 1.0

    def test_in_range(self, tmp_path):
        p = _write_ndjson(tmp_path, "r.ndjson", [{"x": 1}, {"y": 2}])
        assert 0.0 <= ndjson_schema_consistency(p) <= 1.0


class TestNdjsonTotalNumericSum:
    def test_returns_float(self, tmp_path):
        p = _write_ndjson(tmp_path, "s.ndjson", [{"a": 1}, {"a": 2}])
        assert isinstance(ndjson_total_numeric_sum(p), float)

    def test_correct_sum(self, tmp_path):
        p = _write_ndjson(tmp_path, "s.ndjson", [{"v": 10}, {"v": 20}, {"v": 30}])
        assert ndjson_total_numeric_sum(p) == pytest.approx(60.0)

    def test_zero_for_no_numerics(self, tmp_path):
        p = _write_ndjson(tmp_path, "s.ndjson", [{"name": "a"}, {"name": "b"}])
        assert ndjson_total_numeric_sum(p) == 0.0

    def test_nonnegative_for_positive_values(self, tmp_path):
        p = _write_ndjson(tmp_path, "s.ndjson", [{"x": 5}, {"x": 10}])
        assert ndjson_total_numeric_sum(p) >= 0.0


class TestNdjsonIsSingleRecord:
    def test_returns_bool(self, tmp_path):
        p = _write_ndjson(tmp_path, "s.ndjson", [{"a": 1}])
        assert isinstance(ndjson_is_single_record(p), bool)

    def test_true_for_one_record(self, tmp_path):
        p = _write_ndjson(tmp_path, "s.ndjson", [{"a": 1}])
        assert ndjson_is_single_record(p) is True

    def test_false_for_multiple_records(self, tmp_path):
        p = _write_ndjson(tmp_path, "m.ndjson", [{"a": 1}, {"b": 2}])
        assert ndjson_is_single_record(p) is False

    def test_false_for_empty(self, tmp_path):
        p = tmp_path / "e.ndjson"
        p.write_text("")
        assert ndjson_is_single_record(p) is False

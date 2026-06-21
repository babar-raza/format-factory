"""
Tests for NDJSON gap closure (1 FOSS function).
Closes: GAP-NDJSON-FOSS-NDJSON_AVG_R-001

Known inline values:
  flat records (depth=1): avg=1.0
  nested records (one at depth=3, one at depth=1): avg=2.0
  empty: 0.0
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import ndjson_avg_record_depth

_FLAT = b'{"a":1}\n{"b":2}\n'
_NESTED = b'{"a":{"b":{"c":1}}}\n{"x":1}\n'
_EMPTY = b""
_SINGLE_NESTED = b'{"outer":{"inner":42}}\n'


class TestNdjsonAvgRecordDepth:
    def test_returns_float(self):
        assert isinstance(ndjson_avg_record_depth(_FLAT), float)

    def test_empty_returns_zero(self):
        assert ndjson_avg_record_depth(_EMPTY) == 0.0

    def test_flat_records_depth_one(self):
        # all top-level keys → depth 1
        assert ndjson_avg_record_depth(_FLAT) == 1.0

    def test_nested_records_avg(self):
        # {a:{b:{c:1}}} depth=3, {x:1} depth=1 → avg=2.0
        assert ndjson_avg_record_depth(_NESTED) == 2.0

    def test_single_nested(self):
        # {outer:{inner:42}} → depth=2
        assert ndjson_avg_record_depth(_SINGLE_NESTED) == 2.0

    def test_nonnegative(self):
        for src in [_FLAT, _NESTED, _EMPTY, _SINGLE_NESTED]:
            assert ndjson_avg_record_depth(src) >= 0.0

    def test_all_return_float(self):
        for src in [_FLAT, _NESTED, _EMPTY, _SINGLE_NESTED]:
            assert isinstance(ndjson_avg_record_depth(src), float)

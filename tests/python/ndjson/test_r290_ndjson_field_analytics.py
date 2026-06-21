"""
Tests for NDJSON additional field analytics (2 new FOSS functions).
Closes: GAP-NDJSON-FOSS-NDJSON_AVG-001, GAP-NDJSON-FOSS-NDJSON_STR-001

No sample files exist for NDJSON — tests use inline bytes.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import ndjson_avg_field_count, ndjson_string_field_count

_EMPTY = b""
_ONE_REC = b'{"a": 1, "b": "x"}\n'
_TWO_RECS = b'{"a": 1}\n{"b": 2, "c": 3}\n'
_STR_RECS = b'{"name": "Alice", "age": 30}\n{"name": "Bob", "city": "NY"}\n'


class TestNdjsonAvgFieldCount:
    def test_returns_float(self):
        assert isinstance(ndjson_avg_field_count(_EMPTY), float)

    def test_empty_is_zero(self):
        assert ndjson_avg_field_count(_EMPTY) == 0.0

    def test_one_record_two_fields(self):
        assert ndjson_avg_field_count(_ONE_REC) == 2.0

    def test_two_records_avg(self):
        # record 1 has 1 field, record 2 has 2 fields → avg=1.5
        assert ndjson_avg_field_count(_TWO_RECS) == 1.5

    def test_uniform_two_fields(self):
        # both records have 2 fields → avg=2.0
        assert ndjson_avg_field_count(_STR_RECS) == 2.0

    def test_nonnegative(self):
        for src in [_EMPTY, _ONE_REC, _TWO_RECS, _STR_RECS]:
            assert ndjson_avg_field_count(src) >= 0.0

    def test_empty_less_than_nonempty(self):
        assert ndjson_avg_field_count(_EMPTY) < ndjson_avg_field_count(_ONE_REC)

    def test_all_return_float(self):
        for src in [_EMPTY, _ONE_REC, _TWO_RECS]:
            assert isinstance(ndjson_avg_field_count(src), float)


class TestNdjsonStringFieldCount:
    def test_returns_int(self):
        assert isinstance(ndjson_string_field_count(_EMPTY), int)

    def test_empty_is_zero(self):
        assert ndjson_string_field_count(_EMPTY) == 0

    def test_one_string_field(self):
        # {"a": 1, "b": "x"} → "x" is a string → 1
        assert ndjson_string_field_count(_ONE_REC) == 1

    def test_no_string_fields(self):
        # {"a": 1} + {"b": 2, "c": 3} → no strings → 0
        assert ndjson_string_field_count(_TWO_RECS) == 0

    def test_multiple_string_fields(self):
        # {"name": "Alice", "age": 30} + {"name": "Bob", "city": "NY"} → Alice, Bob, NY → 3
        assert ndjson_string_field_count(_STR_RECS) == 3

    def test_nonnegative(self):
        for src in [_EMPTY, _ONE_REC, _TWO_RECS, _STR_RECS]:
            assert ndjson_string_field_count(src) >= 0

    def test_all_return_int(self):
        for src in [_EMPTY, _ONE_REC, _TWO_RECS]:
            assert isinstance(ndjson_string_field_count(src), int)

"""
tests/python/ndjson/test_r291_ndjson_iter_records.py

Sprint: ff-sprint-s291-ndjson-record-iterator-20260626
Authority: NDJSON specification (ndjson.org)

Tests for ndjson_iter_records() in ndjson_record_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_SAMPLE = _REPO / "samples" / "by-format" / "ndjson" / "valid" / "minimal.ndjson"


class TestNdjsonIterRecordsImport:
    def test_importable_from_ndjson_record_iterator(self):
        from ndjson.ndjson_record_iterator import ndjson_iter_records
        assert callable(ndjson_iter_records)

    def test_importable_from_package(self):
        import ndjson
        assert hasattr(ndjson, "ndjson_iter_records")


class TestNdjsonIterRecordsOutput:
    def test_returns_iterator(self):
        from ndjson.ndjson_record_iterator import ndjson_iter_records
        result = ndjson_iter_records(str(_SAMPLE))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_records(self):
        from ndjson.ndjson_record_iterator import ndjson_iter_records
        records = list(ndjson_iter_records(str(_SAMPLE)))
        assert len(records) >= 1

    def test_record_type_is_spec_record(self):
        from ndjson.ndjson_record_iterator import ndjson_iter_records
        from ndjson.spec.record.record import Record
        records = list(ndjson_iter_records(str(_SAMPLE)))
        assert all(isinstance(r, Record) for r in records)

    def test_record_has_spec_qname(self):
        from ndjson.ndjson_record_iterator import ndjson_iter_records
        records = list(ndjson_iter_records(str(_SAMPLE)))
        assert all(hasattr(r, "spec_qname") for r in records)

    def test_record_qname_value(self):
        from ndjson.ndjson_record_iterator import ndjson_iter_records
        records = list(ndjson_iter_records(str(_SAMPLE)))
        assert all(r.spec_qname == "ndjson:record" for r in records)

    def test_record_has_keys(self):
        from ndjson.ndjson_record_iterator import ndjson_iter_records
        records = list(ndjson_iter_records(str(_SAMPLE)))
        for r in records:
            assert isinstance(r.keys, list)

    def test_record_has_field_count(self):
        from ndjson.ndjson_record_iterator import ndjson_iter_records
        records = list(ndjson_iter_records(str(_SAMPLE)))
        for r in records:
            assert isinstance(r.field_count, int) and r.field_count >= 0

    def test_consistent(self):
        from ndjson.ndjson_record_iterator import ndjson_iter_records
        r1 = list(ndjson_iter_records(str(_SAMPLE)))
        r2 = list(ndjson_iter_records(str(_SAMPLE)))
        assert len(r1) == len(r2)

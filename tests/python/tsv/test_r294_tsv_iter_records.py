"""
tests/python/tsv/test_r294_tsv_iter_records.py

Sprint: ff-sprint-s294-tsv-row-iterator-20260626
Authority: IANA text/tab-separated-values media type

Tests for tsv_iter_records() in tsv_row_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_MINIMAL = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"
_SINGLE = _REPO / "samples" / "by-format" / "tsv" / "single-cell.tsv"


class TestTsvIterRecordsImport:
    def test_importable_from_tsv_row_iterator(self):
        from tsv.tsv_row_iterator import tsv_iter_records
        assert callable(tsv_iter_records)

    def test_importable_from_package(self):
        import tsv
        assert hasattr(tsv, "tsv_iter_records")


class TestTsvIterRecordsOutput:
    def test_returns_iterator(self):
        from tsv.tsv_row_iterator import tsv_iter_records
        result = tsv_iter_records(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_records(self):
        from tsv.tsv_row_iterator import tsv_iter_records
        records = list(tsv_iter_records(str(_MINIMAL)))
        assert len(records) >= 1

    def test_record_type_is_spec_record(self):
        from tsv.tsv_row_iterator import tsv_iter_records
        from tsv.spec.record.record import Record
        records = list(tsv_iter_records(str(_MINIMAL)))
        assert all(isinstance(r, Record) for r in records)

    def test_record_has_spec_qname(self):
        from tsv.tsv_row_iterator import tsv_iter_records
        records = list(tsv_iter_records(str(_MINIMAL)))
        assert all(hasattr(r, "spec_qname") for r in records)

    def test_record_qname_value(self):
        from tsv.tsv_row_iterator import tsv_iter_records
        records = list(tsv_iter_records(str(_MINIMAL)))
        assert all(r.spec_qname == "tsv:record" for r in records)

    def test_record_has_fields(self):
        from tsv.tsv_row_iterator import tsv_iter_records
        records = list(tsv_iter_records(str(_MINIMAL)))
        for r in records:
            assert isinstance(r.fields, list)

    def test_record_field_count(self):
        from tsv.tsv_row_iterator import tsv_iter_records
        records = list(tsv_iter_records(str(_MINIMAL)))
        for r in records:
            assert r.field_count >= 1

    def test_consistent(self):
        from tsv.tsv_row_iterator import tsv_iter_records
        r1 = list(tsv_iter_records(str(_MINIMAL)))
        r2 = list(tsv_iter_records(str(_MINIMAL)))
        assert len(r1) == len(r2)

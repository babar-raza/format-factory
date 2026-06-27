"""
tests/python/tsv/test_r313_tsv_iter_fields.py

Sprint: ff-sprint-s313-tsv-field-iterator-20260626
Authority: IANA text/tab-separated-values — field value

Tests for tsv_iter_fields() in tsv_field_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_MINIMAL = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"
_SINGLE = _REPO / "samples" / "by-format" / "tsv" / "single-cell.tsv"


class TestTsvIterFieldsImport:
    def test_importable_from_tsv_field_iterator(self):
        from tsv.tsv_field_iterator import tsv_iter_fields
        assert callable(tsv_iter_fields)

    def test_importable_from_package(self):
        import tsv
        assert hasattr(tsv, "tsv_iter_fields")


class TestTsvIterFieldsOutput:
    def test_returns_iterator(self):
        from tsv.tsv_field_iterator import tsv_iter_fields
        result = tsv_iter_fields(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_fields(self):
        from tsv.tsv_field_iterator import tsv_iter_fields
        fields = list(tsv_iter_fields(str(_MINIMAL)))
        assert len(fields) >= 1

    def test_field_type_is_spec_field(self):
        from tsv.tsv_field_iterator import tsv_iter_fields
        from tsv.spec.record.field import Field
        fields = list(tsv_iter_fields(str(_MINIMAL)))
        assert all(isinstance(f, Field) for f in fields)

    def test_field_has_spec_qname(self):
        from tsv.tsv_field_iterator import tsv_iter_fields
        fields = list(tsv_iter_fields(str(_MINIMAL)))
        assert all(hasattr(f, "spec_qname") for f in fields)

    def test_field_qname_value(self):
        from tsv.tsv_field_iterator import tsv_iter_fields
        fields = list(tsv_iter_fields(str(_MINIMAL)))
        assert all(f.spec_qname == "tsv:field" for f in fields)

    def test_field_has_value(self):
        from tsv.tsv_field_iterator import tsv_iter_fields
        fields = list(tsv_iter_fields(str(_MINIMAL)))
        for f in fields:
            assert isinstance(f.value, str)

    def test_minimal_field_count(self):
        from tsv.tsv_field_iterator import tsv_iter_fields
        # 2 headers + 2 rows * 2 cols = 6 total fields
        fields = list(tsv_iter_fields(str(_MINIMAL)))
        assert len(fields) == 6

    def test_consistent(self):
        from tsv.tsv_field_iterator import tsv_iter_fields
        r1 = [f.value for f in tsv_iter_fields(str(_MINIMAL))]
        r2 = [f.value for f in tsv_iter_fields(str(_MINIMAL))]
        assert r1 == r2

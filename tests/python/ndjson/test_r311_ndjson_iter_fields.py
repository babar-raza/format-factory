"""
tests/python/ndjson/test_r311_ndjson_iter_fields.py

Sprint: ff-sprint-s311-ndjson-field-iterator-20260626
Authority: NDJSON — key-value field within a record

Tests for ndjson_iter_fields() in ndjson_field_iterator.py.
"""
from __future__ import annotations

from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_MINIMAL = _REPO / "samples" / "by-format" / "ndjson" / "valid" / "minimal.ndjson"


class TestNdjsonIterFieldsImport:
    def test_importable_from_ndjson_field_iterator(self):
        from ndjson.ndjson_field_iterator import ndjson_iter_fields
        assert callable(ndjson_iter_fields)

    def test_importable_from_package(self):
        import ndjson
        assert hasattr(ndjson, "ndjson_iter_fields")


class TestNdjsonIterFieldsOutput:
    def test_returns_iterator(self):
        from ndjson.ndjson_field_iterator import ndjson_iter_fields
        result = ndjson_iter_fields(str(_MINIMAL))
        assert hasattr(result, "__iter__") and hasattr(result, "__next__")

    def test_minimal_yields_fields(self):
        from ndjson.ndjson_field_iterator import ndjson_iter_fields
        fields = list(ndjson_iter_fields(str(_MINIMAL)))
        assert len(fields) >= 1

    def test_field_type_is_spec_field(self):
        from ndjson.ndjson_field_iterator import ndjson_iter_fields
        from ndjson.spec.record.field import Field
        fields = list(ndjson_iter_fields(str(_MINIMAL)))
        assert all(isinstance(f, Field) for f in fields)

    def test_field_has_spec_qname(self):
        from ndjson.ndjson_field_iterator import ndjson_iter_fields
        fields = list(ndjson_iter_fields(str(_MINIMAL)))
        assert all(hasattr(f, "spec_qname") for f in fields)

    def test_field_qname_value(self):
        from ndjson.ndjson_field_iterator import ndjson_iter_fields
        fields = list(ndjson_iter_fields(str(_MINIMAL)))
        assert all(f.spec_qname == "ndjson:field" for f in fields)

    def test_field_has_key(self):
        from ndjson.ndjson_field_iterator import ndjson_iter_fields
        fields = list(ndjson_iter_fields(str(_MINIMAL)))
        for f in fields:
            assert isinstance(f.key, str)

    def test_field_has_value(self):
        from ndjson.ndjson_field_iterator import ndjson_iter_fields
        fields = list(ndjson_iter_fields(str(_MINIMAL)))
        for f in fields:
            assert f.value is not None or f.is_null()

    def test_minimal_field_count(self):
        from ndjson.ndjson_field_iterator import ndjson_iter_fields
        # 3 records * 3 fields each = 9 total fields
        fields = list(ndjson_iter_fields(str(_MINIMAL)))
        assert len(fields) == 9

    def test_consistent(self):
        from ndjson.ndjson_field_iterator import ndjson_iter_fields
        r1 = [f.key for f in ndjson_iter_fields(str(_MINIMAL))]
        r2 = [f.key for f in ndjson_iter_fields(str(_MINIMAL))]
        assert r1 == r2

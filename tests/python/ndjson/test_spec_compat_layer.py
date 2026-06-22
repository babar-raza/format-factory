"""Behavioral tests for NDJSON spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.ndjson.Compat import NdjsonRecord, NdjsonField
from src.python.ndjson.spec.record.record import Record as SpecRecord
from src.python.ndjson.spec.record.field import Field as SpecField


_SAMPLE_DATA = {"name": "Alice", "age": 30, "active": True}


class TestNdjsonRecordMetadata:
    def test_spec_qname(self):
        assert NdjsonRecord.spec_qname == "ndjson:record"

    def test_spec_fact_ref(self):
        assert NdjsonRecord.spec_fact_ref == "FACT-NDJSON-001"

    def test_namespace_uri_present(self):
        assert NdjsonRecord.namespace_uri


class TestNdjsonRecordBehavior:
    def test_instantiation(self):
        r = NdjsonRecord(_SAMPLE_DATA)
        assert r is not None

    def test_keys_property(self):
        r = NdjsonRecord(_SAMPLE_DATA)
        assert "name" in r.keys

    def test_field_count(self):
        r = NdjsonRecord(_SAMPLE_DATA)
        assert r.field_count == 3

    def test_to_dict(self):
        r = NdjsonRecord(_SAMPLE_DATA)
        d = r.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        r = NdjsonRecord(_SAMPLE_DATA)
        assert repr(r)

    def test_inherits_spec_class(self):
        r = NdjsonRecord(_SAMPLE_DATA)
        assert isinstance(r, SpecRecord)


class TestNdjsonFieldBehavior:
    def test_instantiation(self):
        f = NdjsonField("name", "Alice")
        assert f is not None

    def test_spec_qname(self):
        assert NdjsonField.spec_qname == "ndjson:field"

    def test_spec_fact_ref(self):
        assert NdjsonField.spec_fact_ref == "FACT-NDJSON-002"

    def test_key_property(self):
        f = NdjsonField("name", "Alice")
        assert f.key == "name"

    def test_value_property(self):
        f = NdjsonField("age", 30)
        assert f.value == 30

    def test_inherits_spec_class(self):
        f = NdjsonField("x", 1)
        assert isinstance(f, SpecField)

    def test_repr_nonempty(self):
        f = NdjsonField("x", 1)
        assert repr(f)

"""Behavioral tests for TSV spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.tsv.Compat import TsvRecord, TsvField
from src.python.tsv.spec.record.record import Record as SpecRecord
from src.python.tsv.spec.record.field import Field as SpecField


class TestTsvRecordMetadata:
    def test_spec_qname(self):
        assert TsvRecord.spec_qname == "tsv:record"

    def test_spec_fact_ref(self):
        assert TsvRecord.spec_fact_ref == "SAL-TSV-00001"

    def test_namespace_uri_present(self):
        assert TsvRecord.namespace_uri


class TestTsvRecordBehavior:
    def test_instantiation(self):
        r = TsvRecord(["a", "b", "c"])
        assert r is not None

    def test_fields_property(self):
        r = TsvRecord(["x", "y"])
        assert r.fields == ["x", "y"]

    def test_field_count(self):
        r = TsvRecord(["a", "b", "c"])
        assert r.field_count == 3

    def test_to_list(self):
        r = TsvRecord(["a", "b"])
        lst = r.to_list()
        assert isinstance(lst, list)
        assert lst == ["a", "b"]

    def test_repr_nonempty(self):
        r = TsvRecord(["a"])
        assert repr(r)

    def test_inherits_spec_class(self):
        r = TsvRecord(["a"])
        assert isinstance(r, SpecRecord)


class TestTsvFieldBehavior:
    def test_instantiation(self):
        f = TsvField("hello")
        assert f is not None

    def test_spec_qname(self):
        assert TsvField.spec_qname == "tsv:field"

    def test_spec_fact_ref(self):
        assert TsvField.spec_fact_ref == "SAL-TSV-00002"

    def test_value_property(self):
        f = TsvField("hello")
        assert f.value == "hello"

    def test_inherits_spec_class(self):
        f = TsvField("x")
        assert isinstance(f, SpecField)

    def test_repr_nonempty(self):
        f = TsvField("x")
        assert repr(f)

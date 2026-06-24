"""Behavioral tests for CSV spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.csv.Compat import CsvRecord, CsvField, CsvHeader
from src.python.csv.spec.record.record import Record as SpecRecord
from src.python.csv.spec.record.field import Field as SpecField
from src.python.csv.spec.record.header import Header as SpecHeader


class TestCsvRecordMetadata:
    def test_spec_qname(self):
        assert CsvRecord.spec_qname == "csv:record"

    def test_spec_fact_ref(self):
        assert CsvRecord.spec_fact_ref == "FACT-CSV-001"

    def test_namespace_uri_present(self):
        assert CsvRecord.namespace_uri


class TestCsvRecordBehavior:
    def test_instantiation(self):
        r = CsvRecord(["a", "b", "c"])
        assert r is not None

    def test_fields_property(self):
        r = CsvRecord(["x", "y"])
        assert r.fields == ["x", "y"]

    def test_field_count(self):
        r = CsvRecord(["a", "b", "c"])
        assert r.field_count == 3

    def test_to_list(self):
        r = CsvRecord(["a", "b"])
        lst = r.to_list()
        assert isinstance(lst, list)
        assert lst == ["a", "b"]

    def test_repr_nonempty(self):
        r = CsvRecord(["a"])
        assert repr(r)

    def test_inherits_spec_class(self):
        r = CsvRecord(["a"])
        assert isinstance(r, SpecRecord)


class TestCsvFieldBehavior:
    def test_instantiation(self):
        f = CsvField("hello")
        assert f is not None

    def test_spec_qname(self):
        assert CsvField.spec_qname == "csv:field"

    def test_spec_fact_ref(self):
        assert CsvField.spec_fact_ref == "FACT-CSV-002"

    def test_value_property(self):
        f = CsvField("hello")
        assert f.value == "hello"

    def test_inherits_spec_class(self):
        f = CsvField("x")
        assert isinstance(f, SpecField)

    def test_repr_nonempty(self):
        f = CsvField("x")
        assert repr(f)


class TestCsvHeaderMetadata:
    def test_spec_qname(self):
        assert CsvHeader.spec_qname == "csv:header"

    def test_spec_fact_ref(self):
        assert CsvHeader.spec_fact_ref == "FACT-CSV-001"

    def test_namespace_uri_present(self):
        assert CsvHeader.namespace_uri


class TestCsvHeaderBehavior:
    def test_instantiation(self):
        h = CsvHeader({"names": ["a", "b"]})
        assert h is not None

    def test_names_property(self):
        h = CsvHeader({"names": ["name", "age", "city"]})
        assert h.names == ["name", "age", "city"]

    def test_count(self):
        h = CsvHeader({"names": ["x", "y"]})
        assert h.count == 2

    def test_has_duplicates_false(self):
        h = CsvHeader({"names": ["a", "b", "c"]})
        assert h.has_duplicates is False

    def test_has_duplicates_true(self):
        h = CsvHeader({"names": ["a", "b", "a"]})
        assert h.has_duplicates is True

    def test_to_dict(self):
        d = {"names": ["x"]}
        h = CsvHeader(d)
        assert h.to_dict() == d

    def test_inherits_spec_class(self):
        h = CsvHeader({"names": []})
        assert isinstance(h, SpecHeader)

    def test_repr_nonempty(self):
        h = CsvHeader({"names": ["a"]})
        assert repr(h)

"""Tests for NdjsonDocument domain model (HO-RC002-MODELS, PQ-T2-003).

Verifies NdjsonDocument wraps load_ndjson() results with typed accessors
and correct spec_qname for V53 compliance.

Gap closure: HO-RC002-MODELS (missing domain models)
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.models import NdjsonDocument


# ---------------------------------------------------------------------------
# spec_qname / class-level attributes
# ---------------------------------------------------------------------------

class TestNdjsonDocumentSpec:
    def test_spec_qname_is_class_attr(self):
        assert NdjsonDocument.spec_qname == "ndjson:record"

    def test_spec_qname_accessible_without_instance(self):
        assert NdjsonDocument.spec_qname == "ndjson:record"

    def test_spec_fact_ref(self):
        assert NdjsonDocument.spec_fact_ref == "SAL-NDJSON-00001"

    def test_namespace_uri(self):
        assert "ndjson" in NdjsonDocument.namespace_uri.lower()

    def test_local_name(self):
        assert NdjsonDocument.local_name == "record"


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestNdjsonDocumentConstruction:
    def test_construct_from_list(self):
        doc = NdjsonDocument([{"a": 1}, {"b": 2}])
        assert isinstance(doc, NdjsonDocument)

    def test_construct_from_empty_list(self):
        doc = NdjsonDocument([])
        assert doc.record_count == 0

    def test_records_are_independent_copy(self):
        original = [{"x": 1}]
        doc = NdjsonDocument(original)
        original.append({"y": 2})
        assert doc.record_count == 1


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

class TestNdjsonDocumentProperties:
    def _doc(self):
        return NdjsonDocument([
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Carol", "age": 35},
        ])

    def test_record_count(self):
        assert self._doc().record_count == 3

    def test_records_returns_list(self):
        records = self._doc().records
        assert isinstance(records, list)
        assert len(records) == 3

    def test_records_returns_copy(self):
        doc = self._doc()
        r = doc.records
        r.append({"extra": True})
        assert doc.record_count == 3

    def test_get_record_valid_index(self):
        doc = self._doc()
        assert doc.get_record(0) == {"name": "Alice", "age": 30}

    def test_get_record_last(self):
        doc = self._doc()
        assert doc.get_record(2) == {"name": "Carol", "age": 35}

    def test_get_record_out_of_bounds(self):
        doc = self._doc()
        assert doc.get_record(99) is None

    def test_get_record_negative_out_of_bounds(self):
        doc = self._doc()
        assert doc.get_record(-1) is None

    def test_get_field_existing(self):
        doc = self._doc()
        assert doc.get_field(0, "name") == "Alice"

    def test_get_field_missing_returns_default(self):
        doc = self._doc()
        assert doc.get_field(0, "nonexistent") is None

    def test_get_field_custom_default(self):
        doc = self._doc()
        assert doc.get_field(0, "missing", "N/A") == "N/A"

    def test_get_field_on_non_dict_record(self):
        doc = NdjsonDocument(["plain_string"])
        assert doc.get_field(0, "key") is None

    def test_to_list_returns_copy(self):
        doc = self._doc()
        lst = doc.to_list()
        lst.clear()
        assert doc.record_count == 3

    def test_repr(self):
        doc = self._doc()
        assert "NdjsonDocument" in repr(doc)
        assert "3" in repr(doc)


# ---------------------------------------------------------------------------
# from_file factory
# ---------------------------------------------------------------------------

class TestNdjsonDocumentFromFile:
    def test_from_file_loads_records(self):
        records = [{"id": 1, "val": "a"}, {"id": 2, "val": "b"}]
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ndjson", delete=False, encoding="utf-8"
        ) as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
            path = Path(f.name)
        try:
            doc = NdjsonDocument.from_file(path)
            assert doc.record_count == 2
            assert doc.get_field(0, "id") == 1
            assert doc.get_field(1, "val") == "b"
        finally:
            path.unlink(missing_ok=True)

    def test_from_file_empty_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".ndjson", delete=False, encoding="utf-8"
        ) as f:
            path = Path(f.name)
        try:
            doc = NdjsonDocument.from_file(path)
            assert doc.record_count == 0
        finally:
            path.unlink(missing_ok=True)

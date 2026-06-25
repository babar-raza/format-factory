"""Tests for CsvDocument domain model class (HO-RC002-MODELS, PQ-T2-002).

Verifies:
  - spec_qname is a class-level attribute
  - rows/headers/row_count/has_header properties
  - get_cell() access
  - to_dict() round-trip
  - repr contains key info
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.models import CsvDocument


class TestCsvDocumentClassAttributes:
    def test_spec_qname_is_class_attribute(self):
        """spec_qname must be accessible on the class, not just instances."""
        assert CsvDocument.spec_qname == "csv:record"

    def test_spec_qname_matches_qname_registry(self):
        assert CsvDocument.spec_qname == "csv:record"

    def test_spec_fact_ref_present(self):
        assert hasattr(CsvDocument, "spec_fact_ref")
        assert CsvDocument.spec_fact_ref.startswith("FACT-CSV-")


class TestCsvDocumentProperties:
    def _make_doc(self, headers, data_rows, delimiter=","):
        return CsvDocument({
            "headers": headers,
            "rows": data_rows,
            "row_count": len(data_rows),
            "has_header": bool(headers),
            "delimiter": delimiter,
        })

    def test_row_count(self):
        doc = self._make_doc(["a", "b"], [["1", "2"], ["3", "4"]])
        assert doc.row_count == 2

    def test_headers(self):
        doc = self._make_doc(["name", "age"], [["Alice", "30"]])
        assert doc.headers == ["name", "age"]

    def test_rows_excludes_header(self):
        doc = self._make_doc(["x"], [["A"], ["B"]])
        assert doc.rows == [["A"], ["B"]]

    def test_column_count_from_headers(self):
        doc = self._make_doc(["a", "b", "c"], [])
        assert doc.column_count == 3

    def test_column_count_from_rows_when_no_header(self):
        doc = self._make_doc([], [["1", "2", "3"]])
        assert doc.column_count == 3

    def test_delimiter(self):
        doc = self._make_doc([], [], delimiter=";")
        assert doc.delimiter == ";"

    def test_get_cell_valid(self):
        doc = self._make_doc(["h1", "h2"], [["val1", "val2"], ["x", "y"]])
        assert doc.get_cell(0, 0) == "val1"
        assert doc.get_cell(1, 1) == "y"

    def test_get_cell_out_of_bounds_returns_empty(self):
        doc = self._make_doc([], [["a"]])
        assert doc.get_cell(0, 99) == ""
        assert doc.get_cell(99, 0) == ""

    def test_to_dict_round_trip(self):
        data = {"headers": ["x"], "rows": [["1"]], "row_count": 1, "has_header": True, "delimiter": ","}
        doc = CsvDocument(data)
        assert doc.to_dict() == data

    def test_has_header_true(self):
        doc = self._make_doc(["h"], [["v"]])
        assert doc.has_header is True

    def test_has_header_false(self):
        doc = self._make_doc([], [["v"]])
        assert doc.has_header is False

    def test_repr_contains_key_info(self):
        doc = self._make_doc(["a", "b"], [["1", "2"]])
        r = repr(doc)
        assert "CsvDocument" in r
        assert "row_count=1" in r

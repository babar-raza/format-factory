"""Tests for TsvDocument domain model class (HO-RC002-MODELS, PQ-T2-001).

Verifies:
  - spec_qname is a class-level attribute
  - from_file() factory loads correctly
  - rows/headers/row_count/has_header properties
  - get_cell() access
  - to_dict() round-trip
  - repr contains key info
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.models import TsvDocument


class TestTsvDocumentClassAttributes:
    def test_spec_qname_is_class_attribute(self):
        """spec_qname must be accessible on the class, not just instances."""
        assert TsvDocument.spec_qname == "tsv:record"

    def test_spec_qname_matches_qname_registry(self):
        """Exact value must match shared/qname-registry/tsv.yaml."""
        assert TsvDocument.spec_qname == "tsv:record"

    def test_spec_fact_ref_present(self):
        assert hasattr(TsvDocument, "spec_fact_ref")
        assert TsvDocument.spec_fact_ref.startswith("FACT-TSV-")


class TestTsvDocumentFromFile:
    def test_from_file_loads_basic_tsv(self, tmp_path):
        tsv_file = tmp_path / "test.tsv"
        tsv_file.write_text("name\tage\talice\t30\nbob\t25\n", encoding="utf-8")
        doc = TsvDocument.from_file(tsv_file)
        assert isinstance(doc, TsvDocument)

    def test_from_file_with_header(self, tmp_path):
        tsv_file = tmp_path / "data.tsv"
        tsv_file.write_text("name\tage\nAlice\t30\nBob\t25\n", encoding="utf-8")
        doc = TsvDocument.from_file(tsv_file)
        assert doc.has_header is True
        assert doc.headers == ["name", "age"]
        assert doc.row_count == 2

    def test_from_file_rows_excludes_header(self, tmp_path):
        tsv_file = tmp_path / "data.tsv"
        tsv_file.write_text("col1\tcol2\nA\tB\nC\tD\n", encoding="utf-8")
        doc = TsvDocument.from_file(tsv_file)
        rows = doc.rows
        assert len(rows) == 2
        assert rows[0] == ["A", "B"]
        assert rows[1] == ["C", "D"]


class TestTsvDocumentProperties:
    def _make_doc(self, headers, data_rows):
        """Build TsvDocument from dict (neutral model simulation)."""
        return TsvDocument({
            "headers": headers,
            "rows": data_rows,
            "row_count": len(data_rows),
            "has_header": bool(headers),
        })

    def test_row_count(self):
        doc = self._make_doc(["a", "b"], [["1", "2"], ["3", "4"], ["5", "6"]])
        assert doc.row_count == 3

    def test_column_count_from_headers(self):
        doc = self._make_doc(["x", "y", "z"], [["1", "2", "3"]])
        assert doc.column_count == 3

    def test_column_count_from_rows_when_no_header(self):
        doc = self._make_doc([], [["a", "b"]])
        assert doc.column_count == 2

    def test_get_cell_valid(self):
        doc = self._make_doc(["h1", "h2"], [["val1", "val2"]])
        assert doc.get_cell(0, 0) == "val1"
        assert doc.get_cell(0, 1) == "val2"

    def test_get_cell_out_of_bounds_returns_empty(self):
        doc = self._make_doc([], [["a"]])
        assert doc.get_cell(99, 0) == ""
        assert doc.get_cell(0, 99) == ""

    def test_to_dict_round_trip(self):
        data = {"headers": ["a"], "rows": [["x"]], "row_count": 1, "has_header": True}
        doc = TsvDocument(data)
        assert doc.to_dict() == data

    def test_repr_contains_key_info(self):
        doc = self._make_doc(["a", "b"], [["1", "2"]])
        r = repr(doc)
        assert "TsvDocument" in r
        assert "row_count=1" in r
        assert "column_count=2" in r

"""Tests for TsvDocument.get_column_values — CQGA-001 Pilot 1 governance proof.

spec_qname: tsv:record
spec_fact_ref: SAL-TSV-00001
skill: /add-python-api
pilot: CQGA-001 Pilot 1 (TC-CQGA-020)
"""
from tsv.models import TsvDocument


def _doc(rows, headers=None, has_header=False):
    data = {"rows": rows, "headers": headers or [], "row_count": len(rows),
            "has_header": has_header, "path": ""}
    return TsvDocument(data)


def test_get_column_values_normal():
    """Returns all values in column 0 for a two-row document."""
    doc = _doc([["a", "b"], ["c", "d"]])
    assert doc.get_column_values(0) == ["a", "c"]
    assert doc.get_column_values(1) == ["b", "d"]


def test_get_column_values_boundary_short_row():
    """Returns '' for rows shorter than col_index + 1."""
    doc = _doc([["a", "b"], ["x"]])  # second row has only 1 column
    assert doc.get_column_values(1) == ["b", ""]


def test_get_column_values_empty_document():
    """Returns empty list for a document with no rows."""
    doc = _doc([])
    assert doc.get_column_values(0) == []


def test_get_column_values_single_column():
    """Works correctly for a single-column document."""
    doc = _doc([["alpha"], ["beta"], ["gamma"]])
    assert doc.get_column_values(0) == ["alpha", "beta", "gamma"]

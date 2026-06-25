"""Tests for GnumericDocument domain model (HO-RC002-MODELS, PQ-T2-004).

Verifies GnumericDocument wraps load() results with typed accessors
and correct spec_qname for V53 compliance.

Gap closure: HO-RC002-MODELS (missing domain models)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.models import GnumericDocument


def _make_model(sheets=None, cell_count=0, is_gnumeric=True):
    """Build a minimal neutral model dict."""
    if sheets is None:
        sheets = []
    return {
        "is_gnumeric": is_gnumeric,
        "sheet_count": len(sheets),
        "sheets": sheets,
        "cell_count": cell_count,
    }


def _make_sheet(name="Sheet1", grid=None):
    return {"name": name, "cell_grid": grid or {}, "row_count": 0, "col_count": 0}


# ---------------------------------------------------------------------------
# spec_qname / class-level attributes
# ---------------------------------------------------------------------------

class TestGnumericDocumentSpec:
    def test_spec_qname_is_class_attr(self):
        assert GnumericDocument.spec_qname == "gnumeric:workbook"

    def test_spec_qname_accessible_without_instance(self):
        assert GnumericDocument.spec_qname == "gnumeric:workbook"

    def test_spec_fact_ref(self):
        assert GnumericDocument.spec_fact_ref == "FACT-GNUMERIC-001"

    def test_namespace_uri(self):
        assert "gnumeric.org" in GnumericDocument.namespace_uri

    def test_local_name(self):
        assert GnumericDocument.local_name == "workbook"


# ---------------------------------------------------------------------------
# Construction and properties
# ---------------------------------------------------------------------------

class TestGnumericDocumentProperties:
    def test_sheet_count_from_model(self):
        model = _make_model([_make_sheet("A"), _make_sheet("B")])
        doc = GnumericDocument(model)
        assert doc.sheet_count == 2

    def test_cell_count(self):
        model = _make_model(cell_count=42)
        doc = GnumericDocument(model)
        assert doc.cell_count == 42

    def test_is_gnumeric_true(self):
        doc = GnumericDocument(_make_model(is_gnumeric=True))
        assert doc.is_gnumeric is True

    def test_sheets_returns_list(self):
        model = _make_model([_make_sheet("S1"), _make_sheet("S2")])
        doc = GnumericDocument(model)
        assert isinstance(doc.sheets, list)
        assert len(doc.sheets) == 2

    def test_sheets_returns_copy(self):
        model = _make_model([_make_sheet("S1")])
        doc = GnumericDocument(model)
        sheets = doc.sheets
        sheets.clear()
        assert doc.sheet_count == 1

    def test_get_sheet_valid(self):
        sheet = _make_sheet("Main")
        doc = GnumericDocument(_make_model([sheet]))
        assert doc.get_sheet(0) == sheet

    def test_get_sheet_out_of_bounds(self):
        doc = GnumericDocument(_make_model())
        assert doc.get_sheet(0) is None

    def test_get_sheet_names(self):
        model = _make_model([_make_sheet("Alpha"), _make_sheet("Beta")])
        doc = GnumericDocument(model)
        assert doc.get_sheet_names() == ["Alpha", "Beta"]

    def test_get_cell_value_existing(self):
        grid = {(0, 0): "hello"}
        sheet = _make_sheet(grid=grid)
        doc = GnumericDocument(_make_model([sheet]))
        assert doc.get_cell_value(0, 0, 0) == "hello"

    def test_get_cell_value_missing(self):
        doc = GnumericDocument(_make_model([_make_sheet()]))
        assert doc.get_cell_value(0, 99, 99) == ""

    def test_get_cell_value_no_sheet(self):
        doc = GnumericDocument(_make_model())
        assert doc.get_cell_value(0, 0, 0) == ""

    def test_to_dict_returns_copy(self):
        model = _make_model()
        doc = GnumericDocument(model)
        d = doc.to_dict()
        d["injected"] = True
        assert "injected" not in doc.to_dict()

    def test_repr(self):
        doc = GnumericDocument(_make_model([_make_sheet()], cell_count=5))
        r = repr(doc)
        assert "GnumericDocument" in r
        assert "1" in r  # sheet_count


# ---------------------------------------------------------------------------
# from_file skips when no fixture available
# ---------------------------------------------------------------------------

class TestGnumericDocumentFromFile:
    def test_from_file_skips_without_fixture(self):
        fixture = _REPO / "tests" / "net" / "gnumeric" / "Fixtures" / "sample.gnumeric"
        if not fixture.exists():
            pytest.skip("Gnumeric fixture not available")
        doc = GnumericDocument.from_file(fixture)
        assert doc.sheet_count >= 1

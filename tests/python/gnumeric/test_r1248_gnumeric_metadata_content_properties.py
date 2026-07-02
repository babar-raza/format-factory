"""Tests for R1248: GnumericDocument metadata and content analysis properties.

Properties under test:
    sheet_names       — names of all sheets in document order
    max_cells_per_sheet — max cell count in any sheet (0 if no sheets)
    is_valid          — alias for is_gnumeric

spec_fact_ref: FACT-GNUMERIC-001
"""

import pytest
from gnumeric.models import GnumericDocument


def _make_doc(sheets: list[dict] | None = None, is_gnumeric: bool = True) -> GnumericDocument:
    """Build a GnumericDocument stub."""
    sheets = sheets or []
    cell_count = sum(len(s.get("cell_grid", {})) for s in sheets)
    return GnumericDocument({
        "is_gnumeric": is_gnumeric,
        "sheet_count": len(sheets),
        "sheets": sheets,
        "cell_count": cell_count,
    })


def _make_sheet(name: str, cell_data: dict | None = None) -> dict:
    """Build a stub sheet dict."""
    return {"name": name, "cell_grid": cell_data or {}}


# ── sheet_names ───────────────────────────────────────────────────────────────

class TestSheetNames:
    def test_empty_workbook_no_names(self):
        doc = _make_doc()
        assert doc.sheet_names == []

    def test_single_sheet_name(self):
        doc = _make_doc([_make_sheet("Sheet1")])
        assert doc.sheet_names == ["Sheet1"]

    def test_multiple_sheet_names_in_order(self):
        doc = _make_doc([_make_sheet("Alpha"), _make_sheet("Beta"), _make_sheet("Gamma")])
        assert doc.sheet_names == ["Alpha", "Beta", "Gamma"]

    def test_consistent_with_sheet_count(self):
        doc = _make_doc([_make_sheet(f"S{i}") for i in range(4)])
        assert len(doc.sheet_names) == doc.sheet_count == 4

    def test_empty_name_sheet(self):
        doc = _make_doc([_make_sheet("")])
        assert doc.sheet_names == [""]


# ── max_cells_per_sheet ───────────────────────────────────────────────────────

class TestMaxCellsPerSheet:
    def test_no_sheets_returns_zero(self):
        doc = _make_doc()
        assert doc.max_cells_per_sheet == 0

    def test_single_sheet_max(self):
        cells = {(0, i): str(i) for i in range(10)}
        doc = _make_doc([_make_sheet("S1", cells)])
        assert doc.max_cells_per_sheet == 10

    def test_max_of_multiple_sheets(self):
        cells_a = {(0, i): str(i) for i in range(5)}
        cells_b = {(0, i): str(i) for i in range(20)}
        doc = _make_doc([_make_sheet("A", cells_a), _make_sheet("B", cells_b)])
        assert doc.max_cells_per_sheet == 20

    def test_empty_sheets_returns_zero(self):
        doc = _make_doc([_make_sheet("S1"), _make_sheet("S2")])
        assert doc.max_cells_per_sheet == 0

    def test_mixed_empty_and_filled(self):
        cells = {(0, i): str(i) for i in range(8)}
        doc = _make_doc([_make_sheet("S1"), _make_sheet("S2", cells)])
        assert doc.max_cells_per_sheet == 8


# ── is_valid ──────────────────────────────────────────────────────────────────

class TestIsValid:
    def test_valid_gnumeric_is_valid(self):
        doc = _make_doc(is_gnumeric=True)
        assert doc.is_valid is True

    def test_invalid_gnumeric_not_valid(self):
        doc = _make_doc(is_gnumeric=False)
        assert doc.is_valid is False

    def test_is_valid_equals_is_gnumeric(self):
        doc = _make_doc(is_gnumeric=True)
        assert doc.is_valid == doc.is_gnumeric


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_sheet_names_count_consistent(self):
        doc = _make_doc([_make_sheet("A"), _make_sheet("B"), _make_sheet("C")])
        assert len(doc.sheet_names) == doc.sheet_count

    def test_max_cells_gte_avg(self):
        cells_a = {(0, i): str(i) for i in range(3)}
        cells_b = {(0, i): str(i) for i in range(7)}
        doc = _make_doc([_make_sheet("A", cells_a), _make_sheet("B", cells_b)])
        assert doc.max_cells_per_sheet >= doc.avg_cells_per_sheet

    def test_valid_with_sheets_and_names(self):
        doc = _make_doc([_make_sheet("Report"), _make_sheet("Data")], is_gnumeric=True)
        assert doc.is_valid is True
        assert "Report" in doc.sheet_names
        assert "Data" in doc.sheet_names

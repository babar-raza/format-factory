"""Tests for R1256: OdsModelDocument workbook density and shape properties.

Properties under test:
    is_uniform_sheet_size — all sheets have the same row count
    min_sheet_rows        — minimum row count in any single sheet (0 if no sheets)
    sheet_row_range       — max_sheet_rows - min_sheet_rows (0 if no sheets)

spec_fact_ref: FACT-ODS-001
"""

import types
import pytest
from ods.models import OdsModelDocument, OdsSheetModel


def _make_doc(sheet_row_counts: list[int]) -> OdsModelDocument:
    """Build OdsModelDocument stub. Each sheet has rows as a list of row stubs."""
    sheets = []
    for i, rc in enumerate(sheet_row_counts):
        # OdsSheetModel wraps _sheet; row_count = len(_sheet.rows)
        sheet = types.SimpleNamespace(
            name=f"Sheet{i+1}",
            rows=[types.SimpleNamespace(cells=[]) for _ in range(rc)],
        )
        sheets.append(sheet)

    parsed = types.SimpleNamespace(
        sheet_count=len(sheets),
        sheet_names=[f"Sheet{i+1}" for i in range(len(sheets))],
        path="test.ods",
        sheets=sheets,
    )
    return OdsModelDocument(parsed)


# ── is_uniform_sheet_size ─────────────────────────────────────────────────────

class TestIsUniformSheetSize:
    def test_single_sheet_is_uniform(self):
        doc = _make_doc([5])
        assert doc.is_uniform_sheet_size is True

    def test_no_sheets_is_uniform(self):
        doc = _make_doc([])
        assert doc.is_uniform_sheet_size is True

    def test_equal_row_counts_uniform(self):
        doc = _make_doc([10, 10, 10])
        assert doc.is_uniform_sheet_size is True

    def test_different_row_counts_not_uniform(self):
        doc = _make_doc([5, 10])
        assert doc.is_uniform_sheet_size is False

    def test_all_zero_row_count_uniform(self):
        doc = _make_doc([0, 0, 0])
        assert doc.is_uniform_sheet_size is True


# ── min_sheet_rows ────────────────────────────────────────────────────────────

class TestMinSheetRows:
    def test_no_sheets_returns_zero(self):
        doc = _make_doc([])
        assert doc.min_sheet_rows == 0

    def test_single_sheet(self):
        doc = _make_doc([7])
        assert doc.min_sheet_rows == 7

    def test_multiple_sheets_min(self):
        doc = _make_doc([3, 10, 5])
        assert doc.min_sheet_rows == 3

    def test_all_zero_min(self):
        doc = _make_doc([0, 0])
        assert doc.min_sheet_rows == 0


# ── sheet_row_range ───────────────────────────────────────────────────────────

class TestSheetRowRange:
    def test_no_sheets_returns_zero(self):
        doc = _make_doc([])
        assert doc.sheet_row_range == 0

    def test_uniform_range_zero(self):
        doc = _make_doc([5, 5, 5])
        assert doc.sheet_row_range == 0

    def test_range_equals_max_minus_min(self):
        doc = _make_doc([2, 10])
        assert doc.sheet_row_range == 8

    def test_large_range(self):
        doc = _make_doc([0, 100, 50])
        assert doc.sheet_row_range == 100


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_uniform_implies_zero_range(self):
        doc = _make_doc([8, 8, 8])
        assert doc.is_uniform_sheet_size is True
        assert doc.sheet_row_range == 0

    def test_nonuniform_implies_positive_range(self):
        doc = _make_doc([3, 9])
        assert doc.is_uniform_sheet_size is False
        assert doc.sheet_row_range > 0

    def test_min_le_max(self):
        doc = _make_doc([1, 5, 3])
        assert doc.min_sheet_rows <= doc.max_sheet_rows

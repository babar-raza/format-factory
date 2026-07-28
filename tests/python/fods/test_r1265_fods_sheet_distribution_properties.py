"""Tests for R1265: FodsDocument sheet distribution analysis properties.

Properties under test:
    min_sheet_rows      — minimum row count in any sheet (0 if no sheets)
    sheet_row_range     — max_sheet_rows - min_sheet_rows
    is_uniform_sheet_size — all sheets have same row count (sheet_row_range == 0)

spec_fact_ref: SAL-FODS-00001
"""

import pytest
from fods.models import FodsDocument


def _make_sheet(name: str, row_count: int) -> dict:
    rows = [{"cells": []} for _ in range(row_count)]
    return {"name": name, "rows": rows}


def _make_doc(sheet_row_counts: list[int]) -> FodsDocument:
    sheets = [_make_sheet(f"Sheet{i+1}", rc) for i, rc in enumerate(sheet_row_counts)]
    return FodsDocument({
        "format_id": "fods",
        "odf_version": "1.3",
        "sheets": sheets,
        "warnings": [],
    })


# ── min_sheet_rows ────────────────────────────────────────────────────────────

class TestMinSheetRows:
    def test_no_sheets_returns_zero(self):
        doc = _make_doc([])
        assert doc.min_sheet_rows == 0

    def test_single_sheet_min(self):
        doc = _make_doc([50])
        assert doc.min_sheet_rows == 50

    def test_picks_smallest(self):
        doc = _make_doc([100, 50, 200])
        assert doc.min_sheet_rows == 50

    def test_all_same_min_equals_max(self):
        doc = _make_doc([100, 100, 100])
        assert doc.min_sheet_rows == 100

    def test_one_empty_sheet(self):
        doc = _make_doc([0, 100, 200])
        assert doc.min_sheet_rows == 0


# ── sheet_row_range ───────────────────────────────────────────────────────────

class TestSheetRowRange:
    def test_no_sheets_range_zero(self):
        doc = _make_doc([])
        assert doc.sheet_row_range == 0

    def test_single_sheet_range_zero(self):
        doc = _make_doc([100])
        assert doc.sheet_row_range == 0

    def test_equal_sheets_range_zero(self):
        doc = _make_doc([200, 200, 200])
        assert doc.sheet_row_range == 0

    def test_varied_sheets_range(self):
        doc = _make_doc([100, 500])
        assert doc.sheet_row_range == 400

    def test_range_is_max_minus_min(self):
        doc = _make_doc([50, 150, 300])
        assert doc.sheet_row_range == doc.max_sheet_rows - doc.min_sheet_rows


# ── is_uniform_sheet_size ─────────────────────────────────────────────────────

class TestIsUniformSheetSize:
    def test_no_sheets_is_uniform(self):
        doc = _make_doc([])
        assert doc.is_uniform_sheet_size is True

    def test_single_sheet_is_uniform(self):
        doc = _make_doc([100])
        assert doc.is_uniform_sheet_size is True

    def test_equal_sheets_uniform(self):
        doc = _make_doc([100, 100, 100])
        assert doc.is_uniform_sheet_size is True

    def test_different_sizes_not_uniform(self):
        doc = _make_doc([100, 200])
        assert doc.is_uniform_sheet_size is False

    def test_one_empty_not_uniform(self):
        doc = _make_doc([0, 100])
        assert doc.is_uniform_sheet_size is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_uniform_implies_zero_range(self):
        doc = _make_doc([150, 150])
        assert doc.is_uniform_sheet_size is True
        assert doc.sheet_row_range == 0

    def test_nonzero_range_implies_not_uniform(self):
        doc = _make_doc([100, 300])
        assert doc.sheet_row_range > 0
        assert doc.is_uniform_sheet_size is False

    def test_range_consistent_with_min_max(self):
        doc = _make_doc([50, 100, 200, 350])
        assert doc.sheet_row_range == doc.max_sheet_rows - doc.min_sheet_rows
        assert doc.min_sheet_rows == 50
        assert doc.max_sheet_rows == 350

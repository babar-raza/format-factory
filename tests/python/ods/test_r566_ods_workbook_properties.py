"""R566: ODS additional workbook properties — has_sheets, total_row_count, max_sheet_rows.

Tests for OdsModelDocument workbook analysis properties added in R566.
Spec refs: SAL-ODS-01068 (office:document), SAL-ODS-00001 (table:table).
"""

import types
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.models import OdsModelDocument, OdsDoc

SAMPLES = Path("samples/by-format/ods/valid")


def _make_sheet(name="Sheet1", row_count=0):
    """Build a fake ODS sheet stub."""
    rows = [types.SimpleNamespace(cells=[]) for _ in range(row_count)]
    return types.SimpleNamespace(name=name, rows=rows)


def _make_doc(sheet_configs=None):
    """Build a minimal OdsModelDocument.

    sheet_configs: list of (name, row_count) tuples.
    """
    if sheet_configs is None:
        sheet_configs = []
    sheets = [_make_sheet(name, rc) for name, rc in sheet_configs]
    parsed = types.SimpleNamespace(sheets=sheets, path="test.ods")
    return OdsModelDocument(parsed)


class TestHasSheets:
    def test_no_sheets(self):
        doc = _make_doc([])
        assert doc.has_sheets is False

    def test_one_sheet(self):
        doc = _make_doc([("Sheet1", 0)])
        assert doc.has_sheets is True

    def test_multiple_sheets(self):
        doc = _make_doc([("S1", 0), ("S2", 0)])
        assert doc.has_sheets is True

    def test_has_sheets_type(self):
        doc = _make_doc([("S1", 1)])
        assert isinstance(doc.has_sheets, bool)

    def test_has_sheets_inverse_of_is_empty(self):
        doc_empty = _make_doc([])
        doc_with = _make_doc([("S1", 0)])
        assert doc_empty.is_empty is True
        assert doc_empty.has_sheets is False
        assert doc_with.is_empty is False
        assert doc_with.has_sheets is True


class TestTotalRowCount:
    def test_no_sheets_zero_rows(self):
        doc = _make_doc([])
        assert doc.total_row_count == 0

    def test_one_sheet_five_rows(self):
        doc = _make_doc([("S1", 5)])
        assert doc.total_row_count == 5

    def test_two_sheets_combined(self):
        doc = _make_doc([("S1", 3), ("S2", 4)])
        assert doc.total_row_count == 7

    def test_three_sheets_zero_rows(self):
        doc = _make_doc([("S1", 0), ("S2", 0), ("S3", 0)])
        assert doc.total_row_count == 0

    def test_total_row_count_type(self):
        doc = _make_doc([("S1", 2)])
        assert isinstance(doc.total_row_count, int)


class TestMaxSheetRows:
    def test_no_sheets_zero_max(self):
        doc = _make_doc([])
        assert doc.max_sheet_rows == 0

    def test_one_sheet(self):
        doc = _make_doc([("S1", 7)])
        assert doc.max_sheet_rows == 7

    def test_two_sheets_returns_max(self):
        doc = _make_doc([("S1", 3), ("S2", 10)])
        assert doc.max_sheet_rows == 10

    def test_all_zero_rows(self):
        doc = _make_doc([("S1", 0), ("S2", 0)])
        assert doc.max_sheet_rows == 0

    def test_max_sheet_rows_type(self):
        doc = _make_doc([("S1", 5)])
        assert isinstance(doc.max_sheet_rows, int)

    def test_max_consistent_with_sheets(self):
        doc = _make_doc([("S1", 2), ("S2", 8), ("S3", 5)])
        assert doc.max_sheet_rows == 8
        assert doc.total_row_count == 15


class TestWorkbookPropertyConsistency:
    def test_has_sheets_implies_not_is_empty(self):
        doc = _make_doc([("S1", 3)])
        assert doc.has_sheets is True
        assert doc.is_empty is False

    def test_is_empty_implies_zero_rows(self):
        doc = _make_doc([])
        assert doc.is_empty is True
        assert doc.total_row_count == 0
        assert doc.max_sheet_rows == 0

    def test_alias_has_properties(self):
        doc = _make_doc([("S1", 2)])
        assert isinstance(doc, OdsDoc)
        assert hasattr(doc, "has_sheets")
        assert hasattr(doc, "total_row_count")
        assert hasattr(doc, "max_sheet_rows")

    def test_from_file(self):
        doc = OdsModelDocument.from_file(SAMPLES / "minimal-spreadsheet.ods")
        assert isinstance(doc.has_sheets, bool)
        assert isinstance(doc.total_row_count, int)
        assert isinstance(doc.max_sheet_rows, int)
        assert doc.has_sheets is True
        assert doc.total_row_count >= 0

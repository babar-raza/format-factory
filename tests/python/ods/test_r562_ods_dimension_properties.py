"""R562: ODS dimension properties — is_empty, is_single_sheet, is_multi_sheet.

Tests for OdsModelDocument dimension properties added in R562.
Spec refs: ODF-SHEET-FACT-TABLE.
"""

import types
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.models import OdsModelDocument, OdsDoc

SAMPLES = Path("samples/by-format/ods/valid")


def _make_doc(sheet_count=0):
    """Build a minimal OdsModelDocument from a stub parsed object."""
    sheets = [types.SimpleNamespace(name=f"Sheet{i}", rows=[]) for i in range(sheet_count)]
    return OdsModelDocument(types.SimpleNamespace(sheets=sheets, path="test.ods"))


class TestIsEmpty:
    def test_no_sheets_is_empty(self):
        doc = _make_doc(sheet_count=0)
        assert doc.is_empty is True

    def test_one_sheet_not_empty(self):
        doc = _make_doc(sheet_count=1)
        assert doc.is_empty is False

    def test_multiple_sheets_not_empty(self):
        doc = _make_doc(sheet_count=3)
        assert doc.is_empty is False

    def test_is_empty_type(self):
        doc = _make_doc(sheet_count=0)
        assert isinstance(doc.is_empty, bool)


class TestIsSingleSheet:
    def test_one_sheet_is_single(self):
        doc = _make_doc(sheet_count=1)
        assert doc.is_single_sheet is True

    def test_zero_sheets_not_single(self):
        doc = _make_doc(sheet_count=0)
        assert doc.is_single_sheet is False

    def test_two_sheets_not_single(self):
        doc = _make_doc(sheet_count=2)
        assert doc.is_single_sheet is False

    def test_is_single_sheet_type(self):
        doc = _make_doc(sheet_count=1)
        assert isinstance(doc.is_single_sheet, bool)


class TestIsMultiSheet:
    def test_two_sheets_is_multi(self):
        doc = _make_doc(sheet_count=2)
        assert doc.is_multi_sheet is True

    def test_one_sheet_not_multi(self):
        doc = _make_doc(sheet_count=1)
        assert doc.is_multi_sheet is False

    def test_zero_sheets_not_multi(self):
        doc = _make_doc(sheet_count=0)
        assert doc.is_multi_sheet is False

    def test_many_sheets_is_multi(self):
        doc = _make_doc(sheet_count=5)
        assert doc.is_multi_sheet is True

    def test_is_multi_sheet_type(self):
        doc = _make_doc(sheet_count=2)
        assert isinstance(doc.is_multi_sheet, bool)


class TestDimensionConsistency:
    def test_empty_not_single_not_multi(self):
        doc = _make_doc(sheet_count=0)
        assert doc.is_empty
        assert not doc.is_single_sheet
        assert not doc.is_multi_sheet

    def test_single_not_empty_not_multi(self):
        doc = _make_doc(sheet_count=1)
        assert not doc.is_empty
        assert doc.is_single_sheet
        assert not doc.is_multi_sheet

    def test_multi_not_empty_not_single(self):
        doc = _make_doc(sheet_count=3)
        assert not doc.is_empty
        assert not doc.is_single_sheet
        assert doc.is_multi_sheet

    def test_alias_ods_doc_has_properties(self):
        doc = _make_doc(sheet_count=1)
        assert isinstance(doc, OdsDoc)
        assert hasattr(doc, "is_empty")
        assert hasattr(doc, "is_single_sheet")
        assert hasattr(doc, "is_multi_sheet")

    def test_from_file_minimal(self):
        doc = OdsModelDocument.from_file(SAMPLES / "minimal-spreadsheet.ods")
        assert isinstance(doc.is_empty, bool)
        assert isinstance(doc.is_single_sheet, bool)
        assert isinstance(doc.is_multi_sheet, bool)

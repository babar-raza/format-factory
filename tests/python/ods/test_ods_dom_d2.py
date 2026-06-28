"""Tests for ODS DOM D2 typed wrappers — OdsSheetModel, OdsCellModel."""
from pathlib import Path

import pytest

from ods.models import OdsModelDocument, OdsSheetModel, OdsCellModel

SAMPLE = Path("samples/by-format/ods/valid/minimal-spreadsheet.ods")


@pytest.fixture
def doc():
    if not SAMPLE.exists():
        pytest.skip("ODS sample not available")
    return OdsModelDocument.from_file(SAMPLE)


def test_sheets_returns_typed_list(doc):
    sheets = doc.sheets()
    assert isinstance(sheets, list)
    assert len(sheets) >= 1
    assert all(isinstance(s, OdsSheetModel) for s in sheets)


def test_sheet_model_name(doc):
    sheet = doc.sheets()[0]
    assert isinstance(sheet.name, str)
    assert len(sheet.name) > 0


def test_sheet_model_cells_yields_cell_models(doc):
    sheet = doc.sheets()[0]
    cells = list(sheet.cells())
    assert len(cells) >= 1
    assert all(isinstance(c, OdsCellModel) for c in cells)


def test_cell_model_value(doc):
    sheet = doc.sheets()[0]
    cell = sheet.cell_at(0, 0)
    assert cell is not None
    assert isinstance(cell, OdsCellModel)


def test_cell_model_spec_qname():
    assert OdsCellModel.spec_qname == "table:table-cell"


def test_sheet_model_spec_qname():
    assert OdsSheetModel.spec_qname == "table:table"


def test_sheet_model_to_dict(doc):
    sheet = doc.sheets()[0]
    d = sheet.to_dict()
    assert "name" in d
    assert "row_count" in d


def test_cell_model_to_dict(doc):
    sheet = doc.sheets()[0]
    cell = sheet.cell_at(0, 0)
    if cell:
        d = cell.to_dict()
        assert "value" in d
        assert "value_type" in d
        assert "text" in d


def test_get_sheet_returns_typed(doc):
    sheet = doc.get_sheet(0)
    assert isinstance(sheet, OdsSheetModel)


def test_get_sheet_out_of_range(doc):
    assert doc.get_sheet(999) is None

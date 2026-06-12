"""
test_ods_sheet_names_count_pipeline.py -- ODS get_sheet_names + count_sheets pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-95
Tests get_sheet_names returns list, names has expected values, count_sheets int,
count_sheets=2, add sheet then count_sheets increases.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    OdsDocument,
    OdsSheet,
    OdsRow,
    OdsCell,
    write_ods,
    get_sheet_names,
    count_sheets,
    add_sheet,
)


def _make_doc(tmp_path):
    sheet1 = OdsSheet(name="Revenue")
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="Q1"), OdsCell(value="Q2")]))
    sheet2 = OdsSheet(name="Costs")
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="Fixed"), OdsCell(value="Variable")]))
    doc = OdsDocument(sheets=[sheet1, sheet2])
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    return doc, dest


def test_get_sheet_names_returns_list(tmp_path):
    doc, dest = _make_doc(tmp_path)
    names = get_sheet_names(str(dest))
    assert isinstance(names, list)


def test_get_sheet_names_has_expected_values(tmp_path):
    doc, dest = _make_doc(tmp_path)
    names = get_sheet_names(str(dest))
    assert "Revenue" in names
    assert "Costs" in names


def test_count_sheets_int(tmp_path):
    doc, dest = _make_doc(tmp_path)
    count = count_sheets(str(dest))
    assert isinstance(count, int)


def test_count_sheets_value(tmp_path):
    doc, dest = _make_doc(tmp_path)
    count = count_sheets(str(dest))
    assert count == 2


def test_add_sheet_increases_count(tmp_path):
    doc, dest = _make_doc(tmp_path)
    before = count_sheets(str(dest))
    ok, _ = add_sheet(doc, "NewSheet")
    write_ods(doc, str(dest))
    after = count_sheets(str(dest))
    assert after == before + 1

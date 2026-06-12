"""
test_ods_remove_rename_sheet_pipeline.py -- ODS remove_sheet + rename_sheet pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-98
Tests remove_sheet decreases count, remove returns True, rename_sheet changes name,
renamed sheet accessible, rename returns True.
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
    count_sheets,
    get_sheet_names,
    remove_sheet,
    rename_sheet,
)


def _make_doc(tmp_path):
    sheet1 = OdsSheet(name="Alpha")
    sheet1.rows.append(OdsRow(cells=[OdsCell(value="A1")]))
    sheet2 = OdsSheet(name="Beta")
    sheet2.rows.append(OdsRow(cells=[OdsCell(value="B1")]))
    sheet3 = OdsSheet(name="Gamma")
    sheet3.rows.append(OdsRow(cells=[OdsCell(value="G1")]))
    doc = OdsDocument(sheets=[sheet1, sheet2, sheet3])
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    return doc, dest


def test_remove_sheet_decreases_count(tmp_path):
    doc, dest = _make_doc(tmp_path)
    before = count_sheets(str(dest))
    ok, _ = remove_sheet(doc, "Beta")
    assert ok is True
    write_ods(doc, str(dest))
    after = count_sheets(str(dest))
    assert after == before - 1


def test_remove_sheet_returns_true(tmp_path):
    doc, dest = _make_doc(tmp_path)
    ok, msg = remove_sheet(doc, "Gamma")
    assert ok is True


def test_rename_sheet_changes_name(tmp_path):
    doc, dest = _make_doc(tmp_path)
    ok, _ = rename_sheet(doc, "Alpha", "Renamed")
    write_ods(doc, str(dest))
    names = get_sheet_names(str(dest))
    assert "Renamed" in names
    assert "Alpha" not in names


def test_rename_sheet_returns_true(tmp_path):
    doc, dest = _make_doc(tmp_path)
    ok, msg = rename_sheet(doc, "Beta", "NewBeta")
    assert ok is True


def test_rename_and_remove_pipeline(tmp_path):
    doc, dest = _make_doc(tmp_path)
    rename_sheet(doc, "Alpha", "First")
    remove_sheet(doc, "Gamma")
    write_ods(doc, str(dest))
    names = get_sheet_names(str(dest))
    assert "First" in names
    assert "Gamma" not in names
    assert len(names) == 2

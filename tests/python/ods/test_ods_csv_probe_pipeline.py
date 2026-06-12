"""
test_ods_csv_probe_pipeline.py -- ODS CSV export + probe pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-77
Tests export_ods_to_csv returns string, probe_ods valid container, ods_to_csv
string, get_all_values list, get_cell_count int.
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
    parse_ods_strict,
    probe_ods,
    ods_to_csv,
    get_all_values,
    get_cell_count,
)
from ods.ods_csv_exporter import export_ods_to_csv


def _make_doc(tmp_path):
    sheet = OdsSheet(name="Data")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Name"), OdsCell(value="Score")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Alice"), OdsCell(value="90")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Bob"), OdsCell(value="75")]))
    doc = OdsDocument(sheets=[sheet])
    dest = tmp_path / "data.ods"
    write_ods(doc, str(dest))
    return dest


def test_export_ods_to_csv_returns_string(tmp_path):
    dest = _make_doc(tmp_path)
    doc = parse_ods_strict(str(dest))
    result = export_ods_to_csv(doc)
    assert isinstance(result, str)
    assert "Alice" in result


def test_probe_ods_valid_container(tmp_path):
    dest = _make_doc(tmp_path)
    result = probe_ods(str(dest))
    assert result.get("valid_container") is True


def test_ods_to_csv_string(tmp_path):
    dest = _make_doc(tmp_path)
    result = ods_to_csv(str(dest))
    assert isinstance(result, str)


def test_get_all_values_list(tmp_path):
    dest = _make_doc(tmp_path)
    result = get_all_values(str(dest))
    assert isinstance(result, list)
    assert len(result) > 0


def test_get_cell_count_int(tmp_path):
    dest = _make_doc(tmp_path)
    result = get_cell_count(str(dest))
    assert isinstance(result, int)
    assert result == 6

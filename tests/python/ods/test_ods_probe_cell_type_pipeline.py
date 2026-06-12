"""
test_ods_probe_cell_type_pipeline.py -- ODS probe + cell type pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-62
Tests probe_ods exists, probe_ods valid_container, ods_cell_type_distribution dict,
get_all_values list, get_column_count int.
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
    parse_ods,
    probe_ods,
    get_all_values,
    get_column_count,
    ods_cell_type_distribution,
)


def _make_doc(tmp_path):
    sheet = OdsSheet(name="Data")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Name"), OdsCell(value="Score")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Alice"), OdsCell(value="90")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Bob"), OdsCell(value="80")]))
    doc = OdsDocument(sheets=[sheet])
    dest = tmp_path / "test.ods"
    write_ods(doc, str(dest))
    return dest


def test_probe_ods_exists(tmp_path):
    dest = _make_doc(tmp_path)
    result = probe_ods(str(dest))
    assert result["exists"] is True


def test_probe_ods_valid_container(tmp_path):
    dest = _make_doc(tmp_path)
    result = probe_ods(str(dest))
    assert result.get("valid_container") is True


def test_ods_cell_type_distribution_dict(tmp_path):
    dest = _make_doc(tmp_path)
    ods_doc = parse_ods(str(dest))
    dist = ods_cell_type_distribution(ods_doc)
    assert isinstance(dist, dict)


def test_get_all_values_list(tmp_path):
    dest = _make_doc(tmp_path)
    vals = get_all_values(str(dest), sheet_index=0)
    assert isinstance(vals, list)
    assert "Alice" in vals


def test_get_column_count_int(tmp_path):
    dest = _make_doc(tmp_path)
    count = get_column_count(str(dest), sheet_index=0)
    assert isinstance(count, int)
    assert count == 2

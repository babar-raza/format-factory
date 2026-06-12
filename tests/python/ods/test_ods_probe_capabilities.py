"""
test_ods_probe_capabilities.py -- ODS probe + get_capabilities pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-36
Tests probe_ods on written file, get_capabilities returns dict with format,
parse_ods returns neutral dict, parse_ods_strict returns OdsDocument,
get_cell_count on single-cell sheet.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import (
    OdsDocument,
    OdsSheet,
    OdsRow,
    OdsCell,
    probe_ods,
    get_capabilities,
    parse_ods,
    parse_ods_strict,
    get_cell_count,
)
from ods.ods_writer import write_ods


def _make_doc(tmp_path):
    sheet = OdsSheet(name="Test")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="A"), OdsCell(value="B")]))
    doc = OdsDocument(sheets=[sheet])
    dest = tmp_path / "test.ods"
    write_ods(doc, str(dest))
    return dest


def test_probe_ods_written_file(tmp_path):
    dest = _make_doc(tmp_path)
    result = probe_ods(str(dest))
    assert result["valid_container"] is True


def test_get_capabilities_format():
    caps = get_capabilities()
    assert caps["format"] == "ods"


def test_parse_ods_returns_dict(tmp_path):
    dest = _make_doc(tmp_path)
    result = parse_ods(str(dest))
    assert isinstance(result, dict)
    assert "sheets" in result


def test_parse_ods_strict_returns_document(tmp_path):
    dest = _make_doc(tmp_path)
    doc = parse_ods_strict(str(dest))
    assert isinstance(doc, OdsDocument)
    assert len(doc.sheets) == 1


def test_get_cell_count_two_cells(tmp_path):
    dest = _make_doc(tmp_path)
    count = get_cell_count(str(dest), sheet_index=0)
    assert count == 2

"""
test_ods_probe_all_values_pipeline.py -- ODS probe_ods + get_all_values pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-104
Tests probe_ods returns dict, has valid_container=True, get_all_values returns list,
has Alice, count >= 3.
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
    probe_ods,
    get_all_values,
)


def _make_doc(tmp_path):
    sheet = OdsSheet(name="Data")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Alice"), OdsCell(value="eng")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Bob"), OdsCell(value="hr")]))
    doc = OdsDocument(sheets=[sheet])
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    return dest


def test_probe_ods_returns_dict(tmp_path):
    dest = _make_doc(tmp_path)
    result = probe_ods(str(dest))
    assert isinstance(result, dict)


def test_probe_ods_valid_container(tmp_path):
    dest = _make_doc(tmp_path)
    result = probe_ods(str(dest))
    assert result.get("valid_container") is True


def test_get_all_values_returns_list(tmp_path):
    dest = _make_doc(tmp_path)
    values = get_all_values(str(dest))
    assert isinstance(values, list)


def test_get_all_values_has_alice(tmp_path):
    dest = _make_doc(tmp_path)
    values = get_all_values(str(dest))
    assert "Alice" in values


def test_get_all_values_count(tmp_path):
    dest = _make_doc(tmp_path)
    values = get_all_values(str(dest))
    assert len(values) >= 3

"""
test_ods_csv_filter_pipeline.py -- ODS ods_to_csv + filter_rows_by_value pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-101
Tests ods_to_csv returns string, csv has Alice, filter_rows_by_value returns list,
filter finds eng rows count=2, filter empty for no match.
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
    ods_to_csv,
    filter_rows_by_value,
)


def _make_doc(tmp_path):
    sheet = OdsSheet(name="Staff")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Alice"), OdsCell(value="eng")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Bob"), OdsCell(value="hr")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Carol"), OdsCell(value="eng")]))
    doc = OdsDocument(sheets=[sheet])
    dest = tmp_path / "doc.ods"
    write_ods(doc, str(dest))
    return dest


def test_ods_to_csv_returns_string(tmp_path):
    dest = _make_doc(tmp_path)
    csv_str = ods_to_csv(str(dest))
    assert isinstance(csv_str, str)


def test_ods_to_csv_has_alice(tmp_path):
    dest = _make_doc(tmp_path)
    csv_str = ods_to_csv(str(dest))
    assert "Alice" in csv_str


def test_filter_rows_returns_list(tmp_path):
    dest = _make_doc(tmp_path)
    rows = filter_rows_by_value(str(dest), col=1, value="eng")
    assert isinstance(rows, list)


def test_filter_rows_correct_count(tmp_path):
    dest = _make_doc(tmp_path)
    rows = filter_rows_by_value(str(dest), col=1, value="eng")
    assert len(rows) == 2


def test_filter_rows_empty_no_match(tmp_path):
    dest = _make_doc(tmp_path)
    rows = filter_rows_by_value(str(dest), col=1, value="finance")
    assert rows == []

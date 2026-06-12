"""
test_ods_multirow_agg_pipeline.py -- ODS multirow aggregation pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-80
Tests sum_column float, average_column float, max_column_value, min_column_value,
get_row_count int.
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
    sum_column,
    average_column,
    max_column_value,
    min_column_value,
    get_row_count,
)


def _make_doc(tmp_path):
    sheet = OdsSheet(name="Data")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Item"), OdsCell(value="Score")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="A"), OdsCell(value=10.0, value_type="float")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="B"), OdsCell(value=20.0, value_type="float")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="C"), OdsCell(value=30.0, value_type="float")]))
    sheet.rows.append(OdsRow(cells=[OdsCell(value="D"), OdsCell(value=40.0, value_type="float")]))
    doc = OdsDocument(sheets=[sheet])
    dest = tmp_path / "agg.ods"
    write_ods(doc, str(dest))
    return dest


def test_sum_column_float(tmp_path):
    dest = _make_doc(tmp_path)
    total = sum_column(str(dest), col=1)
    assert isinstance(total, float)
    assert total == 100.0


def test_average_column_float(tmp_path):
    dest = _make_doc(tmp_path)
    avg = average_column(str(dest), col=1)
    assert isinstance(avg, float)
    assert avg == 25.0


def test_max_column_value(tmp_path):
    dest = _make_doc(tmp_path)
    result = max_column_value(str(dest), col=1)
    assert result == 40.0


def test_min_column_value(tmp_path):
    dest = _make_doc(tmp_path)
    result = min_column_value(str(dest), col=1)
    assert result == 10.0


def test_get_row_count_int(tmp_path):
    dest = _make_doc(tmp_path)
    count = get_row_count(str(dest))
    assert isinstance(count, int)
    assert count == 5

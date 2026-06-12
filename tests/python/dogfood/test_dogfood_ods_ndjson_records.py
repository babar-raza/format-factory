"""
test_dogfood_ods_ndjson_records.py -- ODS->NDJSON records cross-format pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-23
Tests extracting ODS spreadsheet rows and converting them to NDJSON records.
Uses minimal-spreadsheet.ods (Name/Value, Alpha/42.0).
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_ODS_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"

from ods.ods_parser import (
    parse_ods_strict,
    get_sheet_names,
    get_row_count,
    get_cell_value,
    get_all_values,
)


def _ods_rows_to_records(file_path: str) -> list[dict]:
    """Extract ODS sheet into list of dicts using first row as header keys."""
    doc = parse_ods_strict(file_path)
    sheet = doc.sheets[0]
    if not sheet.rows:
        return []
    header_row = sheet.rows[0]
    headers = [c.text or str(c.value or "") for c in header_row.cells]
    records = []
    for row in sheet.rows[1:]:
        rec = {}
        for i, cell in enumerate(row.cells):
            key = headers[i] if i < len(headers) else f"col{i}"
            rec[key] = cell.text or cell.value
        records.append(rec)
    return records


def test_ods_to_records_count():
    records = _ods_rows_to_records(str(_ODS_SAMPLES / "minimal-spreadsheet.ods"))
    assert len(records) == 1


def test_ods_to_records_has_name_key():
    records = _ods_rows_to_records(str(_ODS_SAMPLES / "minimal-spreadsheet.ods"))
    assert "Name" in records[0]


def test_ods_to_records_name_value():
    records = _ods_rows_to_records(str(_ODS_SAMPLES / "minimal-spreadsheet.ods"))
    assert records[0]["Name"] == "Alpha"


def test_ods_row_count_from_parser():
    row_count = get_row_count(str(_ODS_SAMPLES / "minimal-spreadsheet.ods"))
    assert row_count == 2


def test_ods_all_values_contains_alpha():
    all_vals = get_all_values(str(_ODS_SAMPLES / "minimal-spreadsheet.ods"))
    str_vals = [str(v) for v in all_vals]
    assert "Alpha" in str_vals

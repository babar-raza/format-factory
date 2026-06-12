"""
test_dogfood_gnumeric_tsv_pipeline.py -- Cross-format Gnumeric->TSV pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-24
Tests extracting Gnumeric sheet rows and writing them to TSV,
then verifying the TSV has correct headers and values.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_GNUMERIC_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"

from gnumeric.gnumeric_codec import (
    load as load_gnumeric,
    get_cell_value,
    get_row_count,
    get_column_count,
)

sys.path.insert(0, str(_REPO))
from src.python.tsv.tsv_parser import write_tsv, get_headers, count_rows, get_column


def _gnumeric_to_tsv_rows(model, sheet_idx: int = 0) -> tuple[list[str], list[list[str]]]:
    """Extract headers and data rows from a Gnumeric sheet."""
    row_count = get_row_count(model, sheet_idx)
    col_count = get_column_count(model, sheet_idx)
    rows = []
    for r in range(row_count):
        row = [get_cell_value(model, sheet_idx, r, c) for c in range(col_count)]
        rows.append(row)
    if not rows:
        return [], []
    headers = rows[0]
    data_rows = rows[1:]
    return headers, data_rows


def test_gnumeric_to_tsv_headers(tmp_path):
    m = load_gnumeric(str(_GNUMERIC_SAMPLES / "multi-cell-basic.gnumeric"))
    headers, data_rows = _gnumeric_to_tsv_rows(m)
    dest = tmp_path / "gnumeric_export.tsv"
    write_tsv(data_rows, str(dest), headers=headers)
    assert get_headers(str(dest)) == headers


def test_gnumeric_to_tsv_row_count(tmp_path):
    m = load_gnumeric(str(_GNUMERIC_SAMPLES / "multi-cell-basic.gnumeric"))
    headers, data_rows = _gnumeric_to_tsv_rows(m)
    dest = tmp_path / "gnumeric_export.tsv"
    write_tsv(data_rows, str(dest), headers=headers)
    assert count_rows(str(dest)) == len(data_rows)


def test_gnumeric_to_tsv_name_column(tmp_path):
    m = load_gnumeric(str(_GNUMERIC_SAMPLES / "multi-cell-basic.gnumeric"))
    headers, data_rows = _gnumeric_to_tsv_rows(m)
    dest = tmp_path / "gnumeric_export.tsv"
    write_tsv(data_rows, str(dest), headers=headers)
    names = get_column(str(dest), "Name")
    assert "Alice" in names


def test_gnumeric_headers_not_empty():
    m = load_gnumeric(str(_GNUMERIC_SAMPLES / "multi-cell-basic.gnumeric"))
    headers, _ = _gnumeric_to_tsv_rows(m)
    assert len(headers) > 0
    assert headers[0] == "Name"


def test_gnumeric_data_rows_not_empty():
    m = load_gnumeric(str(_GNUMERIC_SAMPLES / "multi-cell-basic.gnumeric"))
    _, data_rows = _gnumeric_to_tsv_rows(m)
    assert len(data_rows) >= 1
    assert data_rows[0][0] == "Alice"

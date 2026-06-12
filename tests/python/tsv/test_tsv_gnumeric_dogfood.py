"""
test_tsv_gnumeric_dogfood.py -- TSV dogfood pipeline from Gnumeric data.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-42
Tests: write TSV from Gnumeric-derived data, load headers, get_column,
sort_rows ascending, filter_rows exact match.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    write_gnumeric,
    get_sheet_as_rows,
    load,
)
from src.python.tsv.tsv_parser import (
    write_tsv,
    load_tsv,
    get_headers,
    get_column,
    sort_rows,
    filter_rows,
    count_rows,
)

_SHEETS = [
    {
        "name": "Employees",
        "rows": [
            ["name", "dept", "salary"],
            ["Alice", "eng", "90000"],
            ["Bob", "mkt", "70000"],
            ["Carol", "eng", "85000"],
            ["Dave", "hr", "75000"],
        ],
    }
]
_MODEL = create_gnumeric(_SHEETS)


def _write_tsv_from_gnumeric(tmp_path):
    """Extract gnumeric data and write as TSV."""
    all_rows = get_sheet_as_rows(_MODEL, 0)
    dest = tmp_path / "employees.tsv"
    write_tsv(all_rows, str(dest))
    return dest


def test_tsv_from_gnumeric_has_headers(tmp_path):
    dest = _write_tsv_from_gnumeric(tmp_path)
    headers = get_headers(str(dest))
    assert "name" in headers
    assert "dept" in headers


def test_tsv_from_gnumeric_row_count(tmp_path):
    dest = _write_tsv_from_gnumeric(tmp_path)
    assert count_rows(str(dest)) == 4


def test_tsv_from_gnumeric_get_column(tmp_path):
    dest = _write_tsv_from_gnumeric(tmp_path)
    names = get_column(str(dest), "name")
    assert "Alice" in names
    assert "Bob" in names


def test_tsv_from_gnumeric_sort_ascending(tmp_path):
    dest = _write_tsv_from_gnumeric(tmp_path)
    result = sort_rows(str(dest), "name")
    # sort_rows returns {"headers":..., "rows":...}
    headers = result["headers"]
    name_idx = headers.index("name")
    names = [row[name_idx] for row in result["rows"]]
    assert names[0] == "Alice"
    assert names[-1] == "Dave"


def test_tsv_from_gnumeric_filter_dept(tmp_path):
    dest = _write_tsv_from_gnumeric(tmp_path)
    result = filter_rows(str(dest), "dept", "eng")
    assert result["row_count"] == 2

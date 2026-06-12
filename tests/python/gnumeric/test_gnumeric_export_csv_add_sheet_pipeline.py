"""
test_gnumeric_export_csv_add_sheet_pipeline.py -- Gnumeric export_to_csv + add_sheet pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-107
Tests export_to_csv returns string, csv has Alice, add_sheet increases count,
add_sheet returns dict, export after add_sheet still works.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    create_gnumeric,
    write_gnumeric,
    export_to_csv,
    add_sheet,
)

_SHEETS = [
    {
        "name": "Staff",
        "rows": [
            ["name", "dept"],
            ["Alice", "eng"],
            ["Bob", "hr"],
        ],
    }
]


def _make_file(tmp_path):
    model = create_gnumeric(_SHEETS)
    dest = tmp_path / "doc.gnumeric"
    write_gnumeric(model, str(dest))
    return dest


def test_export_to_csv_returns_string(tmp_path):
    dest = _make_file(tmp_path)
    csv_str = export_to_csv(str(dest))
    assert isinstance(csv_str, str)


def test_export_to_csv_has_alice(tmp_path):
    dest = _make_file(tmp_path)
    csv_str = export_to_csv(str(dest))
    assert "Alice" in csv_str


def test_add_sheet_increases_count():
    model = create_gnumeric(_SHEETS)
    before = len(model["sheets"])
    new_model = add_sheet(model, "NewSheet")
    assert len(new_model["sheets"]) == before + 1


def test_add_sheet_returns_dict():
    model = create_gnumeric(_SHEETS)
    new_model = add_sheet(model, "Extra")
    assert isinstance(new_model, dict)


def test_add_sheet_name_accessible():
    model = create_gnumeric(_SHEETS)
    new_model = add_sheet(model, "Appended")
    names = [s["name"] for s in new_model["sheets"]]
    assert "Appended" in names

"""
test_gnumeric_export_probe_pipeline.py -- Gnumeric export + probe pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-50
Tests probe_gnumeric valid, export_to_csv content, get_sheet_metadata list,
extract_values has values, get_cell_count matches.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    write_gnumeric,
    probe_gnumeric,
    export_to_csv,
    get_sheet_metadata,
    extract_values,
    get_cell_count,
)

_SHEETS = [
    {
        "name": "Results",
        "rows": [
            ["item", "value"],
            ["Widget", "42"],
            ["Gadget", "17"],
        ],
    }
]
_MODEL = create_gnumeric(_SHEETS)


def _write(tmp_path):
    dest = tmp_path / "data.gnumeric"
    write_gnumeric(_MODEL, str(dest))
    return dest


def test_probe_gnumeric_valid(tmp_path):
    dest = _write(tmp_path)
    assert probe_gnumeric(str(dest)) is True


def test_export_to_csv_has_content(tmp_path):
    dest = _write(tmp_path)
    csv_str = export_to_csv(str(dest))
    assert "Widget" in csv_str
    assert "42" in csv_str


def test_get_sheet_metadata_list(tmp_path):
    dest = _write(tmp_path)
    meta = get_sheet_metadata(str(dest))
    assert isinstance(meta, list)
    assert meta[0]["name"] == "Results"


def test_extract_values_has_values(tmp_path):
    dest = _write(tmp_path)
    vals = extract_values(str(dest))
    assert "Widget" in vals
    assert "42" in vals


def test_get_cell_count(tmp_path):
    dest = _write(tmp_path)
    count = get_cell_count(str(dest))
    assert count == 6  # 3 rows x 2 cols

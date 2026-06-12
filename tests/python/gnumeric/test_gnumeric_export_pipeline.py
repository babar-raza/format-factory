"""
test_gnumeric_export_pipeline.py -- Gnumeric export pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-33
Tests export_to_csv (string contains data), export_to_json (parseable),
extract_values (list), get_sheet_metadata (list of dicts),
get_cell_count on file-based source.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    write_gnumeric,
    export_to_csv,
    export_to_json,
    extract_values,
    get_sheet_metadata,
    get_cell_count,
)

_MODEL = create_gnumeric([{
    "name": "Results",
    "rows": [["Name", "Score"], ["Alice", "90"], ["Bob", "70"]],
}])


def _write_gnumeric(tmp_path):
    dest = tmp_path / "data.gnumeric"
    write_gnumeric(_MODEL, str(dest))
    return dest


def test_export_to_csv_contains_data(tmp_path):
    dest = _write_gnumeric(tmp_path)
    csv_str = export_to_csv(str(dest))
    assert "Alice" in csv_str


def test_export_to_json_parseable(tmp_path):
    dest = _write_gnumeric(tmp_path)
    json_str = export_to_json(str(dest))
    data = json.loads(json_str)
    # export_to_json returns a list of sheet dicts
    assert isinstance(data, list)
    assert data[0]["name"] == "Results"


def test_extract_values_list(tmp_path):
    dest = _write_gnumeric(tmp_path)
    vals = extract_values(str(dest))
    assert isinstance(vals, list)
    assert "Alice" in vals


def test_get_sheet_metadata(tmp_path):
    dest = _write_gnumeric(tmp_path)
    meta = get_sheet_metadata(str(dest))
    assert isinstance(meta, list)
    assert meta[0]["name"] == "Results"


def test_get_cell_count(tmp_path):
    dest = _write_gnumeric(tmp_path)
    count = get_cell_count(str(dest))
    assert count == 6  # 3 rows x 2 cols

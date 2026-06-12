"""
test_gnumeric_roundtrip_probe.py -- Gnumeric roundtrip + probe pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-36
Tests probe_gnumeric on written file, get_sheet_count, get_sheet_names,
roundtrip write+reload data integrity, load returns model with sheets key.
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
    get_sheet_count,
    get_sheet_names,
    load,
    get_cell_value,
)

_MODEL = create_gnumeric([{
    "name": "Sheet1",
    "rows": [["X", "Y"], ["1", "2"]],
}])


def _write_gnumeric(tmp_path):
    dest = tmp_path / "data.gnumeric"
    write_gnumeric(_MODEL, str(dest))
    return dest


def test_probe_gnumeric_written_file(tmp_path):
    dest = _write_gnumeric(tmp_path)
    assert probe_gnumeric(str(dest)) is True


def test_get_sheet_count(tmp_path):
    dest = _write_gnumeric(tmp_path)
    assert get_sheet_count(str(dest)) == 1


def test_get_sheet_names(tmp_path):
    dest = _write_gnumeric(tmp_path)
    names = get_sheet_names(str(dest))
    assert "Sheet1" in names


def test_load_returns_model_with_sheets(tmp_path):
    dest = _write_gnumeric(tmp_path)
    model = load(str(dest))
    assert "sheets" in model
    assert len(model["sheets"]) == 1


def test_roundtrip_data_integrity(tmp_path):
    dest = _write_gnumeric(tmp_path)
    model = load(str(dest))
    val = get_cell_value(model, 0, 0, 0)
    assert val == "X"

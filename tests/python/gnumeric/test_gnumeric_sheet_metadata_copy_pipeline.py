"""
test_gnumeric_sheet_metadata_copy_pipeline.py -- Gnumeric get_sheet_metadata + copy_sheet pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-98
Tests get_sheet_metadata returns list, metadata has name keys, copy_sheet increases count,
copy appends with (Copy) suffix, copy preserves original sheets.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    create_gnumeric,
    write_gnumeric,
    load,
    get_sheet_metadata,
    copy_sheet,
)

_SHEETS = [
    {"name": "Sales", "rows": [["Q1", "Q2"], ["100", "200"]]},
    {"name": "Costs", "rows": [["Fixed", "Variable"], ["50", "80"]]},
]


def _make_file(tmp_path):
    model = create_gnumeric(_SHEETS)
    dest = tmp_path / "doc.gnumeric"
    write_gnumeric(model, str(dest))
    return dest


def test_get_sheet_metadata_returns_list(tmp_path):
    dest = _make_file(tmp_path)
    meta = get_sheet_metadata(str(dest))
    assert isinstance(meta, list)


def test_get_sheet_metadata_has_name_keys(tmp_path):
    dest = _make_file(tmp_path)
    meta = get_sheet_metadata(str(dest))
    names = [m["name"] for m in meta]
    assert "Sales" in names
    assert "Costs" in names


def test_copy_sheet_increases_count(tmp_path):
    dest = _make_file(tmp_path)
    model = load(str(dest))
    before = len(model["sheets"])
    new_model = copy_sheet(model, 0)
    assert len(new_model["sheets"]) == before + 1


def test_copy_sheet_appends_copy_suffix(tmp_path):
    dest = _make_file(tmp_path)
    model = load(str(dest))
    new_model = copy_sheet(model, 0)
    names = [s["name"] for s in new_model["sheets"]]
    assert "Sales (Copy)" in names


def test_copy_sheet_preserves_originals(tmp_path):
    dest = _make_file(tmp_path)
    model = load(str(dest))
    new_model = copy_sheet(model, 0)
    names = [s["name"] for s in new_model["sheets"]]
    assert "Sales" in names
    assert "Costs" in names

"""
test_gnumeric_rename_sheet_pipeline.py -- Gnumeric rename sheet pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-65
Tests rename_sheet changes name, get_sheet_by_name returns dict, get_sheet_by_name None,
get_sheet_index int, sheet_names after rename.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    rename_sheet,
    get_sheet_by_name,
    get_sheet_index,
    sheet_names,
)

_SHEETS = [{"name": "Original"}, {"name": "Second"}]


def test_rename_sheet_changes_name():
    model = create_gnumeric(_SHEETS)
    model = rename_sheet(model, 0, "Renamed")
    names = sheet_names(model)
    assert "Renamed" in names
    assert "Original" not in names


def test_get_sheet_by_name_returns_dict():
    model = create_gnumeric(_SHEETS)
    result = get_sheet_by_name(model, "Second")
    assert isinstance(result, dict)


def test_get_sheet_by_name_none():
    model = create_gnumeric(_SHEETS)
    result = get_sheet_by_name(model, "NonExistent")
    assert result is None


def test_get_sheet_index_int():
    model = create_gnumeric(_SHEETS)
    idx = get_sheet_index(model, "Second")
    assert idx == 1


def test_sheet_names_after_rename():
    model = create_gnumeric(_SHEETS)
    model = rename_sheet(model, 1, "NewSecond")
    names = sheet_names(model)
    assert "NewSecond" in names
    assert len(names) == 2

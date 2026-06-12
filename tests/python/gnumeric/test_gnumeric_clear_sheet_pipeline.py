"""
test_gnumeric_clear_sheet_pipeline.py -- Gnumeric clear sheet pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-62
Tests clear_sheet empties grid, get_all_values returns list, clear_sheet + fill_column,
sheet_names list, row_count after clear.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    clear_sheet,
    get_all_values,
    fill_column,
    sheet_names,
    row_count,
)

_SHEETS = [{"name": "Alpha", "rows": [["10", "20"], ["30", "40"], ["50", "60"]]}]


def test_clear_sheet_empties_grid():
    model = create_gnumeric(_SHEETS)
    model = clear_sheet(model, 0)
    vals = get_all_values(model, 0)
    assert vals == []


def test_get_all_values_returns_list():
    model = create_gnumeric(_SHEETS)
    vals = get_all_values(model, 0)
    assert isinstance(vals, list)
    assert len(vals) >= 6


def test_clear_then_fill_column():
    model = create_gnumeric(_SHEETS)
    model = clear_sheet(model, 0)
    model = fill_column(model, 0, 0, ["A", "B", "C"])
    vals = get_all_values(model, 0)
    assert "A" in vals


def test_sheet_names_list():
    model = create_gnumeric(_SHEETS)
    names = sheet_names(model)
    assert isinstance(names, list)
    assert "Alpha" in names


def test_row_count_after_clear():
    model = create_gnumeric(_SHEETS)
    model = clear_sheet(model, 0)
    count = row_count(model, 0)
    assert count == 0

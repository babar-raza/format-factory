"""
test_gnumeric_index_delete_w110_pipeline.py -- Gnumeric get_sheet_index + delete_sheet pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-110
Tests get_sheet_index returns int, correct index, delete_sheet returns dict,
sheet count decreases after delete, deleted sheet name gone.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    get_sheet_index,
    delete_sheet,
    sheet_names,
)

_SHEETS = [{"name": "Alpha"}, {"name": "Beta"}, {"name": "Gamma"}]


def test_get_sheet_index_returns_int():
    model = create_gnumeric(_SHEETS)
    assert isinstance(get_sheet_index(model, "Beta"), int)


def test_get_sheet_index_correct():
    model = create_gnumeric(_SHEETS)
    assert get_sheet_index(model, "Beta") == 1


def test_delete_sheet_returns_dict():
    model = create_gnumeric(_SHEETS)
    result = delete_sheet(model, 0)
    assert isinstance(result, dict)


def test_delete_sheet_count_decreases():
    model = create_gnumeric(_SHEETS)
    result = delete_sheet(model, 0)
    assert len(sheet_names(result)) == 2


def test_deleted_sheet_name_gone():
    model = create_gnumeric(_SHEETS)
    result = delete_sheet(model, 0)
    assert "Alpha" not in sheet_names(result)

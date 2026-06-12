"""
test_gnumeric_row_operations.py -- Gnumeric row operation pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-31
Tests sum_row, get_row, fill_row, clear_sheet, get_row_count on a created model.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    sum_row,
    get_row,
    fill_row,
    clear_sheet,
    get_row_count,
)

_MODEL = create_gnumeric([{
    "name": "Sheet1",
    "rows": [
        ["10", "20", "30"],
        ["5", "15", "25"],
    ],
}])


def test_sum_row_first():
    total = sum_row(_MODEL, 0, 0)
    assert total == 60.0


def test_sum_row_second():
    total = sum_row(_MODEL, 0, 1)
    assert total == 45.0


def test_get_row_values():
    row = get_row(_MODEL, 0, 0)
    assert row[0] == "10"
    assert row[2] == "30"


def test_fill_row_then_get():
    m2 = fill_row(_MODEL, 0, 0, ["100", "200", "300"])
    row = get_row(m2, 0, 0)
    assert row[0] == "100"
    assert row[1] == "200"


def test_clear_sheet_row_count():
    m2 = clear_sheet(_MODEL, 0)
    assert get_row_count(m2, 0) == 0

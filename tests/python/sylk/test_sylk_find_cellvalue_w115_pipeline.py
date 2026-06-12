"""
test_sylk_find_cellvalue_w115_pipeline.py -- SYLK find_rows_by_value + get_cell_value pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-115
Tests find_rows_by_value returns list, finds match, no match empty,
get_cell_value returns correct value, get_cell_value numeric cell.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    find_rows_by_value,
    get_cell_value,
)

_SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"
_SLK = _SAMPLES / "minimal-2x2.slk"


def test_find_rows_by_value_returns_list():
    result = find_rows_by_value(_SLK, "Alpha")
    assert isinstance(result, list)


def test_find_rows_by_value_finds_match():
    result = find_rows_by_value(_SLK, "Alpha")
    assert result == [2]


def test_find_rows_by_value_no_match_empty():
    result = find_rows_by_value(_SLK, "xyzzy_notpresent")
    assert result == []


def test_get_cell_value_returns_string():
    result = get_cell_value(_SLK, 1, 1)
    assert result == "Name"


def test_get_cell_value_numeric():
    result = get_cell_value(_SLK, 2, 2)
    assert result == 42

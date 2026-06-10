"""Tests for gnumeric.gnumeric_codec.sheet_names() — Sprint 12, R152."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, sheet_names


def test_single_sheet_name():
    model = create_gnumeric([{"name": "MySheet"}])
    assert sheet_names(model) == ["MySheet"]


def test_multiple_sheet_names():
    model = create_gnumeric([{"name": "A"}, {"name": "B"}, {"name": "C"}])
    assert sheet_names(model) == ["A", "B", "C"]


def test_empty_workbook():
    model = create_gnumeric([])
    assert sheet_names(model) == []


def test_returns_list():
    model = create_gnumeric([{"name": "X"}])
    assert isinstance(sheet_names(model), list)


def test_order_preserved():
    model = create_gnumeric([{"name": "First"}, {"name": "Second"}])
    names = sheet_names(model)
    assert names[0] == "First"
    assert names[1] == "Second"

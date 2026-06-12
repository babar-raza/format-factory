"""
tests/python/sylk/test_r166_sylk_find_rows.py

Tests for SYLK find_rows_by_value function.

Sprint: FORMAT-FACTORY-BROAD-SELF-HEALING-PRODUCT-ACCELERATION-RNEXT-001
Queue: broad-accel-q-005
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_parser import find_rows_by_value, write_sylk, SylkDocument, SylkCell


def _make_sylk(tmp_path: Path, cells: list[tuple[int, int, object]]) -> Path:
    """Helper: write a minimal SYLK file with given cells [(row, col, value)]."""
    doc = SylkDocument(
        cells=[SylkCell(row=r, col=c, value=v) for r, c, v in cells],
    )
    path = tmp_path / "test.slk"
    write_sylk(doc, path)
    return path


class TestFindRowsByValue:
    def test_finds_string_value(self, tmp_path: Path) -> None:
        path = _make_sylk(tmp_path, [(1, 1, "Alice"), (2, 1, "Bob"), (3, 1, "Alice")])
        rows = find_rows_by_value(path, "Alice")
        assert rows == [1, 3]

    def test_finds_numeric_value(self, tmp_path: Path) -> None:
        path = _make_sylk(tmp_path, [(1, 1, 42.0), (2, 1, 0.0), (3, 1, 42.0)])
        rows = find_rows_by_value(path, 42.0)
        assert rows == [1, 3]

    def test_value_not_found(self, tmp_path: Path) -> None:
        path = _make_sylk(tmp_path, [(1, 1, "hello")])
        rows = find_rows_by_value(path, "world")
        assert rows == []

    def test_returns_sorted_rows(self, tmp_path: Path) -> None:
        path = _make_sylk(tmp_path, [(3, 1, "X"), (1, 2, "X"), (2, 1, "Y")])
        rows = find_rows_by_value(path, "X")
        assert rows == sorted(rows)

    def test_empty_spreadsheet(self, tmp_path: Path) -> None:
        doc = SylkDocument(cells=[])
        path = tmp_path / "empty.slk"
        write_sylk(doc, path)
        rows = find_rows_by_value(path, "anything")
        assert rows == []

    def test_value_in_multiple_columns_same_row(self, tmp_path: Path) -> None:
        # Same value in row 1 columns 1 and 2 — row 1 should appear once
        path = _make_sylk(tmp_path, [(1, 1, "dupe"), (1, 2, "dupe"), (2, 1, "other")])
        rows = find_rows_by_value(path, "dupe")
        assert rows == [1]  # deduplicated

    def test_non_none_value_found(self, tmp_path: Path) -> None:
        # None cells may not persist through SYLK roundtrip; test with string value
        path = _make_sylk(tmp_path, [(1, 1, "present"), (2, 1, "other")])
        rows = find_rows_by_value(path, "present")
        assert rows == [1]

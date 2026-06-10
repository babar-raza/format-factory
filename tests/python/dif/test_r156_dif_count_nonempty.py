"""Tests for DIF count_nonempty_cells — route-aware product pilot.

Sprint: FORMAT-FACTORY-ROUTE-AWARE-PRODUCT-REENTRY-HARDENING-001
Taskcard: ROUTE-REENTRY-009
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    DifCell,
    DifDocument,
    count_nonempty_cells,
    write_dif,
)


def _make_dif(tmp_path: Path, rows: list[list[DifCell]]) -> Path:
    doc = DifDocument(title="test", vectors=len(rows[0]) if rows else 0,
                      tuples=len(rows), rows=rows)
    p = tmp_path / "test.dif"
    write_dif(doc, p)
    return p


class TestCountNonemptyCells:
    def test_all_nonempty(self, tmp_path):
        rows = [
            [DifCell(value=1.0, value_type="numeric"), DifCell(value="hello", value_type="string")],
            [DifCell(value=2.0, value_type="numeric"), DifCell(value="world", value_type="string")],
        ]
        p = _make_dif(tmp_path, rows)
        assert count_nonempty_cells(p) == 4

    def test_some_empty(self, tmp_path):
        rows = [
            [DifCell(value=1.0, value_type="numeric"), DifCell(value=None, value_type="special")],
            [DifCell(value="", value_type="string"), DifCell(value="ok", value_type="string")],
        ]
        p = _make_dif(tmp_path, rows)
        assert count_nonempty_cells(p) == 2

    def test_empty_document(self, tmp_path):
        p = _make_dif(tmp_path, [])
        assert count_nonempty_cells(p) == 0

    def test_single_cell(self, tmp_path):
        rows = [[DifCell(value=42.0, value_type="numeric")]]
        p = _make_dif(tmp_path, rows)
        assert count_nonempty_cells(p) == 1

    def test_boolean_cells_counted(self, tmp_path):
        rows = [
            [DifCell(value=True, value_type="boolean"), DifCell(value=False, value_type="boolean")],
        ]
        p = _make_dif(tmp_path, rows)
        # Both True and False are non-empty (not None, not "")
        assert count_nonempty_cells(p) == 2

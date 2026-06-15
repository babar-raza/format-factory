"""Dogfood: DIF in-memory model analytics pipeline.

Demonstrates: create DIF → write → parse → cell/column/row analytics → verify.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import (
    DifDocument,
    DifCell,
    write_dif,
    parse_dif_strict,
    get_cell_value,
    get_column_count,
    get_title,
    get_all_values,
    count_nonempty_cells,
)


def _make_dif_file(tmp_path: Path) -> Path:
    """Create a DIF file with structured numeric data."""
    doc = DifDocument(
        title="Inventory",
        vectors=4,
        tuples=4,
        rows=[
            [DifCell("Item"), DifCell("Qty"), DifCell("Price"), DifCell("Total")],
            [DifCell("Bolts"), DifCell(100, "numeric"), DifCell(0.50, "numeric"), DifCell(50.0, "numeric")],
            [DifCell("Nuts"), DifCell(200, "numeric"), DifCell(0.25, "numeric"), DifCell(50.0, "numeric")],
            [DifCell("Washers"), DifCell(500, "numeric"), DifCell(0.10, "numeric"), DifCell(50.0, "numeric")],
        ],
    )
    p = tmp_path / "inventory.dif"
    write_dif(doc, str(p))
    return p


class TestDogfoodDifAnalytics:
    @pytest.fixture
    def dif_file(self, tmp_path):
        return _make_dif_file(tmp_path)

    def test_title(self, dif_file):
        """DIF title is preserved after roundtrip."""
        title = get_title(str(dif_file))
        assert title == "Inventory"

    def test_column_count(self, dif_file):
        """Column count matches expected."""
        count = get_column_count(str(dif_file))
        assert count >= 4

    def test_nonempty_cells(self, dif_file):
        """Non-empty cell count is at least 16 (4x4)."""
        count = count_nonempty_cells(str(dif_file))
        assert count >= 16

    def test_cell_value(self, dif_file):
        """Individual cell values are accessible."""
        val = get_cell_value(str(dif_file), 0, 0)
        assert val == "Item"

    def test_all_values(self, dif_file):
        """All values are extractable as a flat list."""
        values = get_all_values(str(dif_file))
        assert isinstance(values, list)
        assert "Bolts" in values or "Bolts" in str(values)
        assert len(values) >= 16

    def test_parse_preserves_structure(self, dif_file):
        """Parse returns a DifDocument with correct structure."""
        doc = parse_dif_strict(str(dif_file))
        assert isinstance(doc, DifDocument)
        assert len(doc.rows) >= 4
        assert doc.title == "Inventory"

    def test_numeric_values_preserved(self, dif_file):
        """Numeric values survive the write/parse roundtrip."""
        doc = parse_dif_strict(str(dif_file))
        # Find a numeric cell (row 1, col 1 should be 100)
        row1 = doc.rows[1]
        qty_cell = row1[1]
        assert float(qty_cell.value) == 100.0

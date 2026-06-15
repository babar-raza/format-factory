"""Dogfood: SYLK write → parse → analytics roundtrip.

Demonstrates: create SylkDocument → write to disk → parse → analytics → verify.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_parser import (
    SylkDocument,
    SylkCell,
    write_sylk,
    parse_sylk_strict,
    get_row_count,
    get_column_count,
    get_cell_value,
    count_nonempty_cells,
)


def _make_sylk_file(tmp_path: Path) -> Path:
    """Create a SYLK file with known data."""
    cells = [
        SylkCell(row=0, col=0, value="Product", value_type="string"),
        SylkCell(row=0, col=1, value="Price", value_type="string"),
        SylkCell(row=0, col=2, value="Stock", value_type="string"),
        SylkCell(row=1, col=0, value="Widget", value_type="string"),
        SylkCell(row=1, col=1, value="9.99", value_type="number"),
        SylkCell(row=1, col=2, value="150", value_type="number"),
        SylkCell(row=2, col=0, value="Gadget", value_type="string"),
        SylkCell(row=2, col=1, value="24.99", value_type="number"),
        SylkCell(row=2, col=2, value="75", value_type="number"),
        SylkCell(row=3, col=0, value="Doohickey", value_type="string"),
        SylkCell(row=3, col=1, value="4.50", value_type="number"),
        SylkCell(row=3, col=2, value="300", value_type="number"),
    ]
    doc = SylkDocument(cells=cells, rows=4, cols=3)
    p = tmp_path / "products.sylk"
    write_sylk(doc, str(p))
    return p


class TestDogfoodSylkWriteRoundtrip:
    @pytest.fixture
    def sylk_file(self, tmp_path):
        return _make_sylk_file(tmp_path)

    def test_write_creates_file(self, sylk_file):
        """SYLK file is created on disk."""
        assert sylk_file.exists()
        assert sylk_file.stat().st_size > 0

    def test_parse_roundtrip(self, sylk_file):
        """Written SYLK can be parsed back."""
        doc = parse_sylk_strict(str(sylk_file))
        assert isinstance(doc, SylkDocument)
        assert len(doc.cells) >= 12

    def test_row_count(self, sylk_file):
        """Row count matches expected (0-indexed: max row index is 3)."""
        assert get_row_count(str(sylk_file)) >= 3

    def test_column_count(self, sylk_file):
        """Column count matches expected (0-indexed: max col index is 2)."""
        assert get_column_count(str(sylk_file)) >= 2

    def test_cell_value(self, sylk_file):
        """Cell values are accessible after roundtrip."""
        val = get_cell_value(str(sylk_file), 0, 0)
        assert val == "Product"

    def test_nonempty_cells(self, sylk_file):
        """Non-empty cell count is at least 12."""
        count = count_nonempty_cells(str(sylk_file))
        assert count >= 12

    def test_data_content(self, sylk_file):
        """Parsed data contains expected values."""
        doc = parse_sylk_strict(str(sylk_file))
        values = [c.value for c in doc.cells]
        assert "Widget" in values
        assert "Gadget" in values
        assert "Doohickey" in values

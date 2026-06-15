"""Dogfood: Gnumeric create → write → load → analytics roundtrip.

Demonstrates: create Gnumeric model → write to disk → reload → run analytics → verify.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import (
    create_gnumeric,
    write_gnumeric,
    load,
    get_sheet_count,
    get_row_count,
    get_column_count,
    get_cell_value,
    count_nonempty_cells,
    gnumeric_cell_count_file,
    gnumeric_column_count_file,
    gnumeric_row_count_file,
)


def _make_gnumeric_file(tmp_path: Path) -> Path:
    """Create a Gnumeric file with known data."""
    model = create_gnumeric([
        {
            "name": "Sales",
            "rows": [
                ["Region", "Q1", "Q2", "Q3"],
                ["North", "100", "120", "130"],
                ["South", "80", "95", "110"],
                ["East", "90", "105", "115"],
            ],
        },
    ])
    p = tmp_path / "sales.gnumeric"
    write_gnumeric(model, str(p))
    return p


class TestDogfoodGnumericRoundtripAnalytics:
    @pytest.fixture
    def gnumeric_file(self, tmp_path):
        return _make_gnumeric_file(tmp_path)

    def test_write_creates_file(self, gnumeric_file):
        """Gnumeric file is created on disk."""
        assert gnumeric_file.exists()
        assert gnumeric_file.stat().st_size > 0

    def test_load_roundtrip(self, gnumeric_file):
        """Written Gnumeric file can be loaded back."""
        model = load(str(gnumeric_file))
        assert isinstance(model, dict)
        assert "sheets" in model

    def test_sheet_count(self, gnumeric_file):
        """Sheet count is 1."""
        assert get_sheet_count(str(gnumeric_file)) == 1

    def test_row_count(self, gnumeric_file):
        """Row count matches expected (4 rows including header)."""
        model = load(str(gnumeric_file))
        assert get_row_count(model, 0) >= 4

    def test_column_count(self, gnumeric_file):
        """Column count matches expected (4 columns)."""
        model = load(str(gnumeric_file))
        assert get_column_count(model, 0) >= 4

    def test_cell_value_header(self, gnumeric_file):
        """Cell values are readable after roundtrip."""
        model = load(str(gnumeric_file))
        val = get_cell_value(model, 0, 0, 0)
        assert val == "Region"

    def test_nonempty_cells(self, gnumeric_file):
        """Non-empty cell count is at least 16 (4x4)."""
        model = load(str(gnumeric_file))
        count = count_nonempty_cells(model, 0)
        assert count >= 16

    def test_file_based_analytics(self, gnumeric_file):
        """File-based analytics work on the created file."""
        cells = gnumeric_cell_count_file(str(gnumeric_file))
        assert cells >= 16
        cols = gnumeric_column_count_file(str(gnumeric_file))
        assert cols >= 4
        rows = gnumeric_row_count_file(str(gnumeric_file))
        assert rows >= 4

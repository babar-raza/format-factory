"""Dogfood export: Gnumeric → CSV using Format Factory Gnumeric library.

Demonstrates: create Gnumeric model in-memory → export to CSV → verify CSV content.
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
    export_to_csv,
    load,
    gnumeric_sheet_summary,
    gnumeric_empty_cell_count,
    gnumeric_numeric_cell_count,
)


class TestDogfoodGnumericCsvExport:
    @pytest.fixture
    def gnumeric_file(self, tmp_path):
        model = create_gnumeric([
            {"name": "Sales", "rows": [
                ["Product", "Q1", "Q2", "Q3", "Q4"],
                ["Widget A", "100", "150", "200", "250"],
                ["Widget B", "80", "120", "160", "200"],
                ["Widget C", "50", "75", "100", "125"],
            ]},
        ])
        p = tmp_path / "sales.gnumeric"
        write_gnumeric(model, str(p))
        return p

    def test_create_and_write_gnumeric(self, gnumeric_file):
        """Gnumeric file can be created and written to disk."""
        assert gnumeric_file.exists()
        assert gnumeric_file.stat().st_size > 0

    def test_load_roundtrip(self, gnumeric_file):
        """Written file can be loaded back."""
        model = load(str(gnumeric_file))
        assert "sheets" in model
        assert len(model["sheets"]) == 1

    def test_export_to_csv(self, gnumeric_file, tmp_path):
        """Export to CSV produces valid CSV output."""
        csv_str = export_to_csv(str(gnumeric_file))
        assert isinstance(csv_str, str)
        lines = csv_str.strip().split("\n")
        assert len(lines) >= 4  # header + 3 data rows

    def test_csv_contains_data(self, gnumeric_file):
        """CSV export contains the expected data."""
        csv_str = export_to_csv(str(gnumeric_file))
        assert "Widget A" in csv_str
        assert "100" in csv_str

    def test_summary_metadata(self, gnumeric_file):
        """Sheet summary returns correct metadata."""
        model = load(str(gnumeric_file))
        summary = gnumeric_sheet_summary(model, 0)
        assert summary["row_count"] >= 4
        assert summary["col_count"] >= 5

    def test_analytics_on_exported_data(self, gnumeric_file):
        """Analytics functions work on dogfood data."""
        model = load(str(gnumeric_file))
        empty = gnumeric_empty_cell_count(model, 0)
        numeric = gnumeric_numeric_cell_count(model, 0)
        assert empty == 0  # no empty cells
        assert numeric >= 12  # 12 numeric cells (Q1-Q4 × 3 products)

    def test_csv_to_file(self, gnumeric_file, tmp_path):
        """Export CSV to file and verify readability."""
        csv_str = export_to_csv(str(gnumeric_file))
        csv_file = tmp_path / "sales.csv"
        csv_file.write_text(csv_str, encoding="utf-8")
        content = csv_file.read_text(encoding="utf-8")
        assert "Widget" in content
        assert csv_file.stat().st_size > 0

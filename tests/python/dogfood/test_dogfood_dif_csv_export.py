"""Dogfood export: DIF → CSV using Format Factory DIF library.

Demonstrates: create DIF document in-memory → write to disk → parse → export to CSV → verify.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.dif_parser import (
    parse_dif_strict,
    write_dif,
    dif_to_csv,
    get_row_count,
    get_column_count,
    count_nonempty_cells,
    DifDocument,
    DifCell,
)


def _make_dif_file(tmp_path: Path) -> Path:
    """Create a small DIF file with known data."""
    doc = DifDocument(
        title="TestExport",
        vectors=3,
        tuples=4,
        rows=[
            [DifCell("Name"), DifCell("Score"), DifCell("Grade")],
            [DifCell("Alice"), DifCell(95, "numeric"), DifCell("A")],
            [DifCell("Bob"), DifCell(82, "numeric"), DifCell("B")],
            [DifCell("Carol"), DifCell(78, "numeric"), DifCell("C")],
        ],
    )
    p = tmp_path / "export_test.dif"
    write_dif(doc, str(p))
    return p


class TestDogfoodDifCsvExport:
    @pytest.fixture
    def dif_file(self, tmp_path):
        return _make_dif_file(tmp_path)

    def test_write_creates_file(self, dif_file):
        """DIF file is created on disk."""
        assert dif_file.exists()
        assert dif_file.stat().st_size > 0

    def test_parse_roundtrip(self, dif_file):
        """Written DIF file can be parsed back."""
        doc = parse_dif_strict(str(dif_file))
        assert isinstance(doc, DifDocument)
        assert len(doc.rows) >= 3

    def test_export_to_csv(self, dif_file):
        """DIF → CSV export produces valid CSV output."""
        csv_str = dif_to_csv(str(dif_file))
        assert isinstance(csv_str, str)
        lines = csv_str.strip().split("\n")
        assert len(lines) >= 4  # header + 3 data rows

    def test_csv_contains_data(self, dif_file):
        """CSV export contains the expected data values."""
        csv_str = dif_to_csv(str(dif_file))
        assert "Alice" in csv_str
        assert "95" in csv_str
        assert "Carol" in csv_str

    def test_analytics_on_dif_data(self, dif_file):
        """Analytics work on the dogfood DIF document."""
        doc = parse_dif_strict(str(dif_file))
        assert len(doc.rows) >= 4
        assert doc.vectors >= 3
        assert count_nonempty_cells(str(dif_file)) >= 12

    def test_csv_to_file(self, dif_file, tmp_path):
        """Export CSV to file and verify readability."""
        csv_str = dif_to_csv(str(dif_file))
        csv_file = tmp_path / "export.csv"
        csv_file.write_text(csv_str, encoding="utf-8")
        content = csv_file.read_text(encoding="utf-8")
        assert "Alice" in content
        assert csv_file.stat().st_size > 0

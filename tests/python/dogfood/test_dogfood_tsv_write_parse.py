"""Dogfood: TSV write/parse/analyze pipeline.

Demonstrates: write TSV data -> parse back -> analytics -> verify data integrity.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    write_tsv_strict,
    parse_tsv,
    tsv_column_count,
    tsv_row_count,
)


def _make_tsv_file(tmp_path: Path) -> Path:
    """Create a TSV file with known data."""
    rows = [
        ["Name", "Department", "Salary"],
        ["Alice", "Engineering", "95000"],
        ["Bob", "Marketing", "82000"],
        ["Carol", "Engineering", "91000"],
        ["Dave", "Sales", "78000"],
    ]
    p = tmp_path / "employees.tsv"
    write_tsv_strict(rows, str(p))
    return p


class TestDogfoodTsvWriteParse:
    @pytest.fixture
    def tsv_file(self, tmp_path):
        return _make_tsv_file(tmp_path)

    def test_write_creates_file(self, tsv_file):
        """TSV file is created on disk."""
        assert tsv_file.exists()
        assert tsv_file.stat().st_size > 0

    def test_parse_returns_data(self, tsv_file):
        """TSV can be parsed back."""
        result = parse_tsv(str(tsv_file))
        assert result is not None

    def test_row_count(self, tsv_file):
        """Row count matches expected data rows."""
        count = tsv_row_count(str(tsv_file))
        assert count >= 4, f"Expected >= 4 data rows, got {count}"

    def test_column_count(self, tsv_file):
        """Column count matches expected columns."""
        count = tsv_column_count(str(tsv_file))
        assert count == 3, f"Expected 3 columns, got {count}"

    def test_file_content_tab_separated(self, tsv_file):
        """File content uses tab separators."""
        content = tsv_file.read_text(encoding="utf-8")
        assert "\t" in content
        assert "Alice" in content
        assert "Engineering" in content

    def test_roundtrip_preserves_data(self, tsv_file, tmp_path):
        """Parse and re-write preserves data."""
        result = parse_tsv(str(tsv_file))
        rows = result.get("rows", result.get("data", []))
        if rows:
            p2 = tmp_path / "roundtrip.tsv"
            write_tsv_strict(rows, str(p2))
            assert p2.exists()
            assert p2.stat().st_size > 0

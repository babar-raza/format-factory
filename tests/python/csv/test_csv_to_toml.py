"""
Tests for csv_to_toml dogfood export.

Verifies that CSV rows are converted to TOML array table entries using
Format Factory's CSV parser and TOML writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"

from src.python.csv.csv_to_toml import csv_to_toml


class TestCsvToTomlBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.toml"
        count = csv_to_toml(MINIMAL_CSV, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .toml file is created at the specified path."""
        dest = tmp_path / "out.toml"
        csv_to_toml(MINIMAL_CSV, dest)
        assert dest.exists()

    def test_output_has_content(self, tmp_path: Path) -> None:
        """Output file has content."""
        dest = tmp_path / "out.toml"
        csv_to_toml(MINIMAL_CSV, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content) > 5

    def test_produces_rows(self, tmp_path: Path) -> None:
        """CSV rows appear in TOML output."""
        dest = tmp_path / "out.toml"
        count = csv_to_toml(MINIMAL_CSV, dest)
        assert count >= 1


class TestCsvToTomlOptions:
    """Option flag tests."""

    def test_custom_table_key(self, tmp_path: Path) -> None:
        """table_key parameter sets the TOML array table name."""
        dest = tmp_path / "out.toml"
        csv_to_toml(MINIMAL_CSV, dest, table_key="data")
        content = dest.read_text(encoding="utf-8")
        assert "data" in content


class TestCsvToTomlPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.toml"
        csv_to_toml(MINIMAL_CSV, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.toml"
        count = csv_to_toml(str(MINIMAL_CSV), str(dest))
        assert isinstance(count, int) and dest.exists()

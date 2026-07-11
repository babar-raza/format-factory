"""
Tests for csv_to_abw dogfood export.

Verifies that CSV rows are converted to ABW paragraphs using
Format Factory's CSV parser and ABW writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_CSV = _REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv"

from src.python.csv.csv_to_abw import csv_to_abw


class TestCsvToAbwBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        count = csv_to_abw(MINIMAL_CSV, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        csv_to_abw(MINIMAL_CSV, dest)
        assert dest.exists()

    def test_produces_rows(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        count = csv_to_abw(MINIMAL_CSV, dest)
        assert count >= 1

    def test_output_is_xml(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        csv_to_abw(MINIMAL_CSV, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<abiword" in content or "<?xml" in content


class TestCsvToAbwPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.abw"
        csv_to_abw(MINIMAL_CSV, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        count = csv_to_abw(str(MINIMAL_CSV), str(dest))
        assert isinstance(count, int) and dest.exists()

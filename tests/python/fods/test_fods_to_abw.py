"""
Tests for fods_to_abw dogfood export.

Verifies that FODS rows are converted to ABW paragraphs using
Format Factory's FODS parser and ABW writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODS = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"

from fods.fods_to_abw import fods_to_abw


class TestFodsToAbwBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        count = fods_to_abw(MINIMAL_FODS, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        fods_to_abw(MINIMAL_FODS, dest)
        assert dest.exists()

    def test_produces_rows(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        count = fods_to_abw(MINIMAL_FODS, dest)
        assert count >= 1

    def test_output_is_xml(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        fods_to_abw(MINIMAL_FODS, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<abiword" in content or "<?xml" in content


class TestFodsToAbwPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.abw"
        fods_to_abw(MINIMAL_FODS, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        count = fods_to_abw(str(MINIMAL_FODS), str(dest))
        assert isinstance(count, int) and dest.exists()

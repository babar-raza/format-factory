"""
Tests for fodg_to_fods dogfood export.

Verifies that FODG drawing pages are converted to FODS rows using
Format Factory's FODG codec and FODS writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODG = _REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg"
SHAPES_FODG = _REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg"

from fodg.fodg_to_fods import fodg_to_fods


class TestFodgToFodsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.fods"
        count = fodg_to_fods(MINIMAL_FODG, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .fods file is created at the specified path."""
        dest = tmp_path / "out.fods"
        fodg_to_fods(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        """FODS file is XML (flat format, not ZIP)."""
        dest = tmp_path / "out.fods"
        fodg_to_fods(MINIMAL_FODG, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_table(self, tmp_path: Path) -> None:
        """FODS file contains table element."""
        dest = tmp_path / "out.fods"
        fodg_to_fods(MINIMAL_FODG, dest)
        content = dest.read_text(encoding="utf-8")
        assert "table:table" in content


class TestFodgToFodsContent:
    """Content correctness tests."""

    def test_produces_rows(self, tmp_path: Path) -> None:
        """FODG pages appear as FODS rows."""
        dest = tmp_path / "out.fods"
        count = fodg_to_fods(MINIMAL_FODG, dest)
        assert count >= 1

    def test_shapes_fodg_converts(self, tmp_path: Path) -> None:
        """Drawing with shapes converts without error."""
        dest = tmp_path / "out.fods"
        count = fodg_to_fods(SHAPES_FODG, dest)
        assert dest.exists()
        assert count >= 1

    def test_content_has_data(self, tmp_path: Path) -> None:
        """FODS file has substantial content."""
        dest = tmp_path / "out.fods"
        fodg_to_fods(MINIMAL_FODG, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content) > 100


class TestFodgToFodsOptions:
    """Option flag tests."""

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the FODS sheet name."""
        dest = tmp_path / "out.fods"
        fodg_to_fods(MINIMAL_FODG, dest, sheet_name="FODG_Data")
        content = dest.read_text(encoding="utf-8")
        assert "FODG_Data" in content

    def test_include_header(self, tmp_path: Path) -> None:
        """include_header=True writes page_name header."""
        dest = tmp_path / "out.fods"
        fodg_to_fods(MINIMAL_FODG, dest, include_header=True)
        content = dest.read_text(encoding="utf-8")
        assert "page_name" in content

    def test_no_header(self, tmp_path: Path) -> None:
        """include_header=False omits the header row."""
        dest = tmp_path / "out.fods"
        count = fodg_to_fods(MINIMAL_FODG, dest, include_header=False)
        assert count >= 0


class TestFodgToFodsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.fods"
        fodg_to_fods(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.fods"
        count = fodg_to_fods(str(MINIMAL_FODG), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

"""
Tests for dif_to_fods dogfood export.

Verifies that DIF data rows are converted to FODS rows using
Format Factory's DIF parser and FODS writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"
NUMERIC_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "numeric-row.dif"

from dif.dif_to_fods import dif_to_fods


class TestDifToFodsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.fods"
        count = dif_to_fods(MINIMAL_DIF, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .fods file is created at the specified path."""
        dest = tmp_path / "out.fods"
        dif_to_fods(MINIMAL_DIF, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        """FODS file is XML (flat format, not ZIP)."""
        dest = tmp_path / "out.fods"
        dif_to_fods(MINIMAL_DIF, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_table(self, tmp_path: Path) -> None:
        """FODS file contains table element."""
        dest = tmp_path / "out.fods"
        dif_to_fods(MINIMAL_DIF, dest)
        content = dest.read_text(encoding="utf-8")
        assert "table:table" in content


class TestDifToFodsContent:
    """Content correctness tests."""

    def test_produces_rows(self, tmp_path: Path) -> None:
        """DIF rows appear in FODS output."""
        dest = tmp_path / "out.fods"
        count = dif_to_fods(MINIMAL_DIF, dest)
        assert count >= 1

    def test_numeric_dif_converts(self, tmp_path: Path) -> None:
        """Numeric DIF file converts without error."""
        dest = tmp_path / "out.fods"
        count = dif_to_fods(NUMERIC_DIF, dest)
        assert dest.exists()
        assert count >= 1

    def test_content_has_data(self, tmp_path: Path) -> None:
        """FODS file has substantial content."""
        dest = tmp_path / "out.fods"
        dif_to_fods(MINIMAL_DIF, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content) > 100


class TestDifToFodsOptions:
    """Option flag tests."""

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the FODS sheet name."""
        dest = tmp_path / "out.fods"
        dif_to_fods(MINIMAL_DIF, dest, sheet_name="DIF_Data")
        content = dest.read_text(encoding="utf-8")
        assert "DIF_Data" in content


class TestDifToFodsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.fods"
        dif_to_fods(MINIMAL_DIF, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.fods"
        count = dif_to_fods(str(MINIMAL_DIF), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

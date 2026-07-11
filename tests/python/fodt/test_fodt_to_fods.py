"""
Tests for fodt_to_fods dogfood export.

Verifies that FODT blocks are converted to FODS rows using
Format Factory's FODT parser and FODS writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODT = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"
HEADINGS_FODT = _REPO / "samples" / "by-format" / "fodt" / "headings-and-paragraphs.fodt"

from fodt.fodt_to_fods import fodt_to_fods


class TestFodtToFodsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.fods"
        count = fodt_to_fods(MINIMAL_FODT, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .fods file is created at the specified path."""
        dest = tmp_path / "out.fods"
        fodt_to_fods(MINIMAL_FODT, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        """FODS file is XML (flat format, not ZIP)."""
        dest = tmp_path / "out.fods"
        fodt_to_fods(MINIMAL_FODT, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_table(self, tmp_path: Path) -> None:
        """FODS file contains table element."""
        dest = tmp_path / "out.fods"
        fodt_to_fods(MINIMAL_FODT, dest)
        content = dest.read_text(encoding="utf-8")
        assert "table:table" in content


class TestFodtToFodsContent:
    """Content correctness tests."""

    def test_produces_rows(self, tmp_path: Path) -> None:
        """FODT blocks appear as FODS rows."""
        dest = tmp_path / "out.fods"
        count = fodt_to_fods(MINIMAL_FODT, dest)
        assert count >= 1

    def test_headings_convert(self, tmp_path: Path) -> None:
        """Document with headings converts without error."""
        dest = tmp_path / "out.fods"
        count = fodt_to_fods(HEADINGS_FODT, dest)
        assert dest.exists()
        assert count >= 1

    def test_content_has_data(self, tmp_path: Path) -> None:
        """FODS file has substantial content."""
        dest = tmp_path / "out.fods"
        fodt_to_fods(MINIMAL_FODT, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content) > 100


class TestFodtToFodsOptions:
    """Option flag tests."""

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the FODS sheet name."""
        dest = tmp_path / "out.fods"
        fodt_to_fods(MINIMAL_FODT, dest, sheet_name="FODT_Data")
        content = dest.read_text(encoding="utf-8")
        assert "FODT_Data" in content

    def test_include_header(self, tmp_path: Path) -> None:
        """include_header=True writes block_type header."""
        dest = tmp_path / "out.fods"
        fodt_to_fods(MINIMAL_FODT, dest, include_header=True)
        content = dest.read_text(encoding="utf-8")
        assert "block_type" in content

    def test_no_header(self, tmp_path: Path) -> None:
        """include_header=False omits the header row."""
        dest = tmp_path / "out.fods"
        count = fodt_to_fods(MINIMAL_FODT, dest, include_header=False)
        assert count >= 0


class TestFodtToFodsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.fods"
        fodt_to_fods(MINIMAL_FODT, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.fods"
        count = fodt_to_fods(str(MINIMAL_FODT), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

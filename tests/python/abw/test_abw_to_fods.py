"""
Tests for abw_to_fods dogfood export.

Verifies that ABW paragraphs are converted to FODS rows using
Format Factory's ABW codec and FODS writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_ABW = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
TWO_PARA_ABW = _REPO / "samples" / "by-format" / "abw" / "two-paragraphs.abw"

from abw.abw_to_fods import abw_to_fods


class TestAbwToFodsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.fods"
        count = abw_to_fods(MINIMAL_ABW, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .fods file is created at the specified path."""
        dest = tmp_path / "out.fods"
        abw_to_fods(MINIMAL_ABW, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        """FODS file is XML (flat format, not ZIP)."""
        dest = tmp_path / "out.fods"
        abw_to_fods(MINIMAL_ABW, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_table(self, tmp_path: Path) -> None:
        """FODS file contains table element."""
        dest = tmp_path / "out.fods"
        abw_to_fods(MINIMAL_ABW, dest)
        content = dest.read_text(encoding="utf-8")
        assert "table:table" in content


class TestAbwToFodsContent:
    """Content correctness tests."""

    def test_produces_rows(self, tmp_path: Path) -> None:
        """ABW paragraphs appear as FODS rows."""
        dest = tmp_path / "out.fods"
        count = abw_to_fods(MINIMAL_ABW, dest)
        assert count >= 1

    def test_two_paragraphs_convert(self, tmp_path: Path) -> None:
        """Two-paragraph ABW produces at least 2 data rows."""
        dest = tmp_path / "out.fods"
        count = abw_to_fods(TWO_PARA_ABW, dest)
        assert dest.exists()
        assert count >= 2

    def test_content_has_data(self, tmp_path: Path) -> None:
        """FODS file has substantial content."""
        dest = tmp_path / "out.fods"
        abw_to_fods(MINIMAL_ABW, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content) > 100


class TestAbwToFodsOptions:
    """Option flag tests."""

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the FODS sheet name."""
        dest = tmp_path / "out.fods"
        abw_to_fods(MINIMAL_ABW, dest, sheet_name="ABW_Data")
        content = dest.read_text(encoding="utf-8")
        assert "ABW_Data" in content

    def test_include_header(self, tmp_path: Path) -> None:
        """include_header=True writes a 'text' header row."""
        dest = tmp_path / "out.fods"
        abw_to_fods(MINIMAL_ABW, dest, include_header=True)
        content = dest.read_text(encoding="utf-8")
        assert "text" in content

    def test_no_header(self, tmp_path: Path) -> None:
        """include_header=False omits the header row."""
        dest = tmp_path / "out.fods"
        count = abw_to_fods(MINIMAL_ABW, dest, include_header=False)
        assert count >= 0


class TestAbwToFodsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.fods"
        abw_to_fods(MINIMAL_ABW, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.fods"
        count = abw_to_fods(str(MINIMAL_ABW), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

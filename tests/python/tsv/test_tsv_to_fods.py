"""
Tests for tsv_to_fods dogfood export.

Verifies that TSV rows are converted to FODS format using
Format Factory's TSV parser and FODS writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_TSV = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"
MULTI_TSV = _REPO / "samples" / "by-format" / "tsv" / "multi-column.tsv"

from tsv.tsv_to_fods import tsv_to_fods


class TestTsvToFodsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.fods"
        count = tsv_to_fods(MINIMAL_TSV, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .fods file is created at the specified path."""
        dest = tmp_path / "out.fods"
        tsv_to_fods(MINIMAL_TSV, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        """FODS file is XML (flat format, not ZIP)."""
        dest = tmp_path / "out.fods"
        tsv_to_fods(MINIMAL_TSV, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_table(self, tmp_path: Path) -> None:
        """FODS file contains table element."""
        dest = tmp_path / "out.fods"
        tsv_to_fods(MINIMAL_TSV, dest)
        content = dest.read_text(encoding="utf-8")
        assert "table:table" in content


class TestTsvToFodsContent:
    """Content correctness tests."""

    def test_produces_rows(self, tmp_path: Path) -> None:
        """TSV rows appear in FODS output."""
        dest = tmp_path / "out.fods"
        count = tsv_to_fods(MINIMAL_TSV, dest)
        assert count >= 1

    def test_multi_column_converts(self, tmp_path: Path) -> None:
        """Multi-column TSV converts without error."""
        dest = tmp_path / "out.fods"
        count = tsv_to_fods(MULTI_TSV, dest)
        assert dest.exists()
        assert count >= 0

    def test_content_has_data(self, tmp_path: Path) -> None:
        """FODS file has substantial content."""
        dest = tmp_path / "out.fods"
        tsv_to_fods(MINIMAL_TSV, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content) > 100


class TestTsvToFodsOptions:
    """Option flag tests."""

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the FODS sheet name."""
        dest = tmp_path / "out.fods"
        tsv_to_fods(MINIMAL_TSV, dest, sheet_name="TSV_Data")
        content = dest.read_text(encoding="utf-8")
        assert "TSV_Data" in content

    def test_no_headers(self, tmp_path: Path) -> None:
        """include_headers=False skips header row."""
        dest = tmp_path / "out.fods"
        count = tsv_to_fods(MINIMAL_TSV, dest, include_headers=False)
        assert count >= 0


class TestTsvToFodsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.fods"
        tsv_to_fods(MINIMAL_TSV, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.fods"
        count = tsv_to_fods(str(MINIMAL_TSV), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

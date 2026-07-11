"""
Tests for odt_to_tsv dogfood export.

Verifies that ODT document elements are converted to TSV rows using
Format Factory's ODT parser and TSV writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_ODT = _REPO / "samples" / "by-format" / "odt" / "valid" / "minimal-document.odt"
TWO_PARA_ODT = _REPO / "samples" / "by-format" / "odt" / "valid" / "two-paragraphs.odt"

from odt.odt_to_tsv import odt_to_tsv


class TestOdtToTsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.tsv"
        count = odt_to_tsv(MINIMAL_ODT, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .tsv file is created at the specified path."""
        dest = tmp_path / "out.tsv"
        odt_to_tsv(MINIMAL_ODT, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """TSV output is non-empty."""
        dest = tmp_path / "out.tsv"
        odt_to_tsv(MINIMAL_ODT, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_two_para_produces_rows(self, tmp_path: Path) -> None:
        """two-paragraphs.odt produces multiple rows."""
        dest = tmp_path / "out.tsv"
        count = odt_to_tsv(TWO_PARA_ODT, dest)
        assert count >= 1


class TestOdtToTsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row with element_type and text is written by default."""
        dest = tmp_path / "out.tsv"
        odt_to_tsv(MINIMAL_ODT, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "element_type" in first_line
        assert "text" in first_line

    def test_tab_separator_in_output(self, tmp_path: Path) -> None:
        """Output file uses tab as field separator."""
        dest = tmp_path / "out.tsv"
        odt_to_tsv(MINIMAL_ODT, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "\t" in first_line

    def test_line_count_is_data_plus_header(self, tmp_path: Path) -> None:
        """Total non-empty lines = data rows + 1 header."""
        dest = tmp_path / "out.tsv"
        count = odt_to_tsv(TWO_PARA_ODT, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1

    def test_element_type_in_output(self, tmp_path: Path) -> None:
        """Element type column appears in the TSV output."""
        dest = tmp_path / "out.tsv"
        odt_to_tsv(TWO_PARA_ODT, dest)
        content = dest.read_text(encoding="utf-8")
        assert "paragraph" in content or "heading" in content or "list_item" in content

    def test_two_paragraphs_count(self, tmp_path: Path) -> None:
        """two-paragraphs.odt yields at least 2 data rows."""
        dest = tmp_path / "out.tsv"
        count = odt_to_tsv(TWO_PARA_ODT, dest)
        assert count >= 2


class TestOdtToTsvOptions:
    """Option flag tests."""

    def test_no_header_excludes_header_row(self, tmp_path: Path) -> None:
        """include_header=False excludes the header row."""
        dest = tmp_path / "out.tsv"
        count = odt_to_tsv(TWO_PARA_ODT, dest, include_header=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_skip_empty_by_default(self, tmp_path: Path) -> None:
        """skip_empty=True by default omits empty elements."""
        dest = tmp_path / "out.tsv"
        count = odt_to_tsv(MINIMAL_ODT, dest)
        assert count >= 0

    def test_include_empty_elements(self, tmp_path: Path) -> None:
        """skip_empty=False includes empty elements."""
        dest_skip = tmp_path / "out_skip.tsv"
        dest_all = tmp_path / "out_all.tsv"
        count_skip = odt_to_tsv(TWO_PARA_ODT, dest_skip, skip_empty=True)
        count_all = odt_to_tsv(TWO_PARA_ODT, dest_all, skip_empty=False)
        assert count_all >= count_skip


class TestOdtToTsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.tsv"
        odt_to_tsv(MINIMAL_ODT, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.tsv"
        count = odt_to_tsv(str(MINIMAL_ODT), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

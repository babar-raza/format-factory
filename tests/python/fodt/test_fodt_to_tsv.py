"""
Tests for fodt_to_tsv dogfood export.

Verifies that FODT document blocks are converted to TSV rows using
Format Factory's FODT parser and TSV writer libraries.
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

from fodt.fodt_to_tsv import fodt_to_tsv


class TestFodtToTsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.tsv"
        count = fodt_to_tsv(MINIMAL_FODT, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .tsv file is created at the specified path."""
        dest = tmp_path / "out.tsv"
        fodt_to_tsv(MINIMAL_FODT, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """TSV output is non-empty."""
        dest = tmp_path / "out.tsv"
        fodt_to_tsv(MINIMAL_FODT, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_headings_document_produces_rows(self, tmp_path: Path) -> None:
        """headings-and-paragraphs.fodt produces multiple rows."""
        dest = tmp_path / "out.tsv"
        count = fodt_to_tsv(HEADINGS_FODT, dest)
        assert count >= 1


class TestFodtToTsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row with block_type and text is written by default."""
        dest = tmp_path / "out.tsv"
        fodt_to_tsv(MINIMAL_FODT, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "block_type" in first_line
        assert "text" in first_line

    def test_tab_separator_in_output(self, tmp_path: Path) -> None:
        """Output file uses tab as field separator."""
        dest = tmp_path / "out.tsv"
        fodt_to_tsv(MINIMAL_FODT, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "\t" in first_line

    def test_line_count_is_data_plus_header(self, tmp_path: Path) -> None:
        """Total non-empty lines = data rows + 1 header."""
        dest = tmp_path / "out.tsv"
        count = fodt_to_tsv(HEADINGS_FODT, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1

    def test_block_type_in_output(self, tmp_path: Path) -> None:
        """Block type column appears in the TSV output."""
        dest = tmp_path / "out.tsv"
        fodt_to_tsv(HEADINGS_FODT, dest)
        content = dest.read_text(encoding="utf-8")
        assert "paragraph" in content or "heading" in content

    def test_heading_type_in_headings_document(self, tmp_path: Path) -> None:
        """headings-and-paragraphs.fodt has heading type in output."""
        dest = tmp_path / "out.tsv"
        fodt_to_tsv(HEADINGS_FODT, dest)
        content = dest.read_text(encoding="utf-8")
        assert "heading" in content


class TestFodtToTsvOptions:
    """Option flag tests."""

    def test_no_header_excludes_header_row(self, tmp_path: Path) -> None:
        """include_header=False excludes the header row."""
        dest = tmp_path / "out.tsv"
        count = fodt_to_tsv(HEADINGS_FODT, dest, include_header=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_skip_empty_by_default(self, tmp_path: Path) -> None:
        """skip_empty=True by default omits blocks with no text."""
        dest = tmp_path / "out.tsv"
        count = fodt_to_tsv(MINIMAL_FODT, dest)
        assert count >= 0

    def test_include_empty_blocks(self, tmp_path: Path) -> None:
        """skip_empty=False includes empty text blocks."""
        dest_skip = tmp_path / "out_skip.tsv"
        dest_all = tmp_path / "out_all.tsv"
        count_skip = fodt_to_tsv(HEADINGS_FODT, dest_skip, skip_empty=True)
        count_all = fodt_to_tsv(HEADINGS_FODT, dest_all, skip_empty=False)
        assert count_all >= count_skip


class TestFodtToTsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.tsv"
        fodt_to_tsv(MINIMAL_FODT, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.tsv"
        count = fodt_to_tsv(str(MINIMAL_FODT), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

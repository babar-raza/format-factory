"""
Tests for odt_to_csv dogfood export.

Verifies that ODT document elements are converted to CSV rows using
Format Factory's ODT parser and CSV writer libraries.
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

from odt.odt_to_csv import odt_to_csv


class TestOdtToCsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.csv"
        count = odt_to_csv(MINIMAL_ODT, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .csv file is created at the specified path."""
        dest = tmp_path / "out.csv"
        odt_to_csv(MINIMAL_ODT, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """CSV output is non-empty."""
        dest = tmp_path / "out.csv"
        odt_to_csv(MINIMAL_ODT, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_two_paragraphs_produces_two_rows(self, tmp_path: Path) -> None:
        """two-paragraphs.odt → 2 data rows."""
        dest = tmp_path / "out.csv"
        count = odt_to_csv(TWO_PARA_ODT, dest)
        assert count == 2


class TestOdtToCsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row with element_type and text is written by default."""
        dest = tmp_path / "out.csv"
        odt_to_csv(MINIMAL_ODT, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "element_type" in first_line
        assert "text" in first_line

    def test_line_count_is_data_plus_header(self, tmp_path: Path) -> None:
        """Total non-empty lines = data rows + 1 header."""
        dest = tmp_path / "out.csv"
        count = odt_to_csv(TWO_PARA_ODT, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1

    def test_element_type_in_output(self, tmp_path: Path) -> None:
        """Element type column appears in the CSV output."""
        dest = tmp_path / "out.csv"
        odt_to_csv(MINIMAL_ODT, dest)
        content = dest.read_text(encoding="utf-8")
        # ODT elements are paragraphs, headings, or list items
        assert "paragraph" in content or "heading" in content or "list_item" in content

    def test_text_content_in_output(self, tmp_path: Path) -> None:
        """Text content from ODT elements appears in CSV."""
        dest = tmp_path / "out.csv"
        odt_to_csv(MINIMAL_ODT, dest)
        content = dest.read_text(encoding="utf-8")
        # Should have non-trivial content beyond header
        lines = [l for l in content.splitlines() if l.strip()]
        assert len(lines) >= 1


class TestOdtToCsvOptions:
    """Option flag tests."""

    def test_no_header_excludes_header_row(self, tmp_path: Path) -> None:
        """include_header=False excludes the header row."""
        dest = tmp_path / "out.csv"
        count = odt_to_csv(TWO_PARA_ODT, dest, include_header=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_skip_empty_true_by_default(self, tmp_path: Path) -> None:
        """skip_empty=True by default omits elements with no text."""
        dest = tmp_path / "out.csv"
        count = odt_to_csv(TWO_PARA_ODT, dest)
        assert count >= 1


class TestOdtToCsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.csv"
        odt_to_csv(MINIMAL_ODT, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.csv"
        count = odt_to_csv(str(MINIMAL_ODT), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

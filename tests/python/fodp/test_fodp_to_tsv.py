"""
Tests for fodp_to_tsv dogfood export.

Verifies that FODP presentation slides are converted to TSV rows using
Format Factory's FODP codec and TSV writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODP = _REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp"
TWO_SLIDES_FODP = _REPO / "samples" / "by-format" / "fodp" / "two-slides-basic.fodp"

from fodp.fodp_to_tsv import fodp_to_tsv


class TestFodpToTsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.tsv"
        count = fodp_to_tsv(MINIMAL_FODP, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .tsv file is created at the specified path."""
        dest = tmp_path / "out.tsv"
        fodp_to_tsv(MINIMAL_FODP, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """TSV output is non-empty."""
        dest = tmp_path / "out.tsv"
        fodp_to_tsv(MINIMAL_FODP, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_two_slides_produces_two_rows(self, tmp_path: Path) -> None:
        """two-slides-basic.fodp produces two data rows."""
        dest = tmp_path / "out.tsv"
        count = fodp_to_tsv(TWO_SLIDES_FODP, dest)
        assert count == 2


class TestFodpToTsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row with slide_name, title, text_content is written by default."""
        dest = tmp_path / "out.tsv"
        fodp_to_tsv(MINIMAL_FODP, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "slide_name" in first_line
        assert "text_content" in first_line

    def test_tab_separator_in_output(self, tmp_path: Path) -> None:
        """Output file uses tab as field separator."""
        dest = tmp_path / "out.tsv"
        fodp_to_tsv(MINIMAL_FODP, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "\t" in first_line

    def test_line_count_is_data_plus_header(self, tmp_path: Path) -> None:
        """Total non-empty lines = slide count + 1 header."""
        dest = tmp_path / "out.tsv"
        count = fodp_to_tsv(TWO_SLIDES_FODP, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1

    def test_three_columns_by_default(self, tmp_path: Path) -> None:
        """Default output has 3 tab-separated columns per row."""
        dest = tmp_path / "out.tsv"
        fodp_to_tsv(MINIMAL_FODP, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert first_line.count("\t") == 2


class TestFodpToTsvOptions:
    """Option flag tests."""

    def test_no_header_excludes_header_row(self, tmp_path: Path) -> None:
        """include_header=False excludes the header row."""
        dest = tmp_path / "out.tsv"
        count = fodp_to_tsv(TWO_SLIDES_FODP, dest, include_header=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_include_slide_index_adds_column(self, tmp_path: Path) -> None:
        """include_slide_index=True adds a slide_index column."""
        dest = tmp_path / "out.tsv"
        fodp_to_tsv(MINIMAL_FODP, dest, include_slide_index=True)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "slide_index" in first_line
        assert first_line.count("\t") == 3

    def test_slide_index_values_are_sequential(self, tmp_path: Path) -> None:
        """Slide index values are 0-based sequential integers."""
        dest = tmp_path / "out.tsv"
        fodp_to_tsv(TWO_SLIDES_FODP, dest, include_slide_index=True)
        lines = dest.read_text(encoding="utf-8").splitlines()
        # data rows start at index 1 (after header)
        first_idx = lines[1].split("\t")[0]
        second_idx = lines[2].split("\t")[0]
        assert first_idx == "0"
        assert second_idx == "1"


class TestFodpToTsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.tsv"
        fodp_to_tsv(MINIMAL_FODP, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.tsv"
        count = fodp_to_tsv(str(MINIMAL_FODP), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

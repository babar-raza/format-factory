"""
Tests for fodg_to_csv dogfood export.

Verifies that FODG drawing pages are converted to CSV rows using
Format Factory's FODG codec and CSV writer libraries.
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
EMPTY_FODG = _REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg"

from fodg.fodg_to_csv import fodg_to_csv


class TestFodgToCsvBasic:
    """Basic conversion tests."""

    def test_returns_page_count(self, tmp_path: Path) -> None:
        """Returns an integer count of pages written."""
        dest = tmp_path / "out.csv"
        count = fodg_to_csv(MINIMAL_FODG, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .csv file is created at the specified path."""
        dest = tmp_path / "out.csv"
        fodg_to_csv(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """CSV output is non-empty."""
        dest = tmp_path / "out.csv"
        fodg_to_csv(MINIMAL_FODG, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_minimal_drawing_returns_one_row(self, tmp_path: Path) -> None:
        """minimal-drawing.fodg (1 page) → 1 data row."""
        dest = tmp_path / "out.csv"
        count = fodg_to_csv(MINIMAL_FODG, dest)
        assert count == 1


class TestFodgToCsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row with page_name and text_content is written by default."""
        dest = tmp_path / "out.csv"
        fodg_to_csv(MINIMAL_FODG, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "page_name" in first_line
        assert "text_content" in first_line

    def test_shape_count_in_header_by_default(self, tmp_path: Path) -> None:
        """shape_count appears in header by default."""
        dest = tmp_path / "out.csv"
        fodg_to_csv(MINIMAL_FODG, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "shape_count" in first_line

    def test_line_count_is_data_plus_header(self, tmp_path: Path) -> None:
        """Total non-empty lines = data rows + 1 header."""
        dest = tmp_path / "out.csv"
        count = fodg_to_csv(MINIMAL_FODG, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1


class TestFodgToCsvOptions:
    """Option flag tests."""

    def test_no_header_excludes_header_row(self, tmp_path: Path) -> None:
        """include_header=False excludes the header row."""
        dest = tmp_path / "out.csv"
        count = fodg_to_csv(MINIMAL_FODG, dest, include_header=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_include_page_index_adds_column(self, tmp_path: Path) -> None:
        """include_page_index=True adds page_index to header."""
        dest = tmp_path / "out.csv"
        fodg_to_csv(MINIMAL_FODG, dest, include_page_index=True)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "page_index" in first_line

    def test_page_index_absent_by_default(self, tmp_path: Path) -> None:
        """page_index column absent by default."""
        dest = tmp_path / "out.csv"
        fodg_to_csv(MINIMAL_FODG, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "page_index" not in first_line

    def test_no_shape_count_excludes_column(self, tmp_path: Path) -> None:
        """include_shape_count=False removes shape_count column."""
        dest = tmp_path / "out.csv"
        fodg_to_csv(MINIMAL_FODG, dest, include_shape_count=False)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "shape_count" not in first_line


class TestFodgToCsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.csv"
        fodg_to_csv(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.csv"
        count = fodg_to_csv(str(MINIMAL_FODG), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

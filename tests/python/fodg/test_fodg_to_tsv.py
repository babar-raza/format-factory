"""
Tests for fodg_to_tsv dogfood export.

Verifies that FODG drawing pages are converted to TSV rows using
Format Factory's FODG codec and TSV writer libraries.
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

from fodg.fodg_to_tsv import fodg_to_tsv


class TestFodgToTsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.tsv"
        count = fodg_to_tsv(MINIMAL_FODG, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .tsv file is created at the specified path."""
        dest = tmp_path / "out.tsv"
        fodg_to_tsv(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """TSV output is non-empty."""
        dest = tmp_path / "out.tsv"
        fodg_to_tsv(MINIMAL_FODG, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_shapes_document_produces_rows(self, tmp_path: Path) -> None:
        """shapes-basic.fodg produces at least one data row."""
        dest = tmp_path / "out.tsv"
        count = fodg_to_tsv(SHAPES_FODG, dest)
        assert count >= 1


class TestFodgToTsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row with page_name, text_content, shape_count is written by default."""
        dest = tmp_path / "out.tsv"
        fodg_to_tsv(MINIMAL_FODG, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "page_name" in first_line
        assert "text_content" in first_line
        assert "shape_count" in first_line

    def test_tab_separator_in_output(self, tmp_path: Path) -> None:
        """Output file uses tab as field separator."""
        dest = tmp_path / "out.tsv"
        fodg_to_tsv(MINIMAL_FODG, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "\t" in first_line

    def test_line_count_is_data_plus_header(self, tmp_path: Path) -> None:
        """Total non-empty lines = page count + 1 header."""
        dest = tmp_path / "out.tsv"
        count = fodg_to_tsv(SHAPES_FODG, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1

    def test_three_columns_by_default(self, tmp_path: Path) -> None:
        """Default output has 3 tab-separated columns (page_name, text_content, shape_count)."""
        dest = tmp_path / "out.tsv"
        fodg_to_tsv(MINIMAL_FODG, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert first_line.count("\t") == 2


class TestFodgToTsvOptions:
    """Option flag tests."""

    def test_no_header_excludes_header_row(self, tmp_path: Path) -> None:
        """include_header=False excludes the header row."""
        dest = tmp_path / "out.tsv"
        count = fodg_to_tsv(SHAPES_FODG, dest, include_header=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_include_page_index_adds_column(self, tmp_path: Path) -> None:
        """include_page_index=True adds a page_index column."""
        dest = tmp_path / "out.tsv"
        fodg_to_tsv(MINIMAL_FODG, dest, include_page_index=True)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "page_index" in first_line
        assert first_line.count("\t") == 3

    def test_no_shape_count_removes_column(self, tmp_path: Path) -> None:
        """include_shape_count=False removes the shape_count column."""
        dest = tmp_path / "out.tsv"
        fodg_to_tsv(MINIMAL_FODG, dest, include_shape_count=False)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "shape_count" not in first_line
        assert first_line.count("\t") == 1

    def test_page_index_values_are_sequential(self, tmp_path: Path) -> None:
        """Page index values are 0-based sequential integers."""
        dest = tmp_path / "out.tsv"
        count = fodg_to_tsv(SHAPES_FODG, dest, include_page_index=True)
        if count >= 1:
            lines = dest.read_text(encoding="utf-8").splitlines()
            first_idx = lines[1].split("\t")[0]
            assert first_idx == "0"


class TestFodgToTsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.tsv"
        fodg_to_tsv(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.tsv"
        count = fodg_to_tsv(str(MINIMAL_FODG), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

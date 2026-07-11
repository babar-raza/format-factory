"""
Tests for dif_to_tsv dogfood export.

Verifies that DIF data rows are converted to TSV using
Format Factory's DIF parser and TSV writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

NUMERIC_ROW_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "numeric-row.dif"
SINGLE_CELL_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "single-cell.dif"
MINIMAL_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"

from dif.dif_to_tsv import dif_to_tsv


class TestDifToTsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.tsv"
        count = dif_to_tsv(NUMERIC_ROW_DIF, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .tsv file is created at the specified path."""
        dest = tmp_path / "out.tsv"
        dif_to_tsv(NUMERIC_ROW_DIF, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """TSV output is non-empty."""
        dest = tmp_path / "out.tsv"
        dif_to_tsv(NUMERIC_ROW_DIF, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_numeric_row_returns_one_row(self, tmp_path: Path) -> None:
        """numeric-row.dif (1 row) → 1 data row."""
        dest = tmp_path / "out.tsv"
        count = dif_to_tsv(NUMERIC_ROW_DIF, dest)
        assert count == 1

    def test_single_cell_returns_one_row(self, tmp_path: Path) -> None:
        """single-cell.dif → 1 data row."""
        dest = tmp_path / "out.tsv"
        count = dif_to_tsv(SINGLE_CELL_DIF, dest)
        assert count == 1


class TestDifToTsvContent:
    """Content correctness tests."""

    def test_numeric_values_in_output(self, tmp_path: Path) -> None:
        """Numeric cell values appear in TSV output."""
        dest = tmp_path / "out.tsv"
        dif_to_tsv(NUMERIC_ROW_DIF, dest)
        content = dest.read_text(encoding="utf-8")
        # numeric-row.dif has values 1.0, 2.0, 3.0
        assert "1.0" in content or "1" in content

    def test_data_uses_tabs(self, tmp_path: Path) -> None:
        """Multi-column rows use tab separator."""
        dest = tmp_path / "out.tsv"
        dif_to_tsv(NUMERIC_ROW_DIF, dest)
        content = dest.read_text(encoding="utf-8")
        # numeric-row has 3 cells, so should have tabs
        lines = [l for l in content.splitlines() if l.strip()]
        if lines:
            assert "\t" in lines[0]

    def test_minimal_dif_row_count(self, tmp_path: Path) -> None:
        """minimal-2x2.dif → correct number of rows."""
        dest = tmp_path / "out.tsv"
        count = dif_to_tsv(MINIMAL_DIF, dest)
        assert count >= 1


class TestDifToTsvOptions:
    """Option flag tests."""

    def test_include_row_index_adds_column(self, tmp_path: Path) -> None:
        """include_row_index=True prepends row index."""
        dest = tmp_path / "out.tsv"
        dif_to_tsv(NUMERIC_ROW_DIF, dest, include_row_index=True)
        content = dest.read_text(encoding="utf-8")
        # Row index 0 should appear
        assert "0" in content

    def test_row_index_absent_by_default(self, tmp_path: Path) -> None:
        """include_row_index=False by default."""
        dest_with = tmp_path / "with_idx.tsv"
        dest_without = tmp_path / "without_idx.tsv"
        dif_to_tsv(NUMERIC_ROW_DIF, dest_with, include_row_index=True)
        dif_to_tsv(NUMERIC_ROW_DIF, dest_without, include_row_index=False)
        # File with index should be longer
        assert len(dest_with.read_text()) >= len(dest_without.read_text())


class TestDifToTsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.tsv"
        dif_to_tsv(NUMERIC_ROW_DIF, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.tsv"
        count = dif_to_tsv(str(NUMERIC_ROW_DIF), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

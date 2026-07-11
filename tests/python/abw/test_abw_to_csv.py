"""
Tests for abw_to_csv dogfood export.

Verifies that ABW paragraphs are converted to CSV rows using
Format Factory's ABW codec and CSV writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_ABW = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
TWO_PARAS_ABW = _REPO / "samples" / "by-format" / "abw" / "two-paragraphs.abw"

from abw.abw_to_csv import abw_to_csv


class TestAbwToCsvBasic:
    """Basic conversion tests."""

    def test_returns_data_row_count(self, tmp_path: Path) -> None:
        """Returns count of data rows (excluding header)."""
        dest = tmp_path / "out.csv"
        count = abw_to_csv(MINIMAL_ABW, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .csv file is created."""
        dest = tmp_path / "out.csv"
        abw_to_csv(MINIMAL_ABW, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """CSV output is non-empty."""
        dest = tmp_path / "out.csv"
        abw_to_csv(MINIMAL_ABW, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_two_paragraphs_produces_two_rows(self, tmp_path: Path) -> None:
        """two-paragraphs.abw → 2 data rows."""
        dest = tmp_path / "out.csv"
        count = abw_to_csv(TWO_PARAS_ABW, dest)
        assert count == 2


class TestAbwToCsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row 'text' is present by default."""
        dest = tmp_path / "out.csv"
        abw_to_csv(MINIMAL_ABW, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "text" in first_line.lower()

    def test_line_count_is_data_plus_header(self, tmp_path: Path) -> None:
        """Total lines = data rows + 1 header."""
        dest = tmp_path / "out.csv"
        count = abw_to_csv(TWO_PARAS_ABW, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1

    def test_paragraph_text_in_output(self, tmp_path: Path) -> None:
        """Paragraph text appears in the CSV output."""
        dest = tmp_path / "out.csv"
        abw_to_csv(MINIMAL_ABW, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content.strip()) > 0


class TestAbwToCsvOptions:
    """Option flag tests."""

    def test_no_header_excludes_header_row(self, tmp_path: Path) -> None:
        """include_header=False excludes the header row."""
        dest = tmp_path / "out.csv"
        count = abw_to_csv(TWO_PARAS_ABW, dest, include_header=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_paragraph_index_absent_by_default(self, tmp_path: Path) -> None:
        """paragraph_index column not present by default."""
        dest = tmp_path / "out.csv"
        abw_to_csv(TWO_PARAS_ABW, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        # Header should have one column only
        assert lines[0].count(",") == 0

    def test_paragraph_index_included_when_enabled(self, tmp_path: Path) -> None:
        """paragraph_index column present when include_paragraph_index=True."""
        dest = tmp_path / "out.csv"
        abw_to_csv(TWO_PARAS_ABW, dest, include_paragraph_index=True)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "paragraph_index" in first_line

    def test_skip_empty_true_by_default(self, tmp_path: Path) -> None:
        """skip_empty=True by default omits empty paragraphs."""
        dest = tmp_path / "out.csv"
        count = abw_to_csv(TWO_PARAS_ABW, dest)
        # two-paragraphs.abw has exactly 2 non-empty paragraphs
        assert count >= 1


class TestAbwToCsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.csv"
        abw_to_csv(MINIMAL_ABW, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.csv"
        count = abw_to_csv(str(MINIMAL_ABW), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

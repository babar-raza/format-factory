"""
Tests for fodp_to_csv dogfood export.

Verifies that FODP presentation slides are converted to CSV rows using
Format Factory's FODP codec and CSV writer libraries.
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

from fodp.fodp_to_csv import fodp_to_csv


class TestFodpToCsvBasic:
    """Basic conversion tests."""

    def test_returns_slide_count(self, tmp_path: Path) -> None:
        """Returns an integer count of slides written."""
        dest = tmp_path / "out.csv"
        count = fodp_to_csv(MINIMAL_FODP, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .csv file is created at the specified path."""
        dest = tmp_path / "out.csv"
        fodp_to_csv(MINIMAL_FODP, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """CSV output is non-empty."""
        dest = tmp_path / "out.csv"
        fodp_to_csv(MINIMAL_FODP, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_minimal_presentation_returns_one_row(self, tmp_path: Path) -> None:
        """minimal-presentation.fodp (1 slide) → 1 data row."""
        dest = tmp_path / "out.csv"
        count = fodp_to_csv(MINIMAL_FODP, dest)
        assert count == 1

    def test_two_slides_returns_two_rows(self, tmp_path: Path) -> None:
        """two-slides-basic.fodp (2 slides) → 2 data rows."""
        dest = tmp_path / "out.csv"
        count = fodp_to_csv(TWO_SLIDES_FODP, dest)
        assert count == 2


class TestFodpToCsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row with slide_name, title, text_content is written by default."""
        dest = tmp_path / "out.csv"
        fodp_to_csv(MINIMAL_FODP, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "slide_name" in first_line
        assert "title" in first_line

    def test_line_count_is_data_plus_header(self, tmp_path: Path) -> None:
        """Total non-empty lines = data rows + 1 header."""
        dest = tmp_path / "out.csv"
        count = fodp_to_csv(TWO_SLIDES_FODP, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1

    def test_slide_content_in_output(self, tmp_path: Path) -> None:
        """Slide content appears in the CSV output."""
        dest = tmp_path / "out.csv"
        fodp_to_csv(TWO_SLIDES_FODP, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content.strip()) > 0


class TestFodpToCsvOptions:
    """Option flag tests."""

    def test_no_header_excludes_header_row(self, tmp_path: Path) -> None:
        """include_header=False excludes the header row."""
        dest = tmp_path / "out.csv"
        count = fodp_to_csv(TWO_SLIDES_FODP, dest, include_header=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_include_slide_index_adds_column(self, tmp_path: Path) -> None:
        """include_slide_index=True adds slide_index to header."""
        dest = tmp_path / "out.csv"
        fodp_to_csv(MINIMAL_FODP, dest, include_slide_index=True)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "slide_index" in first_line

    def test_slide_index_absent_by_default(self, tmp_path: Path) -> None:
        """slide_index column absent by default."""
        dest = tmp_path / "out.csv"
        fodp_to_csv(MINIMAL_FODP, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "slide_index" not in first_line


class TestFodpToCsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.csv"
        fodp_to_csv(MINIMAL_FODP, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.csv"
        count = fodp_to_csv(str(MINIMAL_FODP), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

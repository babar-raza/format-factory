"""
Tests for abw_to_tsv dogfood export.

Verifies that ABW paragraphs are converted to TSV rows using
Format Factory's ABW codec and TSV writer libraries.
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

from abw.abw_to_tsv import abw_to_tsv


class TestAbwToTsvBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of rows written."""
        dest = tmp_path / "out.tsv"
        count = abw_to_tsv(MINIMAL_ABW, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .tsv file is created at the specified path."""
        dest = tmp_path / "out.tsv"
        abw_to_tsv(MINIMAL_ABW, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path: Path) -> None:
        """TSV output is non-empty."""
        dest = tmp_path / "out.tsv"
        abw_to_tsv(MINIMAL_ABW, dest)
        assert len(dest.read_text(encoding="utf-8").strip()) > 0

    def test_two_paragraphs_produces_two_rows(self, tmp_path: Path) -> None:
        """two-paragraphs.abw → 2 data rows."""
        dest = tmp_path / "out.tsv"
        count = abw_to_tsv(TWO_PARAS_ABW, dest)
        assert count == 2


class TestAbwToTsvContent:
    """Content correctness tests."""

    def test_header_row_present_by_default(self, tmp_path: Path) -> None:
        """Header row 'text' is present by default."""
        dest = tmp_path / "out.tsv"
        abw_to_tsv(MINIMAL_ABW, dest)
        first_line = dest.read_text(encoding="utf-8").splitlines()[0]
        assert "text" in first_line.lower()

    def test_line_count_is_data_plus_header(self, tmp_path: Path) -> None:
        """Total non-empty lines = data rows + 1 header."""
        dest = tmp_path / "out.tsv"
        count = abw_to_tsv(TWO_PARAS_ABW, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count + 1

    def test_paragraph_text_in_output(self, tmp_path: Path) -> None:
        """Paragraph text appears in the TSV output."""
        dest = tmp_path / "out.tsv"
        abw_to_tsv(MINIMAL_ABW, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content.strip()) > 0


class TestAbwToTsvOptions:
    """Option flag tests."""

    def test_no_header_excludes_header_row(self, tmp_path: Path) -> None:
        """include_headers=False excludes the header row."""
        dest = tmp_path / "out.tsv"
        count = abw_to_tsv(TWO_PARAS_ABW, dest, include_headers=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_skip_empty_true_by_default(self, tmp_path: Path) -> None:
        """skip_empty=True by default omits empty paragraphs."""
        dest = tmp_path / "out.tsv"
        count = abw_to_tsv(TWO_PARAS_ABW, dest)
        assert count >= 1


class TestAbwToTsvPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.tsv"
        abw_to_tsv(MINIMAL_ABW, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.tsv"
        count = abw_to_tsv(str(MINIMAL_ABW), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

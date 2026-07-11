"""
Tests for tsv_to_abw dogfood export.

Verifies that TSV rows are converted to ABW paragraphs using
Format Factory's TSV parser and ABW writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_TSV = _REPO / "samples" / "by-format" / "tsv" / "minimal-2x2.tsv"

from tsv.tsv_to_abw import tsv_to_abw


class TestTsvToAbwBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        count = tsv_to_abw(MINIMAL_TSV, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        tsv_to_abw(MINIMAL_TSV, dest)
        assert dest.exists()

    def test_produces_rows(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        count = tsv_to_abw(MINIMAL_TSV, dest)
        assert count >= 1

    def test_output_is_xml(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        tsv_to_abw(MINIMAL_TSV, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<abiword" in content or "<?xml" in content


class TestTsvToAbwPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.abw"
        tsv_to_abw(MINIMAL_TSV, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        count = tsv_to_abw(str(MINIMAL_TSV), str(dest))
        assert isinstance(count, int) and dest.exists()

"""
Tests for dif_to_fodt dogfood export.

Verifies that DIF rows are converted to FODT paragraphs using
Format Factory's DIF parser and FODT writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "minimal-2x2.dif"
NUMERIC_DIF = _REPO / "samples" / "by-format" / "dif" / "valid" / "numeric-row.dif"

from dif.dif_to_fodt import dif_to_fodt


class TestDifToFodtBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = dif_to_fodt(MINIMAL_DIF, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        dif_to_fodt(MINIMAL_DIF, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        dif_to_fodt(MINIMAL_DIF, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_paragraph(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        dif_to_fodt(MINIMAL_DIF, dest)
        content = dest.read_text(encoding="utf-8")
        assert "text:p" in content


class TestDifToFodtContent:
    """Content correctness tests."""

    def test_produces_paragraphs(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = dif_to_fodt(MINIMAL_DIF, dest)
        assert count >= 1

    def test_numeric_dif_converts(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = dif_to_fodt(NUMERIC_DIF, dest)
        assert dest.exists() and count >= 1

    def test_custom_separator(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        dif_to_fodt(MINIMAL_DIF, dest, separator=" , ")
        content = dest.read_text(encoding="utf-8")
        assert " , " in content


class TestDifToFodtPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.fodt"
        dif_to_fodt(MINIMAL_DIF, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.fodt"
        count = dif_to_fodt(str(MINIMAL_DIF), str(dest))
        assert isinstance(count, int) and dest.exists()

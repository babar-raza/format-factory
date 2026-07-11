"""
Tests for odt_to_abw dogfood export.

Verifies that ODT elements are converted to ABW paragraphs using
Format Factory's ODT parser and ABW writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_ODT = _REPO / "samples" / "by-format" / "odt" / "valid" / "minimal-document.odt"

from odt.odt_to_abw import odt_to_abw


class TestOdtToAbwBasic:
    """Basic conversion tests."""

    def test_returns_element_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        count = odt_to_abw(MINIMAL_ODT, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        odt_to_abw(MINIMAL_ODT, dest)
        assert dest.exists()

    def test_produces_elements(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        count = odt_to_abw(MINIMAL_ODT, dest)
        assert count >= 1

    def test_output_is_xml(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        odt_to_abw(MINIMAL_ODT, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<abiword" in content or "<?xml" in content


class TestOdtToAbwPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.abw"
        odt_to_abw(MINIMAL_ODT, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        count = odt_to_abw(str(MINIMAL_ODT), str(dest))
        assert isinstance(count, int) and dest.exists()

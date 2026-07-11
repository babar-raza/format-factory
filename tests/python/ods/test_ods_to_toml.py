"""
Tests for ods_to_toml dogfood export.

Verifies that ODS rows are converted to TOML array table entries using
Format Factory's ODS parser and TOML writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_ODS = _REPO / "samples" / "by-format" / "ods" / "valid" / "minimal-spreadsheet.ods"

from ods.ods_to_toml import ods_to_toml


class TestOdsToTomlBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = ods_to_toml(MINIMAL_ODS, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        ods_to_toml(MINIMAL_ODS, dest)
        assert dest.exists()

    def test_produces_rows(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = ods_to_toml(MINIMAL_ODS, dest)
        assert count >= 1

    def test_custom_table_key(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        ods_to_toml(MINIMAL_ODS, dest, table_key="data")
        content = dest.read_text(encoding="utf-8")
        assert "data" in content


class TestOdsToTomlPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.toml"
        ods_to_toml(MINIMAL_ODS, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.toml"
        count = ods_to_toml(str(MINIMAL_ODS), str(dest))
        assert isinstance(count, int) and dest.exists()

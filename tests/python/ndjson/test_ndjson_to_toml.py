"""
Tests for ndjson_to_toml dogfood export.

Verifies that NDJSON records are converted to TOML array table entries using
Format Factory's NDJSON codec and TOML writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_NDJSON = _REPO / "samples" / "by-format" / "ndjson" / "valid" / "minimal.ndjson"

from ndjson.ndjson_to_toml import ndjson_to_toml


class TestNdjsonToTomlBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of records written."""
        dest = tmp_path / "out.toml"
        count = ndjson_to_toml(MINIMAL_NDJSON, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .toml file is created at the specified path."""
        dest = tmp_path / "out.toml"
        ndjson_to_toml(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_output_is_toml(self, tmp_path: Path) -> None:
        """Output file contains TOML array table markers."""
        dest = tmp_path / "out.toml"
        ndjson_to_toml(MINIMAL_NDJSON, dest)
        content = dest.read_text(encoding="utf-8")
        assert "[[" in content or "=" in content

    def test_content_has_data(self, tmp_path: Path) -> None:
        """TOML file has substantial content."""
        dest = tmp_path / "out.toml"
        ndjson_to_toml(MINIMAL_NDJSON, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content) > 10


class TestNdjsonToTomlOptions:
    """Option flag tests."""

    def test_custom_table_key(self, tmp_path: Path) -> None:
        """table_key parameter sets the TOML array table name."""
        dest = tmp_path / "out.toml"
        ndjson_to_toml(MINIMAL_NDJSON, dest, table_key="items")
        content = dest.read_text(encoding="utf-8")
        assert "items" in content


class TestNdjsonToTomlPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.toml"
        ndjson_to_toml(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.toml"
        count = ndjson_to_toml(str(MINIMAL_NDJSON), str(dest))
        assert isinstance(count, int) and dest.exists()

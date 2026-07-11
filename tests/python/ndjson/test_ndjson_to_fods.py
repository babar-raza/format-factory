"""
Tests for ndjson_to_fods dogfood export.

Verifies that NDJSON records are converted to FODS format using
Format Factory's NDJSON codec and FODS writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_NDJSON = _REPO / "samples" / "by-format" / "ndjson" / "valid" / "minimal.ndjson"

from ndjson.ndjson_to_fods import ndjson_to_fods


class TestNdjsonToFodsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of records written."""
        dest = tmp_path / "out.fods"
        count = ndjson_to_fods(MINIMAL_NDJSON, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .fods file is created at the specified path."""
        dest = tmp_path / "out.fods"
        ndjson_to_fods(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_output_is_xml(self, tmp_path: Path) -> None:
        """FODS file is XML (flat format, not ZIP)."""
        dest = tmp_path / "out.fods"
        ndjson_to_fods(MINIMAL_NDJSON, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<?xml" in content or "<office:document" in content

    def test_output_contains_table(self, tmp_path: Path) -> None:
        """FODS file contains table element."""
        dest = tmp_path / "out.fods"
        ndjson_to_fods(MINIMAL_NDJSON, dest)
        content = dest.read_text(encoding="utf-8")
        assert "table:table" in content


class TestNdjsonToFodsContent:
    """Content correctness tests."""

    def test_produces_rows(self, tmp_path: Path) -> None:
        """NDJSON records appear as FODS rows."""
        dest = tmp_path / "out.fods"
        count = ndjson_to_fods(MINIMAL_NDJSON, dest)
        assert count >= 1

    def test_content_has_data(self, tmp_path: Path) -> None:
        """FODS file has substantial content."""
        dest = tmp_path / "out.fods"
        ndjson_to_fods(MINIMAL_NDJSON, dest)
        content = dest.read_text(encoding="utf-8")
        assert len(content) > 100


class TestNdjsonToFodsOptions:
    """Option flag tests."""

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the FODS sheet name."""
        dest = tmp_path / "out.fods"
        ndjson_to_fods(MINIMAL_NDJSON, dest, sheet_name="NDJSON_Data")
        content = dest.read_text(encoding="utf-8")
        assert "NDJSON_Data" in content

    def test_include_headers(self, tmp_path: Path) -> None:
        """include_headers=True (default) includes header row."""
        dest = tmp_path / "out.fods"
        ndjson_to_fods(MINIMAL_NDJSON, dest, include_headers=True)
        assert dest.exists()

    def test_no_headers(self, tmp_path: Path) -> None:
        """include_headers=False skips header row."""
        dest = tmp_path / "out.fods"
        count = ndjson_to_fods(MINIMAL_NDJSON, dest, include_headers=False)
        assert count >= 0


class TestNdjsonToFodsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.fods"
        ndjson_to_fods(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.fods"
        count = ndjson_to_fods(str(MINIMAL_NDJSON), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

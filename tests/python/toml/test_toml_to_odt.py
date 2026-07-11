"""
Tests for toml_to_odt dogfood export.

Verifies that TOML key-value pairs are converted to ODT paragraphs using
Format Factory's TOML codec and ODT writer libraries.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_TOML = _REPO / "samples" / "by-format" / "toml" / "minimal.toml"

from toml.toml_to_odt import toml_to_odt


class TestTomlToOdtBasic:
    """Basic conversion tests."""

    def test_returns_paragraph_count(self, tmp_path: Path) -> None:
        """Returns an integer count of paragraphs written."""
        dest = tmp_path / "out.odt"
        count = toml_to_odt(MINIMAL_TOML, dest)
        assert isinstance(count, int)
        assert count >= 1

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .odt file is created at the specified path."""
        dest = tmp_path / "out.odt"
        toml_to_odt(MINIMAL_TOML, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODT file is a valid ZIP container."""
        dest = tmp_path / "out.odt"
        toml_to_odt(MINIMAL_TOML, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODT ZIP contains content.xml."""
        dest = tmp_path / "out.odt"
        toml_to_odt(MINIMAL_TOML, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestTomlToOdtContent:
    """Content correctness tests."""

    def test_content_xml_has_paragraph(self, tmp_path: Path) -> None:
        """content.xml contains paragraph elements."""
        dest = tmp_path / "out.odt"
        toml_to_odt(MINIMAL_TOML, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "text:p" in content

    def test_keys_appear_in_content(self, tmp_path: Path) -> None:
        """TOML keys appear in content.xml."""
        dest = tmp_path / "out.odt"
        toml_to_odt(MINIMAL_TOML, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "title" in content

    def test_values_appear_in_content(self, tmp_path: Path) -> None:
        """TOML values appear in content.xml."""
        dest = tmp_path / "out.odt"
        toml_to_odt(MINIMAL_TOML, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "Format Factory" in content

    def test_paragraph_count_matches_top_level_keys(self, tmp_path: Path) -> None:
        """Paragraph count equals number of top-level TOML keys."""
        dest = tmp_path / "out.odt"
        count = toml_to_odt(MINIMAL_TOML, dest)
        # minimal.toml has: title, version, enabled, server, database = 5 top-level keys
        assert count == 5

    def test_boolean_formatted_as_lowercase(self, tmp_path: Path) -> None:
        """Boolean values are formatted as 'true'/'false'."""
        dest = tmp_path / "out.odt"
        toml_to_odt(MINIMAL_TOML, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "true" in content or "false" in content


class TestTomlToOdtPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.odt"
        toml_to_odt(MINIMAL_TOML, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.odt"
        count = toml_to_odt(str(MINIMAL_TOML), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

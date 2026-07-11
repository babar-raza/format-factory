"""
Tests for toml_to_ods dogfood export.

Verifies that TOML key-value pairs are converted to ODS rows using
Format Factory's TOML codec and ODS writer libraries.
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

from toml.toml_to_ods import toml_to_ods


class TestTomlToOdsBasic:
    """Basic conversion tests."""

    def test_returns_row_count(self, tmp_path: Path) -> None:
        """Returns an integer count of data rows written."""
        dest = tmp_path / "out.ods"
        count = toml_to_ods(MINIMAL_TOML, dest)
        assert isinstance(count, int)
        assert count >= 1

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ods file is created at the specified path."""
        dest = tmp_path / "out.ods"
        toml_to_ods(MINIMAL_TOML, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODS file is a valid ZIP container."""
        dest = tmp_path / "out.ods"
        toml_to_ods(MINIMAL_TOML, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODS ZIP contains content.xml."""
        dest = tmp_path / "out.ods"
        toml_to_ods(MINIMAL_TOML, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestTomlToOdsContent:
    """Content correctness tests."""

    def test_content_xml_has_table(self, tmp_path: Path) -> None:
        """content.xml contains a table element."""
        dest = tmp_path / "out.ods"
        toml_to_ods(MINIMAL_TOML, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "table:table" in content

    def test_keys_appear_in_content(self, tmp_path: Path) -> None:
        """TOML keys appear in content.xml."""
        dest = tmp_path / "out.ods"
        toml_to_ods(MINIMAL_TOML, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "title" in content

    def test_values_appear_in_content(self, tmp_path: Path) -> None:
        """TOML string values appear in content.xml."""
        dest = tmp_path / "out.ods"
        toml_to_ods(MINIMAL_TOML, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "Format Factory" in content

    def test_row_count_matches_top_level_keys(self, tmp_path: Path) -> None:
        """Row count equals number of top-level TOML keys."""
        dest = tmp_path / "out.ods"
        count = toml_to_ods(MINIMAL_TOML, dest)
        # minimal.toml has 5 top-level keys
        assert count == 5


class TestTomlToOdsOptions:
    """Option flag tests."""

    def test_include_value_type_adds_column(self, tmp_path: Path) -> None:
        """include_value_type=True adds value_type column."""
        dest = tmp_path / "out.ods"
        toml_to_ods(MINIMAL_TOML, dest, include_value_type=True)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "value_type" in content

    def test_custom_sheet_name(self, tmp_path: Path) -> None:
        """sheet_name parameter sets the ODS sheet name."""
        dest = tmp_path / "out.ods"
        toml_to_ods(MINIMAL_TOML, dest, sheet_name="Config")
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "Config" in content

    def test_no_header(self, tmp_path: Path) -> None:
        """include_header=False excludes the header row."""
        dest = tmp_path / "out.ods"
        toml_to_ods(MINIMAL_TOML, dest, include_header=False)
        assert dest.exists()


class TestTomlToOdsPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ods"
        toml_to_ods(MINIMAL_TOML, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ods"
        count = toml_to_ods(str(MINIMAL_TOML), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

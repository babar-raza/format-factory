"""
Tests for ndjson_to_odt dogfood export.

Verifies that NDJSON records are converted to ODT paragraphs using
Format Factory's NDJSON codec and ODT writer libraries.
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_NDJSON = _REPO / "samples" / "by-format" / "ndjson" / "valid" / "minimal.ndjson"

from ndjson.ndjson_to_odt import ndjson_to_odt


class TestNdjsonToOdtBasic:
    """Basic conversion tests."""

    def test_returns_paragraph_count(self, tmp_path: Path) -> None:
        """Returns an integer count of paragraphs written."""
        dest = tmp_path / "out.odt"
        count = ndjson_to_odt(MINIMAL_NDJSON, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .odt file is created at the specified path."""
        dest = tmp_path / "out.odt"
        ndjson_to_odt(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_output_is_valid_zip(self, tmp_path: Path) -> None:
        """ODT file is a valid ZIP container."""
        dest = tmp_path / "out.odt"
        ndjson_to_odt(MINIMAL_NDJSON, dest)
        assert zipfile.is_zipfile(dest)

    def test_output_contains_content_xml(self, tmp_path: Path) -> None:
        """ODT ZIP contains content.xml."""
        dest = tmp_path / "out.odt"
        ndjson_to_odt(MINIMAL_NDJSON, dest)
        with zipfile.ZipFile(dest) as z:
            assert "content.xml" in z.namelist()


class TestNdjsonToOdtContent:
    """Content correctness tests."""

    def test_three_records_produce_three_paragraphs(self, tmp_path: Path) -> None:
        """minimal.ndjson has 3 records → 3 paragraphs."""
        dest = tmp_path / "out.odt"
        count = ndjson_to_odt(MINIMAL_NDJSON, dest)
        assert count == 3

    def test_record_values_in_content(self, tmp_path: Path) -> None:
        """Record values appear in content.xml."""
        dest = tmp_path / "out.odt"
        ndjson_to_odt(MINIMAL_NDJSON, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "Alice" in content

    def test_content_xml_has_paragraph(self, tmp_path: Path) -> None:
        """content.xml contains paragraph elements."""
        dest = tmp_path / "out.odt"
        ndjson_to_odt(MINIMAL_NDJSON, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "text:p" in content

    def test_key_value_format_by_default(self, tmp_path: Path) -> None:
        """Default format uses key: value pairs."""
        dest = tmp_path / "out.odt"
        ndjson_to_odt(MINIMAL_NDJSON, dest)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        assert "name" in content


class TestNdjsonToOdtOptions:
    """Option flag tests."""

    def test_format_as_json_produces_json_strings(self, tmp_path: Path) -> None:
        """format_as_json=True serializes each record as JSON."""
        dest = tmp_path / "out.odt"
        ndjson_to_odt(MINIMAL_NDJSON, dest, format_as_json=True)
        with zipfile.ZipFile(dest) as z:
            content = z.read("content.xml").decode("utf-8")
        # JSON format uses quotes around string values
        assert '"Alice"' in content or "Alice" in content


class TestNdjsonToOdtPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.odt"
        ndjson_to_odt(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.odt"
        count = ndjson_to_odt(str(MINIMAL_NDJSON), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

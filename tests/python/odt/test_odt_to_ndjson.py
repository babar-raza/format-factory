"""
Tests for odt_to_ndjson dogfood export.

Verifies that ODT elements are converted to NDJSON records using
Format Factory's odt and ndjson libraries.
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
SAMPLE_ODT = _REPO / "samples" / "by-format" / "odt" / "valid" / "minimal-document.odt"
TWO_PARAS_ODT = _REPO / "samples" / "by-format" / "odt" / "valid" / "two-paragraphs.odt"

import sys
sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_to_ndjson import odt_to_ndjson


class TestOdtToNdjsonBasic:
    """Basic conversion tests."""

    def test_returns_record_count(self, tmp_path: Path) -> None:
        """Returns an integer count of records written."""
        dest = tmp_path / "out.ndjson"
        count = odt_to_ndjson(SAMPLE_ODT, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output file is created at the specified path."""
        dest = tmp_path / "out.ndjson"
        odt_to_ndjson(SAMPLE_ODT, dest)
        assert dest.exists()

    def test_output_is_valid_ndjson(self, tmp_path: Path) -> None:
        """Each line of output is valid JSON."""
        dest = tmp_path / "out.ndjson"
        odt_to_ndjson(SAMPLE_ODT, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_records_have_element_type(self, tmp_path: Path) -> None:
        """Every record has an element_type field."""
        dest = tmp_path / "out.ndjson"
        odt_to_ndjson(SAMPLE_ODT, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            obj = json.loads(line)
            assert "element_type" in obj

    def test_records_have_text_field(self, tmp_path: Path) -> None:
        """Every record has a text field."""
        dest = tmp_path / "out.ndjson"
        odt_to_ndjson(SAMPLE_ODT, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            obj = json.loads(line)
            assert "text" in obj


class TestOdtToNdjsonElementIndex:
    """Element index field tests."""

    def test_element_index_included_by_default(self, tmp_path: Path) -> None:
        """element_index is included in each record by default."""
        dest = tmp_path / "out.ndjson"
        odt_to_ndjson(SAMPLE_ODT, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        if lines:
            obj = json.loads(lines[0])
            assert "element_index" in obj

    def test_element_index_omitted_when_disabled(self, tmp_path: Path) -> None:
        """element_index is absent when include_element_index=False."""
        dest = tmp_path / "out.ndjson"
        odt_to_ndjson(SAMPLE_ODT, dest, include_element_index=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            obj = json.loads(line)
            assert "element_index" not in obj

    def test_element_indices_are_sequential(self, tmp_path: Path) -> None:
        """element_index values are sequential starting from 0."""
        dest = tmp_path / "out.ndjson"
        count = odt_to_ndjson(TWO_PARAS_ODT, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        if count > 1:
            indices = [json.loads(l)["element_index"] for l in lines]
            assert indices == list(range(count))


class TestOdtToNdjsonContent:
    """Content accuracy tests."""

    def test_two_paragraphs_produces_two_records(self, tmp_path: Path) -> None:
        """Two-paragraphs ODT file produces exactly 2 records."""
        dest = tmp_path / "out.ndjson"
        count = odt_to_ndjson(TWO_PARAS_ODT, dest)
        assert count == 2

    def test_paragraph_elements_have_correct_type(self, tmp_path: Path) -> None:
        """Paragraph elements are recorded with element_type='paragraph'."""
        dest = tmp_path / "out.ndjson"
        odt_to_ndjson(TWO_PARAS_ODT, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        types = {json.loads(l)["element_type"] for l in lines}
        assert "paragraph" in types or "heading" in types

    def test_record_count_matches_return_value(self, tmp_path: Path) -> None:
        """Line count in output matches the return value."""
        dest = tmp_path / "out.ndjson"
        count = odt_to_ndjson(TWO_PARAS_ODT, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count


class TestOdtToNdjsonPaths:
    """Path and output directory tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories as needed."""
        dest = tmp_path / "nested" / "dir" / "out.ndjson"
        odt_to_ndjson(SAMPLE_ODT, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths in addition to Path objects."""
        dest = tmp_path / "out.ndjson"
        count = odt_to_ndjson(str(SAMPLE_ODT), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

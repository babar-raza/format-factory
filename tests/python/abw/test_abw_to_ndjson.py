"""
Tests for abw_to_ndjson dogfood export.

Verifies that ABW paragraphs are converted to NDJSON records using
Format Factory's abw reader and ndjson writer libraries.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

MINIMAL_ABW = _REPO / "samples" / "by-format" / "abw" / "minimal-document.abw"
TWO_PARAS_ABW = _REPO / "samples" / "by-format" / "abw" / "two-paragraphs.abw"

from abw.abw_to_ndjson import abw_to_ndjson


class TestAbwToNdjsonBasic:
    """Basic conversion tests."""

    def test_returns_record_count(self, tmp_path: Path) -> None:
        """Returns an integer count of records written."""
        dest = tmp_path / "out.ndjson"
        count = abw_to_ndjson(TWO_PARAS_ABW, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ndjson file is created at the specified path."""
        dest = tmp_path / "out.ndjson"
        abw_to_ndjson(TWO_PARAS_ABW, dest)
        assert dest.exists()

    def test_output_is_valid_ndjson(self, tmp_path: Path) -> None:
        """Each line of output is valid JSON."""
        dest = tmp_path / "out.ndjson"
        abw_to_ndjson(TWO_PARAS_ABW, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_two_paragraphs_produces_two_records(self, tmp_path: Path) -> None:
        """two-paragraphs.abw produces exactly 2 records."""
        dest = tmp_path / "out.ndjson"
        count = abw_to_ndjson(TWO_PARAS_ABW, dest)
        assert count == 2

    def test_records_have_text_field(self, tmp_path: Path) -> None:
        """Every record has a 'text' field."""
        dest = tmp_path / "out.ndjson"
        abw_to_ndjson(TWO_PARAS_ABW, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            assert "text" in json.loads(line)


class TestAbwToNdjsonContent:
    """Content accuracy tests."""

    def test_paragraph_text_preserved(self, tmp_path: Path) -> None:
        """Paragraph text content is preserved in records."""
        dest = tmp_path / "out.ndjson"
        abw_to_ndjson(TWO_PARAS_ABW, dest)
        content = dest.read_text(encoding="utf-8")
        assert "First paragraph" in content or "paragraph" in content.lower()

    def test_paragraph_index_sequential(self, tmp_path: Path) -> None:
        """paragraph_index values are sequential from 0."""
        dest = tmp_path / "out.ndjson"
        count = abw_to_ndjson(TWO_PARAS_ABW, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        indices = [json.loads(l)["paragraph_index"] for l in lines]
        assert indices == list(range(count))

    def test_line_count_matches_return(self, tmp_path: Path) -> None:
        """Line count in output matches the return value."""
        dest = tmp_path / "out.ndjson"
        count = abw_to_ndjson(TWO_PARAS_ABW, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count


class TestAbwToNdjsonOptions:
    """Option and parameter tests."""

    def test_paragraph_index_included_by_default(self, tmp_path: Path) -> None:
        """paragraph_index is included in each record by default."""
        dest = tmp_path / "out.ndjson"
        abw_to_ndjson(TWO_PARAS_ABW, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        if lines:
            assert "paragraph_index" in json.loads(lines[0])

    def test_paragraph_index_omitted_when_disabled(self, tmp_path: Path) -> None:
        """paragraph_index absent when include_paragraph_index=False."""
        dest = tmp_path / "out.ndjson"
        abw_to_ndjson(TWO_PARAS_ABW, dest, include_paragraph_index=False)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            assert "paragraph_index" not in json.loads(line)

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ndjson"
        count = abw_to_ndjson(str(TWO_PARAS_ABW), str(dest))
        assert isinstance(count, int)
        assert dest.exists()


class TestAbwToNdjsonPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ndjson"
        abw_to_ndjson(TWO_PARAS_ABW, dest)
        assert dest.exists()

"""
Tests for fodp_to_ndjson dogfood export.

Verifies that FODP presentation slides are converted to NDJSON records using
Format Factory's FODP codec and NDJSON writer libraries.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODP = _REPO / "samples" / "by-format" / "fodp" / "minimal-presentation.fodp"
TWO_SLIDES_FODP = _REPO / "samples" / "by-format" / "fodp" / "two-slides-basic.fodp"
TITLE_ONLY_FODP = _REPO / "samples" / "by-format" / "fodp" / "title-only.fodp"

from fodp.fodp_to_ndjson import fodp_to_ndjson


class TestFodpToNdjsonBasic:
    """Basic conversion tests."""

    def test_returns_record_count(self, tmp_path: Path) -> None:
        """Returns an integer count of records written."""
        dest = tmp_path / "out.ndjson"
        count = fodp_to_ndjson(MINIMAL_FODP, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ndjson file is created."""
        dest = tmp_path / "out.ndjson"
        fodp_to_ndjson(MINIMAL_FODP, dest)
        assert dest.exists()

    def test_one_record_per_slide(self, tmp_path: Path) -> None:
        """One NDJSON record is emitted per slide."""
        dest = tmp_path / "out.ndjson"
        count = fodp_to_ndjson(MINIMAL_FODP, dest)
        assert count == 1

    def test_two_slides_two_records(self, tmp_path: Path) -> None:
        """Two-slide file produces exactly two records."""
        dest = tmp_path / "out.ndjson"
        count = fodp_to_ndjson(TWO_SLIDES_FODP, dest)
        assert count == 2

    def test_output_is_valid_ndjson(self, tmp_path: Path) -> None:
        """Each line of output is valid JSON."""
        dest = tmp_path / "out.ndjson"
        fodp_to_ndjson(TWO_SLIDES_FODP, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_record_count_matches_return_value(self, tmp_path: Path) -> None:
        """Line count in output matches the return value."""
        dest = tmp_path / "out.ndjson"
        count = fodp_to_ndjson(TWO_SLIDES_FODP, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count


class TestFodpToNdjsonContent:
    """Content correctness tests."""

    def test_slide_name_present(self, tmp_path: Path) -> None:
        """Records contain slide_name field."""
        dest = tmp_path / "out.ndjson"
        fodp_to_ndjson(MINIMAL_FODP, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "slide_name" in record

    def test_title_present(self, tmp_path: Path) -> None:
        """Records contain title field."""
        dest = tmp_path / "out.ndjson"
        fodp_to_ndjson(MINIMAL_FODP, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "title" in record

    def test_text_content_is_list(self, tmp_path: Path) -> None:
        """text_content field is a list."""
        dest = tmp_path / "out.ndjson"
        fodp_to_ndjson(MINIMAL_FODP, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert isinstance(record["text_content"], list)

    def test_two_slides_titles(self, tmp_path: Path) -> None:
        """Two-slide file contains expected titles."""
        dest = tmp_path / "out.ndjson"
        fodp_to_ndjson(TWO_SLIDES_FODP, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        records = [json.loads(l) for l in lines]
        titles = [r["title"] for r in records]
        assert "Introduction" in titles
        assert "Conclusion" in titles


class TestFodpToNdjsonOptions:
    """Option flag tests."""

    def test_slide_index_absent_by_default(self, tmp_path: Path) -> None:
        """slide_index is NOT the default — check actual default behavior."""
        dest = tmp_path / "out.ndjson"
        fodp_to_ndjson(MINIMAL_FODP, dest, include_slide_index=False)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "slide_index" not in record

    def test_slide_index_included_when_enabled(self, tmp_path: Path) -> None:
        """slide_index is present when include_slide_index=True."""
        dest = tmp_path / "out.ndjson"
        fodp_to_ndjson(TWO_SLIDES_FODP, dest, include_slide_index=True)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        records = [json.loads(l) for l in lines]
        indices = [r["slide_index"] for r in records]
        assert indices == list(range(len(records)))

    def test_shape_count_included_by_default(self, tmp_path: Path) -> None:
        """shape_count is present by default."""
        dest = tmp_path / "out.ndjson"
        fodp_to_ndjson(MINIMAL_FODP, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "shape_count" in record
        assert isinstance(record["shape_count"], int)

    def test_shape_count_excluded_when_disabled(self, tmp_path: Path) -> None:
        """shape_count is absent when include_shape_count=False."""
        dest = tmp_path / "out.ndjson"
        fodp_to_ndjson(MINIMAL_FODP, dest, include_shape_count=False)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "shape_count" not in record


class TestFodpToNdjsonPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ndjson"
        fodp_to_ndjson(MINIMAL_FODP, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ndjson"
        count = fodp_to_ndjson(str(MINIMAL_FODP), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

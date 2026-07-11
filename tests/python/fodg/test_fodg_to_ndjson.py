"""
Tests for fodg_to_ndjson dogfood export.

Verifies that FODG drawing pages are converted to NDJSON records using
Format Factory's FODG codec and NDJSON writer libraries.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

EMPTY_FODG = _REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg"
MINIMAL_FODG = _REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg"
SHAPES_FODG = _REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg"

from fodg.fodg_to_ndjson import fodg_to_ndjson


class TestFodgToNdjsonBasic:
    """Basic conversion tests."""

    def test_returns_record_count(self, tmp_path: Path) -> None:
        """Returns an integer count of records written."""
        dest = tmp_path / "out.ndjson"
        count = fodg_to_ndjson(MINIMAL_FODG, dest)
        assert isinstance(count, int)
        assert count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        """Output .ndjson file is created."""
        dest = tmp_path / "out.ndjson"
        fodg_to_ndjson(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_one_record_per_page(self, tmp_path: Path) -> None:
        """One NDJSON record is emitted per drawing page."""
        dest = tmp_path / "out.ndjson"
        count = fodg_to_ndjson(MINIMAL_FODG, dest)
        assert count == 1

    def test_output_is_valid_ndjson(self, tmp_path: Path) -> None:
        """Each line of output is valid JSON."""
        dest = tmp_path / "out.ndjson"
        fodg_to_ndjson(SHAPES_FODG, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)

    def test_record_count_matches_return_value(self, tmp_path: Path) -> None:
        """Line count in output matches the return value."""
        dest = tmp_path / "out.ndjson"
        count = fodg_to_ndjson(SHAPES_FODG, dest)
        lines = [l for l in dest.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == count

    def test_empty_page_has_zero_shapes(self, tmp_path: Path) -> None:
        """Empty page record has shape_count=0."""
        dest = tmp_path / "out.ndjson"
        fodg_to_ndjson(EMPTY_FODG, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert record["shape_count"] == 0


class TestFodgToNdjsonContent:
    """Content correctness tests."""

    def test_page_name_present(self, tmp_path: Path) -> None:
        """Records contain page_name field."""
        dest = tmp_path / "out.ndjson"
        fodg_to_ndjson(MINIMAL_FODG, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "page_name" in record
        assert isinstance(record["page_name"], str)

    def test_text_content_is_list(self, tmp_path: Path) -> None:
        """text_content field is a list."""
        dest = tmp_path / "out.ndjson"
        fodg_to_ndjson(SHAPES_FODG, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert isinstance(record["text_content"], list)

    def test_shapes_basic_has_text(self, tmp_path: Path) -> None:
        """shapes-basic.fodg has text content extracted."""
        dest = tmp_path / "out.ndjson"
        fodg_to_ndjson(SHAPES_FODG, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        # shapes-basic has 3 shapes with text like 'Rect', 'Ellipse'
        assert len(record["text_content"]) > 0


class TestFodgToNdjsonOptions:
    """Option flag tests."""

    def test_page_index_present_by_default(self, tmp_path: Path) -> None:
        """page_index is present by default."""
        dest = tmp_path / "out.ndjson"
        fodg_to_ndjson(MINIMAL_FODG, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "page_index" in record
        assert record["page_index"] == 0

    def test_page_index_absent_when_disabled(self, tmp_path: Path) -> None:
        """page_index absent when include_page_index=False."""
        dest = tmp_path / "out.ndjson"
        fodg_to_ndjson(MINIMAL_FODG, dest, include_page_index=False)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "page_index" not in record

    def test_shape_count_present_by_default(self, tmp_path: Path) -> None:
        """shape_count is present by default."""
        dest = tmp_path / "out.ndjson"
        fodg_to_ndjson(MINIMAL_FODG, dest)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "shape_count" in record

    def test_shape_count_absent_when_disabled(self, tmp_path: Path) -> None:
        """shape_count absent when include_shape_count=False."""
        dest = tmp_path / "out.ndjson"
        fodg_to_ndjson(MINIMAL_FODG, dest, include_shape_count=False)
        record = json.loads(dest.read_text(encoding="utf-8").strip())
        assert "shape_count" not in record


class TestFodgToNdjsonPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates intermediate parent directories."""
        dest = tmp_path / "nested" / "dir" / "out.ndjson"
        fodg_to_ndjson(MINIMAL_FODG, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        """Accepts string paths as well as Path objects."""
        dest = tmp_path / "out.ndjson"
        count = fodg_to_ndjson(str(MINIMAL_FODG), str(dest))
        assert isinstance(count, int)
        assert dest.exists()

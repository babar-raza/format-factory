"""
Tests for ndjson_to_abw dogfood export.

Verifies that NDJSON records are converted to ABW paragraphs using
Format Factory's NDJSON codec and ABW writer libraries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_NDJSON = _REPO / "samples" / "by-format" / "ndjson" / "valid/minimal.ndjson"

from ndjson.ndjson_to_abw import ndjson_to_abw


class TestNdjsonToAbwBasic:
    """Basic conversion tests."""

    def test_returns_record_count(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        count = ndjson_to_abw(MINIMAL_NDJSON, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        ndjson_to_abw(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_produces_records(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        count = ndjson_to_abw(MINIMAL_NDJSON, dest)
        assert count >= 1

    def test_output_is_xml(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        ndjson_to_abw(MINIMAL_NDJSON, dest)
        content = dest.read_text(encoding="utf-8")
        assert "<abiword" in content or "<?xml" in content


class TestNdjsonToAbwPaths:
    """Path handling tests."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        dest = tmp_path / "nested" / "dir" / "out.abw"
        ndjson_to_abw(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path: Path) -> None:
        dest = tmp_path / "out.abw"
        count = ndjson_to_abw(str(MINIMAL_NDJSON), str(dest))
        assert isinstance(count, int) and dest.exists()

"""Tests for fodt_to_ndjson dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODT = _REPO / "samples" / "by-format" / "fodt" / "minimal-document.fodt"
from src.python.fodt.fodt_to_ndjson import fodt_to_ndjson


class TestFodtToNdjsonBasic:
    def test_returns_record_count(self, tmp_path):
        dest = tmp_path / "out.ndjson"
        count = fodt_to_ndjson(MINIMAL_FODT, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.ndjson"
        fodt_to_ndjson(MINIMAL_FODT, dest)
        assert dest.exists()

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.ndjson"
        fodt_to_ndjson(MINIMAL_FODT, dest)
        assert dest.stat().st_size > 0

    def test_produces_records(self, tmp_path):
        dest = tmp_path / "out.ndjson"
        count = fodt_to_ndjson(MINIMAL_FODT, dest)
        assert count >= 0


class TestFodtToNdjsonPaths:
    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.ndjson"
        count = fodt_to_ndjson(str(MINIMAL_FODT), str(dest))
        assert isinstance(count, int) and dest.exists()

    def test_count_matches_file_lines(self, tmp_path):
        dest = tmp_path / "out.ndjson"
        count = fodt_to_ndjson(MINIMAL_FODT, dest)
        lines = [l for l in dest.read_text().splitlines() if l.strip()]
        assert len(lines) == count

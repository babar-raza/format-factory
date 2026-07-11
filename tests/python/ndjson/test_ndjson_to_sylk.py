"""Tests for ndjson_to_sylk dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_NDJSON = _REPO / "samples" / "by-format" / "ndjson" / "valid" / "minimal.ndjson"
from src.python.ndjson.ndjson_to_sylk import ndjson_to_sylk


class TestNdjsonToSylkBasic:
    def test_returns_row_count(self, tmp_path):
        dest = tmp_path / "out.slk"
        count = ndjson_to_sylk(MINIMAL_NDJSON, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.slk"
        ndjson_to_sylk(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_produces_rows(self, tmp_path):
        dest = tmp_path / "out.slk"
        count = ndjson_to_sylk(MINIMAL_NDJSON, dest)
        assert count >= 1

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.slk"
        ndjson_to_sylk(MINIMAL_NDJSON, dest)
        assert dest.stat().st_size > 0


class TestNdjsonToSylkPaths:
    def test_creates_parent_directories(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.slk"
        ndjson_to_sylk(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.slk"
        count = ndjson_to_sylk(str(MINIMAL_NDJSON), str(dest))
        assert isinstance(count, int) and dest.exists()

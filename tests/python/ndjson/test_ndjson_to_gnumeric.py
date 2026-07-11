"""Tests for ndjson_to_gnumeric dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_NDJSON = _REPO / "samples" / "by-format" / "ndjson" / "valid" / "minimal.ndjson"
from ndjson.ndjson_to_gnumeric import ndjson_to_gnumeric


class TestNdjsonToGnumericBasic:
    def test_returns_record_count(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = ndjson_to_gnumeric(MINIMAL_NDJSON, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        ndjson_to_gnumeric(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_produces_records(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = ndjson_to_gnumeric(MINIMAL_NDJSON, dest)
        assert count >= 1

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        ndjson_to_gnumeric(MINIMAL_NDJSON, dest)
        assert dest.stat().st_size > 0


class TestNdjsonToGnumericPaths:
    def test_creates_parent_directories(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.gnumeric"
        ndjson_to_gnumeric(MINIMAL_NDJSON, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.gnumeric"
        count = ndjson_to_gnumeric(str(MINIMAL_NDJSON), str(dest))
        assert isinstance(count, int) and dest.exists()

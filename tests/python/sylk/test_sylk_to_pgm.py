"""Tests for sylk_to_pgm dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

SAMPLE = _REPO / "samples" / "by-format" / "sylk" / "valid" / "minimal-2x2.slk"
from src.python.sylk.sylk_to_pgm import sylk_to_pgm


class TestSYLKToPGMBasic:
    def test_returns_row_count(self, tmp_path):
        dest = tmp_path / "out.pgm"
        count = sylk_to_pgm(SAMPLE, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.pgm"
        sylk_to_pgm(SAMPLE, dest)
        assert dest.exists()

    def test_produces_rows(self, tmp_path):
        dest = tmp_path / "out.pgm"
        count = sylk_to_pgm(SAMPLE, dest)
        assert count >= 1

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.pgm"
        sylk_to_pgm(SAMPLE, dest)
        assert dest.stat().st_size > 0


class TestSYLKToPGMPaths:
    def test_creates_parent_directories(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.pgm"
        sylk_to_pgm(SAMPLE, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.pgm"
        count = sylk_to_pgm(str(SAMPLE), str(dest))
        assert isinstance(count, int) and dest.exists()

"""Tests for gnumeric_to_pgm dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

SAMPLE = _REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric"
from src.python.gnumeric.gnumeric_to_pgm import gnumeric_to_pgm


class TestGnumericToPGMBasic:
    def test_returns_row_count(self, tmp_path):
        dest = tmp_path / "out.pgm"
        count = gnumeric_to_pgm(SAMPLE, dest)
        assert isinstance(count, int) and count >= 0

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.pgm"
        gnumeric_to_pgm(SAMPLE, dest)
        assert dest.exists()

    def test_produces_rows(self, tmp_path):
        dest = tmp_path / "out.pgm"
        count = gnumeric_to_pgm(SAMPLE, dest)
        assert count >= 1

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.pgm"
        gnumeric_to_pgm(SAMPLE, dest)
        assert dest.stat().st_size > 0


class TestGnumericToPGMPaths:
    def test_creates_parent_directories(self, tmp_path):
        dest = tmp_path / "nested" / "dir" / "out.pgm"
        gnumeric_to_pgm(SAMPLE, dest)
        assert dest.exists()

    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.pgm"
        count = gnumeric_to_pgm(str(SAMPLE), str(dest))
        assert isinstance(count, int) and dest.exists()

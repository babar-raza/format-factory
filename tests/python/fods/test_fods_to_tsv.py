"""Tests for fods_to_tsv dogfood export."""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))
sys.path.insert(0, str(_REPO))

MINIMAL_FODS = _REPO / "samples" / "by-format" / "fods" / "minimal-spreadsheet.fods"
from src.python.fods.fods_to_tsv import fods_to_tsv


class TestFodsToTsvBasic:
    def test_returns_tuple(self, tmp_path):
        dest = tmp_path / "out.tsv"
        result = fods_to_tsv(MINIMAL_FODS, dest)
        assert isinstance(result, tuple) and len(result) == 2

    def test_output_file_created(self, tmp_path):
        dest = tmp_path / "out.tsv"
        fods_to_tsv(MINIMAL_FODS, dest)
        assert dest.exists()

    def test_row_count_is_int(self, tmp_path):
        dest = tmp_path / "out.tsv"
        row_count, headers = fods_to_tsv(MINIMAL_FODS, dest)
        assert isinstance(row_count, int) and row_count >= 0

    def test_output_nonempty(self, tmp_path):
        dest = tmp_path / "out.tsv"
        fods_to_tsv(MINIMAL_FODS, dest)
        assert dest.stat().st_size > 0


class TestFodsToTsvPaths:
    def test_accepts_string_paths(self, tmp_path):
        dest = tmp_path / "out.tsv"
        result = fods_to_tsv(str(MINIMAL_FODS), str(dest))
        assert isinstance(result, tuple) and dest.exists()

    def test_headers_is_list(self, tmp_path):
        dest = tmp_path / "out.tsv"
        row_count, headers = fods_to_tsv(MINIMAL_FODS, dest)
        assert isinstance(headers, list)

"""
test_r161_pgm_flip.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT21-001
Added: 2026-06-10

Tests for PGM flip_horizontal function.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import flip_horizontal, write_pgm, parse_pgm_strict, PgmError


class TestPgmFlipHorizontal:
    def test_2x1(self, tmp_path):
        src = tmp_path / "src.pgm"
        write_pgm([100, 200], 2, 1, 255, src)
        dest = tmp_path / "flipped.pgm"
        result = flip_horizontal(src, dest)
        assert result["ok"] is True
        img = parse_pgm_strict(dest)
        assert img.pixels == [200, 100]

    def test_1x1(self, tmp_path):
        src = tmp_path / "src.pgm"
        write_pgm([128], 1, 1, 255, src)
        dest = tmp_path / "flipped.pgm"
        flip_horizontal(src, dest)
        img = parse_pgm_strict(dest)
        assert img.pixels == [128]

    def test_2x2(self, tmp_path):
        src = tmp_path / "src.pgm"
        write_pgm([10, 20, 30, 40], 2, 2, 255, src)
        dest = tmp_path / "flipped.pgm"
        flip_horizontal(src, dest)
        img = parse_pgm_strict(dest)
        assert img.pixels == [20, 10, 40, 30]

    def test_preserves_dimensions(self, tmp_path):
        src = tmp_path / "src.pgm"
        write_pgm([0] * 6, 3, 2, 255, src)
        dest = tmp_path / "flipped.pgm"
        result = flip_horizontal(src, dest)
        assert result["width"] == 3
        assert result["height"] == 2

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(PgmError):
            flip_horizontal(tmp_path / "ghost.pgm", tmp_path / "out.pgm")

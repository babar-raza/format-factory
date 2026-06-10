"""
test_r159_pbm_flip.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT19-001
Added: 2026-06-10

Tests for PBM flip_horizontal function.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import flip_horizontal, write_pbm, parse_pbm_strict, PbmError


class TestFlipHorizontal:
    def test_2x2(self, tmp_path):
        src = tmp_path / "src.pbm"
        write_pbm([1, 0, 0, 1], 2, 2, src)
        dest = tmp_path / "flipped.pbm"
        result = flip_horizontal(src, dest)
        assert result["ok"] is True
        img = parse_pbm_strict(dest)
        assert img.pixels == [0, 1, 1, 0]

    def test_1x1(self, tmp_path):
        src = tmp_path / "src.pbm"
        write_pbm([1], 1, 1, src)
        dest = tmp_path / "flipped.pbm"
        flip_horizontal(src, dest)
        img = parse_pbm_strict(dest)
        assert img.pixels == [1]

    def test_3x1(self, tmp_path):
        src = tmp_path / "src.pbm"
        write_pbm([1, 0, 1], 3, 1, src)
        dest = tmp_path / "flipped.pbm"
        flip_horizontal(src, dest)
        img = parse_pbm_strict(dest)
        assert img.pixels == [1, 0, 1]

    def test_asymmetric(self, tmp_path):
        src = tmp_path / "src.pbm"
        write_pbm([1, 0, 0], 3, 1, src)
        dest = tmp_path / "flipped.pbm"
        flip_horizontal(src, dest)
        img = parse_pbm_strict(dest)
        assert img.pixels == [0, 0, 1]

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(PbmError):
            flip_horizontal(tmp_path / "ghost.pbm", tmp_path / "out.pbm")

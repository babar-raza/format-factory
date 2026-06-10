"""
test_r161_pbm_count_white.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT21-001
Added: 2026-06-10

Tests for PBM count_white function.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import count_white, write_pbm, PbmError


class TestCountWhite:
    def test_all_white(self, tmp_path):
        p = tmp_path / "test.pbm"
        write_pbm([0, 0, 0, 0], 2, 2, p)
        assert count_white(p) == 4

    def test_all_black(self, tmp_path):
        p = tmp_path / "test.pbm"
        write_pbm([1, 1, 1, 1], 2, 2, p)
        assert count_white(p) == 0

    def test_mixed(self, tmp_path):
        p = tmp_path / "test.pbm"
        write_pbm([1, 0, 0, 1], 2, 2, p)
        assert count_white(p) == 2

    def test_single_white(self, tmp_path):
        p = tmp_path / "test.pbm"
        write_pbm([0], 1, 1, p)
        assert count_white(p) == 1

    def test_nonexistent_file(self, tmp_path):
        with pytest.raises(PbmError):
            count_white(tmp_path / "ghost.pbm")

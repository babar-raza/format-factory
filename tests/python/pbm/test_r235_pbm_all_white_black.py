"""Tests for pbm_all_white and pbm_all_black (Sprint 25)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm import pbm_all_white, pbm_all_black, write_pbm


def _make_pbm(tmp_path, name, pixels, width, height):
    p = tmp_path / f"{name}.pbm"
    write_pbm(pixels, width, height, str(p))
    return str(p)


class TestPbmAllWhite:
    def test_all_white_image(self, tmp_path):
        p = _make_pbm(tmp_path, "aw", [0, 0, 0, 0], 2, 2)
        assert pbm_all_white(p) is True

    def test_mixed_image(self, tmp_path):
        p = _make_pbm(tmp_path, "mx", [0, 1, 0, 0], 2, 2)
        assert pbm_all_white(p) is False

    def test_all_black_returns_false(self, tmp_path):
        p = _make_pbm(tmp_path, "ab", [1, 1, 1, 1], 2, 2)
        assert pbm_all_white(p) is False

    def test_return_type(self, tmp_path):
        p = _make_pbm(tmp_path, "rt", [0], 1, 1)
        assert isinstance(pbm_all_white(p), bool)

    def test_single_white_pixel(self, tmp_path):
        p = _make_pbm(tmp_path, "sw", [0], 1, 1)
        assert pbm_all_white(p) is True


class TestPbmAllBlack:
    def test_all_black_image(self, tmp_path):
        p = _make_pbm(tmp_path, "ab2", [1, 1, 1, 1], 2, 2)
        assert pbm_all_black(p) is True

    def test_mixed_image(self, tmp_path):
        p = _make_pbm(tmp_path, "mx2", [1, 0, 1, 1], 2, 2)
        assert pbm_all_black(p) is False

    def test_all_white_returns_false(self, tmp_path):
        p = _make_pbm(tmp_path, "aw2", [0, 0, 0, 0], 2, 2)
        assert pbm_all_black(p) is False

    def test_return_type(self, tmp_path):
        p = _make_pbm(tmp_path, "rt2", [1], 1, 1)
        assert isinstance(pbm_all_black(p), bool)

    def test_single_black_pixel(self, tmp_path):
        p = _make_pbm(tmp_path, "sb", [1], 1, 1)
        assert pbm_all_black(p) is True

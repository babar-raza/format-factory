"""Tests for pbm_total_pixel_count and pbm_is_binary.

Product deepening: PBM analytics — TC-H3-002-PBM / PDC-PBM-TOTAL-PIXEL-001.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import (
    pbm_total_pixel_count,
    pbm_is_binary,
    write_pbm,
)


def _make_pbm(tmp_path, name, pixels, w, h):
    path = tmp_path / f"{name}.pbm"
    write_pbm(pixels, w, h, str(path))
    return path


class TestPbmTotalPixelCount:
    def test_1x1(self, tmp_path):
        f = _make_pbm(tmp_path, "1x1", [0], 1, 1)
        assert pbm_total_pixel_count(f) == 1

    def test_2x3(self, tmp_path):
        pixels = [0, 1, 1, 0, 0, 1]
        f = _make_pbm(tmp_path, "2x3", pixels, 3, 2)
        assert pbm_total_pixel_count(f) == 6

    def test_4x4(self, tmp_path):
        pixels = [0] * 16
        f = _make_pbm(tmp_path, "4x4", pixels, 4, 4)
        assert pbm_total_pixel_count(f) == 16

    def test_returns_int(self, tmp_path):
        f = _make_pbm(tmp_path, "type", [0], 1, 1)
        assert isinstance(pbm_total_pixel_count(f), int)

    def test_10x10(self, tmp_path):
        pixels = [1] * 100
        f = _make_pbm(tmp_path, "10x10", pixels, 10, 10)
        assert pbm_total_pixel_count(f) == 100


class TestPbmIsBinary:
    def test_ascii_p1(self, tmp_path):
        f = _make_pbm(tmp_path, "ascii", [0, 1, 1, 0], 2, 2)
        assert pbm_is_binary(f) is False

    def test_returns_bool(self, tmp_path):
        f = _make_pbm(tmp_path, "type2", [0], 1, 1)
        assert isinstance(pbm_is_binary(f), bool)

    def test_p1_file_starts_with_p1(self, tmp_path):
        f = _make_pbm(tmp_path, "check", [0, 1], 2, 1)
        data = f.read_bytes()
        assert data[:2] == b"P1"
        assert pbm_is_binary(f) is False

    def test_manual_p4(self, tmp_path):
        path = tmp_path / "binary.pbm"
        # P4 format: header + packed binary data
        # 8x1 image: byte 0xFF = all black
        path.write_bytes(b"P4\n8 1\n\xff")
        assert pbm_is_binary(path) is True

    def test_manual_p1(self, tmp_path):
        path = tmp_path / "ascii2.pbm"
        path.write_bytes(b"P1\n2 2\n0 1\n1 0\n")
        assert pbm_is_binary(path) is False

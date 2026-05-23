"""
test_r55_ppm_p6_binary.py — R55 Train F: P6 binary PPM parse tests.

TC-BINARY-PPM-001: P6 binary PPM files (8-bit RGB) are parsed correctly.

Sprint: FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.ppm.ppm_parser import (
    SUPPORTED_FEATURES,
    UNSUPPORTED_FEATURES,
    PpmDecodeError,
    parse_ppm_strict,
)


def _make_p6(
    width: int,
    height: int,
    maxval: int,
    pixels: list[tuple[int, int, int]],
    tmp_path: Path,
) -> Path:
    """Build a P6 binary PPM file."""
    header = f"P6\n{width} {height}\n{maxval}\n".encode("ascii")
    if maxval <= 255:
        pixel_bytes = b"".join(bytes([r, g, b]) for r, g, b in pixels)
    else:
        import struct
        pixel_bytes = b"".join(
            struct.pack(">HHH", r, g, b) for r, g, b in pixels
        )
    f = tmp_path / "test.ppm"
    f.write_bytes(header + pixel_bytes)
    return f


class TestP6BinaryBasic:
    def test_p6_feature_in_supported(self):
        """p6_binary_parse must be in SUPPORTED_FEATURES after R55."""
        assert "p6_binary_parse" in SUPPORTED_FEATURES

    def test_p6_not_in_unsupported(self):
        """p6_binary_parse must NOT be in UNSUPPORTED_FEATURES after R55."""
        assert "p6_binary_parse" not in UNSUPPORTED_FEATURES

    def test_p6_1x1_pixel(self, tmp_path):
        """P6 1x1 image parses correctly."""
        f = _make_p6(1, 1, 255, [(10, 20, 30)], tmp_path)
        img = parse_ppm_strict(f)
        assert img.magic == "P6"
        assert img.pixels == [(10, 20, 30)]
        assert img.width == 1
        assert img.height == 1

    def test_p6_2x2_pixels(self, tmp_path):
        """P6 2x2 image parses all 4 RGB pixels."""
        px = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]
        f = _make_p6(2, 2, 255, px, tmp_path)
        img = parse_ppm_strict(f)
        assert img.pixels == px

    def test_p6_maxval_boundary(self, tmp_path):
        """Pixel component equal to maxval is valid."""
        f = _make_p6(1, 1, 200, [(200, 100, 50)], tmp_path)
        img = parse_ppm_strict(f)
        assert img.pixels[0] == (200, 100, 50)

    def test_p6_zero_pixel(self, tmp_path):
        """All-zero pixel is valid."""
        f = _make_p6(1, 1, 255, [(0, 0, 0)], tmp_path)
        img = parse_ppm_strict(f)
        assert img.pixels[0] == (0, 0, 0)

    def test_p6_pixel_count(self, tmp_path):
        """Total pixel count equals width * height."""
        px = [(i, i, i) for i in range(6)]
        f = _make_p6(3, 2, 255, px, tmp_path)
        img = parse_ppm_strict(f)
        assert len(img.pixels) == 6


class TestP6BinaryErrors:
    def test_p6_truncated_raises(self, tmp_path):
        """Truncated P6 data raises PpmDecodeError."""
        header = b"P6\n2 2\n255\n"
        f = tmp_path / "trunc.ppm"
        f.write_bytes(header + bytes(6))  # only 6 of 12 bytes
        with pytest.raises(PpmDecodeError):
            parse_ppm_strict(f)


class TestP6BackwardCompat:
    def test_p3_still_parses(self, tmp_path):
        """P3 ASCII parsing still works after adding P6 support."""
        f = tmp_path / "ascii.ppm"
        f.write_text("P3\n1 1\n255\n10 20 30\n", encoding="ascii")
        img = parse_ppm_strict(f)
        assert img.magic == "P3"
        assert img.pixels == [(10, 20, 30)]

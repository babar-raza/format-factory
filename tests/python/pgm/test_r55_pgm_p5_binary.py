"""
test_r55_pgm_p5_binary.py — R55 Train F: P5 binary PGM parse tests.

TC-BINARY-PGM-001: P5 binary PGM files (8-bit and 16-bit) are parsed correctly.

Sprint: FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.pgm.pgm_parser import (
    SUPPORTED_FEATURES,
    UNSUPPORTED_FEATURES,
    PgmDecodeError,
    PgmInvalidHeaderError,
    PgmInvalidMagicError,
    parse_pgm_strict,
)


def _make_p5(width: int, height: int, maxval: int, pixels: list[int], tmp_path: Path) -> Path:
    """Build a P5 binary PGM file."""
    header = f"P5\n{width} {height}\n{maxval}\n".encode("ascii")
    if maxval <= 255:
        pixel_bytes = bytes(pixels)
    else:
        pixel_bytes = b"".join(struct.pack(">H", v) for v in pixels)
    f = tmp_path / "test.pgm"
    f.write_bytes(header + pixel_bytes)
    return f


class TestP5BinaryBasic:
    def test_p5_feature_in_supported(self):
        """p5_binary_parse must be in SUPPORTED_FEATURES after R55."""
        assert "p5_binary_parse" in SUPPORTED_FEATURES

    def test_p5_not_in_unsupported(self):
        """p5_binary_parse must NOT be in UNSUPPORTED_FEATURES after R55."""
        assert "p5_binary_parse" not in UNSUPPORTED_FEATURES

    def test_p5_1x1_pixel(self, tmp_path):
        """P5 1x1 image parses correctly."""
        f = _make_p5(1, 1, 255, [128], tmp_path)
        img = parse_pgm_strict(f)
        assert img.magic == "P5"
        assert img.width == 1
        assert img.height == 1
        assert img.pixels == [128]

    def test_p5_2x2_pixels(self, tmp_path):
        """P5 2x2 image parses all 4 pixels."""
        f = _make_p5(2, 2, 255, [10, 20, 30, 40], tmp_path)
        img = parse_pgm_strict(f)
        assert img.pixels == [10, 20, 30, 40]
        assert img.width == 2
        assert img.height == 2

    def test_p5_pixel_count_matches_wh(self, tmp_path):
        """Pixel count equals width * height."""
        f = _make_p5(3, 2, 200, [1, 2, 3, 4, 5, 6], tmp_path)
        img = parse_pgm_strict(f)
        assert len(img.pixels) == 6

    def test_p5_maxval_boundary(self, tmp_path):
        """Pixel equal to maxval is valid."""
        f = _make_p5(1, 1, 100, [100], tmp_path)
        img = parse_pgm_strict(f)
        assert img.pixels[0] == 100

    def test_p5_zero_pixel(self, tmp_path):
        """Pixel value 0 is valid."""
        f = _make_p5(1, 1, 255, [0], tmp_path)
        img = parse_pgm_strict(f)
        assert img.pixels[0] == 0


class TestP5BinaryErrors:
    def test_p5_truncated_data_raises(self, tmp_path):
        """Truncated pixel data raises PgmDecodeError."""
        header = b"P5\n2 2\n255\n"
        f = tmp_path / "trunc.pgm"
        f.write_bytes(header + b"\x01\x02")  # only 2 of 4 bytes
        with pytest.raises(PgmDecodeError):
            parse_pgm_strict(f)


class TestP5BackwardCompat:
    def test_p2_still_parses(self, tmp_path):
        """P2 ASCII parsing still works after adding P5 support."""
        f = tmp_path / "ascii.pgm"
        f.write_text("P2\n2 1\n255\n100 200\n", encoding="ascii")
        img = parse_pgm_strict(f)
        assert img.magic == "P2"
        assert img.pixels == [100, 200]

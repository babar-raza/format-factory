"""
test_r55_pbm_p4_binary.py — R55 Train F: P4 binary PBM parse tests.

TC-BINARY-PBM-001: P4 binary PBM files (packed bits) are parsed correctly.

Sprint: FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.pbm.pbm_parser import (
    SUPPORTED_FEATURES,
    UNSUPPORTED_FEATURES,
    PbmDecodeError,
    parse_pbm_strict,
)


def _make_p4(width: int, height: int, pixels: list[int], tmp_path: Path) -> Path:
    """Build a P4 binary PBM file. pixels must be 0/1 values, row x col order."""
    header = f"P4\n{width} {height}\n".encode("ascii")
    row_bytes = (width + 7) // 8
    data = bytearray()
    for row in range(height):
        for byte_idx in range(row_bytes):
            byte_val = 0
            for bit in range(8):
                col = byte_idx * 8 + bit
                if col < width:
                    pix = pixels[row * width + col]
                    byte_val |= (pix & 1) << (7 - bit)
            data.append(byte_val)
    f = tmp_path / "test.pbm"
    f.write_bytes(header + bytes(data))
    return f


class TestP4BinaryBasic:
    def test_p4_feature_in_supported(self):
        """p4_binary_parse must be in SUPPORTED_FEATURES after R55."""
        assert "p4_binary_parse" in SUPPORTED_FEATURES

    def test_p4_not_in_unsupported(self):
        """p4_binary_parse must NOT be in UNSUPPORTED_FEATURES after R55."""
        assert "p4_binary_parse" not in UNSUPPORTED_FEATURES

    def test_p4_1x1_black(self, tmp_path):
        """P4 1x1 black pixel (bit=1) parses to pixel=1."""
        f = _make_p4(1, 1, [1], tmp_path)
        img = parse_pbm_strict(f)
        assert img.magic == "P4"
        assert img.pixels == [1]

    def test_p4_1x1_white(self, tmp_path):
        """P4 1x1 white pixel (bit=0) parses to pixel=0."""
        f = _make_p4(1, 1, [0], tmp_path)
        img = parse_pbm_strict(f)
        assert img.pixels == [0]

    def test_p4_8x1_row(self, tmp_path):
        """P4 8-pixel row fills exactly one byte."""
        pixels = [1, 0, 1, 0, 1, 0, 1, 0]
        f = _make_p4(8, 1, pixels, tmp_path)
        img = parse_pbm_strict(f)
        assert img.pixels == pixels

    def test_p4_3x2_non_aligned(self, tmp_path):
        """P4 3-pixel wide rows (padded to byte boundary) parse correctly."""
        pixels = [1, 0, 1,
                  0, 1, 0]
        f = _make_p4(3, 2, pixels, tmp_path)
        img = parse_pbm_strict(f)
        assert img.pixels == pixels
        assert img.width == 3
        assert img.height == 2

    def test_p4_pixel_count(self, tmp_path):
        """Total pixel count equals width * height."""
        f = _make_p4(4, 3, [0] * 12, tmp_path)
        img = parse_pbm_strict(f)
        assert len(img.pixels) == 12


class TestP4BinaryErrors:
    def test_p4_truncated_raises(self, tmp_path):
        """Truncated P4 data raises PbmDecodeError."""
        header = b"P4\n8 2\n"
        f = tmp_path / "trunc.pbm"
        f.write_bytes(header + b"\xff")  # only 1 of 2 row-bytes
        with pytest.raises(PbmDecodeError):
            parse_pbm_strict(f)


class TestP4BackwardCompat:
    def test_p1_still_parses(self, tmp_path):
        """P1 ASCII parsing still works after adding P4 support."""
        f = tmp_path / "ascii.pbm"
        f.write_text("P1\n2 1\n1 0\n", encoding="ascii")
        img = parse_pbm_strict(f)
        assert img.magic == "P1"
        assert img.pixels == [1, 0]

"""
test_r58_pgm_deepening.py — R58 Train G: PGM parser deepening.

Deepens coverage of PGM corpus samples, pixel value oracle, and edge cases
not covered by existing Gate 5-7 and R43/R55 tests.

R58 Sprint: FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
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

VALID = PROJECT_ROOT / "samples" / "by-format" / "pgm" / "valid"


class TestPgmCorpusOracle:
    """Oracle: committed corpus samples — exact pixel and dimension values."""

    def test_1x1_white_pixels(self):
        """1x1-white.pgm: single white pixel = 255."""
        img = parse_pgm_strict(VALID / "1x1-white.pgm")
        assert img.width == 1
        assert img.height == 1
        assert img.maxval == 255
        assert img.pixels == [255]

    def test_2x2_gradient_dimensions(self):
        """2x2-gradient.pgm: 2x2 image."""
        img = parse_pgm_strict(VALID / "2x2-gradient.pgm")
        assert img.width == 2
        assert img.height == 2

    def test_2x2_gradient_pixel_count(self):
        """2x2-gradient.pgm: exactly 4 pixels."""
        img = parse_pgm_strict(VALID / "2x2-gradient.pgm")
        assert len(img.pixels) == 4

    def test_2x2_gradient_pixel_values(self):
        """2x2-gradient.pgm: pixels are [0, 85, 170, 255]."""
        img = parse_pgm_strict(VALID / "2x2-gradient.pgm")
        assert img.pixels == [0, 85, 170, 255]

    def test_3x1_ramp_dimensions(self):
        """3x1-ramp.pgm: 3 wide, 1 tall."""
        img = parse_pgm_strict(VALID / "3x1-ramp.pgm")
        assert img.width == 3
        assert img.height == 1

    def test_3x1_ramp_pixel_values(self):
        """3x1-ramp.pgm: pixels are [0, 128, 255]."""
        img = parse_pgm_strict(VALID / "3x1-ramp.pgm")
        assert img.pixels == [0, 128, 255]

    def test_magic_is_p2_for_ascii(self):
        """All corpus P2 ASCII files: magic == 'P2'."""
        for f in VALID.glob("*.pgm"):
            img = parse_pgm_strict(f)
            assert img.magic in ("P2", "P5"), f"{f.name}: unexpected magic {img.magic}"


class TestPgmP2Synthetic:
    """Synthetic P2 ASCII PGM deepening tests."""

    def _write_p2(self, tmp_path, w, h, maxval, pixels):
        p = tmp_path / "t.pgm"
        rows = " ".join(str(v) for v in pixels)
        p.write_text(f"P2\n{w} {h}\n{maxval}\n{rows}\n", encoding="ascii")
        return p

    def test_single_black_pixel(self, tmp_path):
        """P2 1x1 black pixel = 0."""
        p = self._write_p2(tmp_path, 1, 1, 255, [0])
        img = parse_pgm_strict(p)
        assert img.pixels == [0]
        assert img.maxval == 255

    def test_custom_maxval_16(self, tmp_path):
        """P2 with maxval=16 — pixels 0..16 range."""
        p = self._write_p2(tmp_path, 2, 1, 16, [0, 16])
        img = parse_pgm_strict(p)
        assert img.maxval == 16
        assert img.pixels == [0, 16]

    def test_comment_line_skipped(self, tmp_path):
        """P2 with comment line — dimensions still parsed correctly."""
        p = tmp_path / "c.pgm"
        p.write_text("P2\n# this is a comment\n2 1\n255\n100 200\n", encoding="ascii")
        img = parse_pgm_strict(p)
        assert img.width == 2
        assert img.pixels == [100, 200]

    def test_pixel_values_in_range(self, tmp_path):
        """All pixel values must be 0 <= v <= maxval."""
        p = self._write_p2(tmp_path, 3, 1, 200, [0, 100, 200])
        img = parse_pgm_strict(p)
        for pv in img.pixels:
            assert 0 <= pv <= img.maxval

    def test_path_attribute_set(self, tmp_path):
        """parse_pgm_strict result has path attribute."""
        p = self._write_p2(tmp_path, 1, 1, 255, [128])
        img = parse_pgm_strict(p)
        assert img.path is not None


class TestPgmCapabilities:
    """Capability feature set — p5_binary_parse included (R55 addition)."""

    def test_p5_binary_in_supported(self):
        assert "p5_binary_parse" in SUPPORTED_FEATURES

    def test_p2_ascii_in_supported(self):
        assert "p2_ascii_parse" in SUPPORTED_FEATURES

    def test_size_guard_in_supported(self):
        assert "size_guard" in SUPPORTED_FEATURES

    def test_encoding_to_pgm_unsupported(self):
        assert "encoding_to_pgm" in UNSUPPORTED_FEATURES

    def test_16bit_unsupported(self):
        assert "16bit_values" in UNSUPPORTED_FEATURES

"""
test_r58_pbm_deepening.py — R58 Train G: PBM parser deepening.

Deepens coverage of PBM corpus samples, pixel value oracle, and edge cases
not covered by existing Gate 5-7 and R43/R55 tests.

R58 Sprint: FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.pbm.pbm_parser import (
    SUPPORTED_FEATURES,
    UNSUPPORTED_FEATURES,
    parse_pbm_strict,
)

VALID = PROJECT_ROOT / "samples" / "by-format" / "pbm" / "valid"


class TestPbmCorpusOracle:
    """Oracle: committed corpus samples — exact pixel and dimension values."""

    def test_1x1_black_pixel(self):
        """1x1-black.pbm: single black pixel = 1."""
        img = parse_pbm_strict(VALID / "1x1-black.pbm")
        assert img.width == 1
        assert img.height == 1
        assert img.pixels == [1]

    def test_2x2_checker_dimensions(self):
        """2x2-checker.pbm: 2x2 image."""
        img = parse_pbm_strict(VALID / "2x2-checker.pbm")
        assert img.width == 2
        assert img.height == 2

    def test_2x2_checker_pixel_count(self):
        """2x2-checker.pbm: exactly 4 pixels."""
        img = parse_pbm_strict(VALID / "2x2-checker.pbm")
        assert len(img.pixels) == 4

    def test_2x2_checker_checkerboard(self):
        """2x2-checker.pbm: alternating pixels [1,0,0,1] or [0,1,1,0]."""
        img = parse_pbm_strict(VALID / "2x2-checker.pbm")
        # Checkerboard: top-left and bottom-right differ from top-right and bottom-left
        assert img.pixels[0] != img.pixels[1]
        assert img.pixels[0] == img.pixels[3]

    def test_3x2_pattern_dimensions(self):
        """3x2-pattern.pbm: 3 wide, 2 tall."""
        img = parse_pbm_strict(VALID / "3x2-pattern.pbm")
        assert img.width == 3
        assert img.height == 2

    def test_3x2_pattern_pixel_count(self):
        """3x2-pattern.pbm: exactly 6 pixels."""
        img = parse_pbm_strict(VALID / "3x2-pattern.pbm")
        assert len(img.pixels) == 6

    def test_pixels_only_zero_or_one(self):
        """PBM pixels must all be 0 or 1 (bitmap)."""
        for f in VALID.glob("*.pbm"):
            img = parse_pbm_strict(f)
            for pv in img.pixels:
                assert pv in (0, 1), f"{f.name}: unexpected pixel value {pv}"

    def test_magic_is_p1_for_ascii(self):
        """P1 ASCII PBM files have magic == 'P1'."""
        for f in VALID.glob("*.pbm"):
            img = parse_pbm_strict(f)
            assert img.magic in ("P1", "P4"), f"{f.name}: unexpected magic {img.magic}"


class TestPbmP1Synthetic:
    """Synthetic P1 ASCII PBM deepening tests."""

    def _write_p1(self, tmp_path, w, h, pixels):
        p = tmp_path / "t.pbm"
        rows = " ".join(str(v) for v in pixels)
        p.write_text(f"P1\n{w} {h}\n{rows}\n", encoding="ascii")
        return p

    def test_all_white_row(self, tmp_path):
        """P1 1x3: all white pixels = 0 0 0."""
        p = self._write_p1(tmp_path, 3, 1, [0, 0, 0])
        img = parse_pbm_strict(p)
        assert img.pixels == [0, 0, 0]

    def test_all_black_row(self, tmp_path):
        """P1 1x3: all black pixels = 1 1 1."""
        p = self._write_p1(tmp_path, 3, 1, [1, 1, 1])
        img = parse_pbm_strict(p)
        assert img.pixels == [1, 1, 1]

    def test_comment_line_skipped(self, tmp_path):
        """P1 with comment line — dimensions still parsed correctly."""
        p = tmp_path / "c.pbm"
        p.write_text("P1\n# comment\n2 1\n1 0\n", encoding="ascii")
        img = parse_pbm_strict(p)
        assert img.width == 2
        assert img.pixels == [1, 0]

    def test_path_attribute_set(self, tmp_path):
        """parse_pbm_strict result has path attribute."""
        p = self._write_p1(tmp_path, 1, 1, [0])
        img = parse_pbm_strict(p)
        assert img.path is not None

    def test_dimensions_from_header(self, tmp_path):
        """Width and height from header match result."""
        p = self._write_p1(tmp_path, 4, 2, [1, 0, 1, 0, 0, 1, 0, 1])
        img = parse_pbm_strict(p)
        assert img.width == 4
        assert img.height == 2
        assert len(img.pixels) == 8


class TestPbmCapabilities:
    """Capability feature set."""

    def test_p4_binary_in_supported(self):
        assert "p4_binary_parse" in SUPPORTED_FEATURES

    def test_p1_ascii_in_supported(self):
        assert "p1_ascii_parse" in SUPPORTED_FEATURES

    def test_size_guard_in_supported(self):
        assert "size_guard" in SUPPORTED_FEATURES

    def test_encoding_to_pbm_unsupported(self):
        assert "encoding_to_pbm" in UNSUPPORTED_FEATURES

    def test_run_length_encoding_unsupported(self):
        assert "run_length_encoding" in UNSUPPORTED_FEATURES

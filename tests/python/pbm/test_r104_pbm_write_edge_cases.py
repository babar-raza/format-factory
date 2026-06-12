# R104 Wave 2: PBM write edge cases and large image robustness
# Lane E — Python Netpbm FOSS hardening
# Ledger: R104-FOSS-PBM-WRITE-EDGE-CASES-001

import pytest
from pbm.pbm_parser import (
    write_pbm,
    parse_pbm_strict,
    PbmSizeError,
    MAX_DIMENSION,
)


class TestWritePbmEdgeCases:
    """Edge cases for write_pbm P1 output."""

    def test_1x1_white(self, tmp_path):
        p = tmp_path / "1x1w.pbm"
        write_pbm([0], 1, 1, str(p))
        img = parse_pbm_strict(str(p))
        assert img.width == 1
        assert img.height == 1
        assert img.pixels == [0]

    def test_1x1_black(self, tmp_path):
        p = tmp_path / "1x1b.pbm"
        write_pbm([1], 1, 1, str(p))
        img = parse_pbm_strict(str(p))
        assert img.pixels == [1]

    def test_wide_image_100x1(self, tmp_path):
        p = tmp_path / "wide.pbm"
        pixels = [i % 2 for i in range(100)]
        write_pbm(pixels, 100, 1, str(p))
        img = parse_pbm_strict(str(p))
        assert img.width == 100
        assert img.height == 1
        assert img.pixels == pixels

    def test_tall_image_1x100(self, tmp_path):
        p = tmp_path / "tall.pbm"
        pixels = [i % 2 for i in range(100)]
        write_pbm(pixels, 1, 100, str(p))
        img = parse_pbm_strict(str(p))
        assert img.width == 1
        assert img.height == 100
        assert img.pixels == pixels

    def test_all_white(self, tmp_path):
        p = tmp_path / "white.pbm"
        write_pbm([0] * 25, 5, 5, str(p))
        img = parse_pbm_strict(str(p))
        assert all(px == 0 for px in img.pixels)

    def test_all_black(self, tmp_path):
        p = tmp_path / "black.pbm"
        write_pbm([1] * 25, 5, 5, str(p))
        img = parse_pbm_strict(str(p))
        assert all(px == 1 for px in img.pixels)

    def test_checkerboard_4x4(self, tmp_path):
        p = tmp_path / "checker.pbm"
        pixels = []
        for r in range(4):
            for c in range(4):
                pixels.append((r + c) % 2)
        write_pbm(pixels, 4, 4, str(p))
        img = parse_pbm_strict(str(p))
        assert img.pixels == pixels

    def test_comment_preserved_in_file(self, tmp_path):
        p = tmp_path / "comment.pbm"
        write_pbm([0, 1, 1, 0], 2, 2, str(p), comment="test comment")
        content = p.read_text()
        assert "# test comment" in content
        img = parse_pbm_strict(str(p))
        assert img.pixels == [0, 1, 1, 0]

    def test_comment_newline_sanitized(self, tmp_path):
        p = tmp_path / "sanitized.pbm"
        write_pbm([0], 1, 1, str(p), comment="line1\nline2")
        content = p.read_text()
        assert "\nline2" not in content.split("#")[1].split("\n")[0]

    def test_nonzero_clamped_to_1(self, tmp_path):
        p = tmp_path / "clamp.pbm"
        write_pbm([0, 5, 255, 0], 2, 2, str(p))
        img = parse_pbm_strict(str(p))
        assert img.pixels == [0, 1, 1, 0]


class TestWritePbmValidation:
    """Validation errors for write_pbm."""

    def test_pixel_count_mismatch(self, tmp_path):
        with pytest.raises(ValueError, match="does not match"):
            write_pbm([0, 1], 3, 3, str(tmp_path / "bad.pbm"))

    def test_dimension_exceeds_max(self, tmp_path):
        with pytest.raises(PbmSizeError, match="exceeds limit"):
            write_pbm([0], MAX_DIMENSION + 1, 1, str(tmp_path / "big.pbm"))


class TestLargeImage:
    """Larger image roundtrip (not MAX_DIMENSION, but significant)."""

    def test_256x256_roundtrip(self, tmp_path):
        w, h = 256, 256
        pixels = [(r * w + c) % 2 for r in range(h) for c in range(w)]
        p = tmp_path / "large.pbm"
        write_pbm(pixels, w, h, str(p))
        img = parse_pbm_strict(str(p))
        assert img.width == w
        assert img.height == h
        assert img.pixels == pixels

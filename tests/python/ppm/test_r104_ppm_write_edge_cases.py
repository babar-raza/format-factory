# R104 Wave 2: PPM write edge cases and channel verification
# Lane E — Python Netpbm FOSS hardening
# Ledger: R104-FOSS-PPM-WRITE-EDGE-CASES-001

import pytest
from ppm.ppm_parser import (
    write_ppm,
    parse_ppm_strict,
    PpmSizeError,
    MAX_DIMENSION,
    MAX_MAXVAL,
)


class TestWritePpmEdgeCases:
    """Edge cases for write_ppm P3 output."""

    def test_1x1_red(self, tmp_path):
        p = tmp_path / "red.ppm"
        write_ppm([(255, 0, 0)], 1, 1, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert img.pixels == [(255, 0, 0)]

    def test_1x1_white(self, tmp_path):
        p = tmp_path / "white.ppm"
        write_ppm([(255, 255, 255)], 1, 1, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert img.pixels == [(255, 255, 255)]

    def test_1x1_black(self, tmp_path):
        p = tmp_path / "black.ppm"
        write_ppm([(0, 0, 0)], 1, 1, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert img.pixels == [(0, 0, 0)]

    def test_2x2_mixed_colors(self, tmp_path):
        p = tmp_path / "mixed.ppm"
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]
        write_ppm(pixels, 2, 2, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert img.pixels == pixels

    def test_wide_image_10x1(self, tmp_path):
        p = tmp_path / "wide.ppm"
        pixels = [(i * 25, 255 - i * 25, 128) for i in range(10)]
        write_ppm(pixels, 10, 1, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert img.width == 10
        assert img.height == 1
        assert img.pixels == pixels

    def test_tall_image_1x10(self, tmp_path):
        p = tmp_path / "tall.ppm"
        pixels = [(i * 25, i * 25, i * 25) for i in range(10)]
        write_ppm(pixels, 1, 10, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert img.width == 1
        assert img.height == 10

    def test_comment_in_file(self, tmp_path):
        p = tmp_path / "comment.ppm"
        write_ppm([(100, 200, 50)], 1, 1, 255, str(p), comment="test")
        content = p.read_text()
        assert "# test" in content
        img = parse_ppm_strict(str(p))
        assert img.pixels == [(100, 200, 50)]

    def test_maxval_1_binary_image(self, tmp_path):
        p = tmp_path / "binary.ppm"
        pixels = [(0, 0, 0), (1, 1, 1), (1, 0, 1), (0, 1, 0)]
        write_ppm(pixels, 2, 2, 1, str(p))
        img = parse_ppm_strict(str(p))
        assert img.maxval == 1
        assert img.pixels == pixels

    def test_high_maxval_roundtrip(self, tmp_path):
        p = tmp_path / "high.ppm"
        pixels = [(1000, 2000, 3000)]
        write_ppm(pixels, 1, 1, 4000, str(p))
        img = parse_ppm_strict(str(p))
        assert img.maxval == 4000
        assert img.pixels == pixels


class TestWritePpmValidation:
    """Validation errors for write_ppm."""

    def test_pixel_count_mismatch(self, tmp_path):
        with pytest.raises(ValueError, match="does not match"):
            write_ppm([(0, 0, 0)], 2, 2, 255, str(tmp_path / "bad.ppm"))

    def test_maxval_zero_raises(self, tmp_path):
        with pytest.raises(ValueError, match="maxval"):
            write_ppm([(0, 0, 0)], 1, 1, 0, str(tmp_path / "bad.ppm"))

    def test_maxval_exceeds_max(self, tmp_path):
        with pytest.raises(ValueError, match="maxval"):
            write_ppm([(0, 0, 0)], 1, 1, MAX_MAXVAL + 1, str(tmp_path / "bad.ppm"))

    def test_channel_exceeds_maxval(self, tmp_path):
        with pytest.raises(ValueError, match="out of range"):
            write_ppm([(256, 0, 0)], 1, 1, 255, str(tmp_path / "bad.ppm"))

    def test_negative_dimension(self, tmp_path):
        with pytest.raises(ValueError, match="positive"):
            write_ppm([], 0, 1, 255, str(tmp_path / "bad.ppm"))

    def test_dimension_exceeds_max(self, tmp_path):
        with pytest.raises(PpmSizeError, match="exceeds limit"):
            write_ppm([(0, 0, 0)], MAX_DIMENSION + 1, 1, 255, str(tmp_path / "big.ppm"))


class TestLargeImageRoundtrip:
    """Moderate-size image roundtrip."""

    def test_64x64_gradient(self, tmp_path):
        w, h = 64, 64
        pixels = [(r * 4, c * 4, (r + c) * 2) for r in range(h) for c in range(w)]
        p = tmp_path / "gradient.ppm"
        write_ppm(pixels, w, h, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert img.width == w
        assert img.height == h
        assert img.pixels == pixels

# R105 Wave 3: PGM write roundtrip with maxval variation and comment preservation
# Lane E — Python Netpbm FOSS
# Ledger: R105-FOSS-PGM-WRITE-HARDENING-001

import pytest
from pgm.pgm_parser import (
    write_pgm,
    parse_pgm_strict,
    PgmSizeError,
    MAX_DIMENSION,
)


class TestWritePgmRoundtrip:
    """PGM P2 write/parse roundtrip tests."""

    def test_1x1_roundtrip(self, tmp_path):
        p = tmp_path / "1x1.pgm"
        write_pgm([128], 1, 1, 255, str(p))
        img = parse_pgm_strict(str(p))
        assert img.width == 1
        assert img.height == 1
        assert img.pixels == [128]

    def test_gradient_roundtrip(self, tmp_path):
        pixels = list(range(256))
        p = tmp_path / "gradient.pgm"
        write_pgm(pixels, 16, 16, 255, str(p))
        img = parse_pgm_strict(str(p))
        assert img.pixels == pixels

    def test_maxval_15(self, tmp_path):
        pixels = [0, 5, 10, 15]
        p = tmp_path / "low_maxval.pgm"
        write_pgm(pixels, 2, 2, 15, str(p))
        img = parse_pgm_strict(str(p))
        assert img.maxval == 15
        assert img.pixels == pixels

    def test_maxval_1(self, tmp_path):
        pixels = [0, 1, 1, 0]
        p = tmp_path / "binary.pgm"
        write_pgm(pixels, 2, 2, 1, str(p))
        img = parse_pgm_strict(str(p))
        assert img.maxval == 1
        assert img.pixels == pixels

    def test_all_zeros(self, tmp_path):
        pixels = [0] * 16
        p = tmp_path / "zeros.pgm"
        write_pgm(pixels, 4, 4, 255, str(p))
        img = parse_pgm_strict(str(p))
        assert all(px == 0 for px in img.pixels)

    def test_all_max(self, tmp_path):
        pixels = [255] * 16
        p = tmp_path / "max.pgm"
        write_pgm(pixels, 4, 4, 255, str(p))
        img = parse_pgm_strict(str(p))
        assert all(px == 255 for px in img.pixels)

    def test_comment_in_file(self, tmp_path):
        p = tmp_path / "comment.pgm"
        write_pgm([100, 200], 2, 1, 255, str(p), comment="test comment")
        content = p.read_text()
        assert "# test comment" in content
        img = parse_pgm_strict(str(p))
        assert img.pixels == [100, 200]

    def test_wide_image(self, tmp_path):
        pixels = list(range(100))
        p = tmp_path / "wide.pgm"
        write_pgm(pixels, 100, 1, 255, str(p))
        img = parse_pgm_strict(str(p))
        assert img.width == 100
        assert img.pixels == pixels

    def test_tall_image(self, tmp_path):
        pixels = [i % 256 for i in range(100)]
        p = tmp_path / "tall.pgm"
        write_pgm(pixels, 1, 100, 255, str(p))
        img = parse_pgm_strict(str(p))
        assert img.height == 100

    def test_128x128_roundtrip(self, tmp_path):
        w, h = 128, 128
        pixels = [(r * w + c) % 256 for r in range(h) for c in range(w)]
        p = tmp_path / "large.pgm"
        write_pgm(pixels, w, h, 255, str(p))
        img = parse_pgm_strict(str(p))
        assert img.pixels == pixels


class TestWritePgmValidation:
    """Validation errors for write_pgm."""

    def test_pixel_count_mismatch(self, tmp_path):
        with pytest.raises(ValueError, match="does not match"):
            write_pgm([0, 1], 3, 3, 255, str(tmp_path / "bad.pgm"))

    def test_dimension_exceeds_max(self, tmp_path):
        with pytest.raises(PgmSizeError):
            write_pgm([0], MAX_DIMENSION + 1, 1, 255, str(tmp_path / "big.pgm"))

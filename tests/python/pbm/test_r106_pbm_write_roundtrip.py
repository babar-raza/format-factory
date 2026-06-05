# R106 Wave 3: PBM write roundtrip proof
# Lane E — Python Netpbm FOSS
# Ledger: R106-FOSS-PBM-WRITE-ROUNDTRIP-001

import pytest
from pbm.pbm_parser import parse_pbm_strict, write_pbm, PbmError


class TestPbmWriteRoundtrip:
    """PBM P1 write/parse roundtrip tests."""

    def test_1x1_white(self, tmp_path):
        p = tmp_path / "w.pbm"
        write_pbm([0], 1, 1, str(p))
        img = parse_pbm_strict(str(p))
        assert img.pixels == [0]

    def test_1x1_black(self, tmp_path):
        p = tmp_path / "b.pbm"
        write_pbm([1], 1, 1, str(p))
        img = parse_pbm_strict(str(p))
        assert img.pixels == [1]

    def test_2x2_checkerboard(self, tmp_path):
        pixels = [0, 1, 1, 0]
        p = tmp_path / "check.pbm"
        write_pbm(pixels, 2, 2, str(p))
        img = parse_pbm_strict(str(p))
        assert img.pixels == pixels

    def test_all_white(self, tmp_path):
        pixels = [0] * 16
        p = tmp_path / "white.pbm"
        write_pbm(pixels, 4, 4, str(p))
        img = parse_pbm_strict(str(p))
        assert all(px == 0 for px in img.pixels)

    def test_all_black(self, tmp_path):
        pixels = [1] * 16
        p = tmp_path / "black.pbm"
        write_pbm(pixels, 4, 4, str(p))
        img = parse_pbm_strict(str(p))
        assert all(px == 1 for px in img.pixels)

    def test_wide_image(self, tmp_path):
        pixels = [i % 2 for i in range(100)]
        p = tmp_path / "wide.pbm"
        write_pbm(pixels, 100, 1, str(p))
        img = parse_pbm_strict(str(p))
        assert img.pixels == pixels

    def test_tall_image(self, tmp_path):
        pixels = [i % 2 for i in range(100)]
        p = tmp_path / "tall.pbm"
        write_pbm(pixels, 1, 100, str(p))
        img = parse_pbm_strict(str(p))
        assert img.pixels == pixels

    def test_large_checkerboard(self, tmp_path):
        w, h = 64, 64
        pixels = [(r + c) % 2 for r in range(h) for c in range(w)]
        p = tmp_path / "large.pbm"
        write_pbm(pixels, w, h, str(p))
        img = parse_pbm_strict(str(p))
        assert img.pixels == pixels

    def test_pixel_count_mismatch_raises(self, tmp_path):
        with pytest.raises((ValueError, PbmError)):
            write_pbm([0, 1], 3, 3, str(tmp_path / "bad.pbm"))

    def test_file_starts_with_p1(self, tmp_path):
        p = tmp_path / "magic.pbm"
        write_pbm([0], 1, 1, str(p))
        content = p.read_text()
        assert content.startswith("P1")

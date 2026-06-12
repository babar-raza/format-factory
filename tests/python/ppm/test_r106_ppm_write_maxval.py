# R106 Wave 3: PPM write roundtrip with maxval variation
# Lane E — Python Netpbm FOSS
# Ledger: R106-FOSS-PPM-WRITE-MAXVAL-001

from ppm.ppm_parser import write_ppm, parse_ppm_strict


class TestPpmWriteMaxval:
    """PPM P3 write/parse roundtrip with varied maxval."""

    def test_maxval_255_roundtrip(self, tmp_path):
        p = tmp_path / "m255.ppm"
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]
        write_ppm(pixels, 2, 2, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert img.pixels == pixels

    def test_maxval_15_roundtrip(self, tmp_path):
        p = tmp_path / "m15.ppm"
        pixels = [(0, 0, 0), (15, 15, 15), (7, 3, 12), (1, 2, 3)]
        write_ppm(pixels, 2, 2, 15, str(p))
        img = parse_ppm_strict(str(p))
        assert img.maxval == 15
        assert img.pixels == pixels

    def test_maxval_1_roundtrip(self, tmp_path):
        p = tmp_path / "m1.ppm"
        pixels = [(0, 0, 0), (1, 1, 1)]
        write_ppm(pixels, 2, 1, 1, str(p))
        img = parse_ppm_strict(str(p))
        assert img.maxval == 1

    def test_single_pixel(self, tmp_path):
        p = tmp_path / "single.ppm"
        pixels = [(42, 84, 126)]
        write_ppm(pixels, 1, 1, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert img.pixels[0] == (42, 84, 126)

    def test_large_image(self, tmp_path):
        p = tmp_path / "large.ppm"
        w, h = 50, 50
        pixels = [(r % 256, c % 256, (r + c) % 256) for r in range(h) for c in range(w)]
        write_ppm(pixels, w, h, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert len(img.pixels) == 2500
        assert img.pixels[0] == pixels[0]

    def test_all_black(self, tmp_path):
        p = tmp_path / "black.ppm"
        pixels = [(0, 0, 0)] * 9
        write_ppm(pixels, 3, 3, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert all(px == (0, 0, 0) for px in img.pixels)

    def test_all_white(self, tmp_path):
        p = tmp_path / "white.ppm"
        pixels = [(255, 255, 255)] * 9
        write_ppm(pixels, 3, 3, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert all(px == (255, 255, 255) for px in img.pixels)

    def test_file_starts_with_p3(self, tmp_path):
        p = tmp_path / "magic.ppm"
        write_ppm([(0, 0, 0)], 1, 1, 255, str(p))
        content = p.read_text()
        assert content.startswith("P3")

    def test_gradient_roundtrip(self, tmp_path):
        p = tmp_path / "grad.ppm"
        pixels = [(i, 0, 255 - i) for i in range(10)]
        write_ppm(pixels, 10, 1, 255, str(p))
        img = parse_ppm_strict(str(p))
        for i, px in enumerate(img.pixels):
            assert px[0] == i

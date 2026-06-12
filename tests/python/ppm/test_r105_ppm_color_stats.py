# R105 Wave 3: PPM color statistics and channel hardening
# Lane E — Python Netpbm FOSS
# Ledger: R105-FOSS-PPM-COLOR-STATS-001

from ppm.ppm_parser import (
    write_ppm,
    parse_ppm_strict,
)


class TestPpmColorProperties:
    """Verify PPM image color properties after write/parse."""

    def test_pure_red(self, tmp_path):
        p = tmp_path / "red.ppm"
        pixels = [(255, 0, 0)] * 4
        write_ppm(pixels, 2, 2, 255, str(p))
        img = parse_ppm_strict(str(p))
        for px in img.pixels:
            assert px[0] == 255
            assert px[1] == 0
            assert px[2] == 0

    def test_pure_green(self, tmp_path):
        p = tmp_path / "green.ppm"
        pixels = [(0, 255, 0)] * 4
        write_ppm(pixels, 2, 2, 255, str(p))
        img = parse_ppm_strict(str(p))
        for px in img.pixels:
            assert px[1] == 255

    def test_pure_blue(self, tmp_path):
        p = tmp_path / "blue.ppm"
        pixels = [(0, 0, 255)] * 4
        write_ppm(pixels, 2, 2, 255, str(p))
        img = parse_ppm_strict(str(p))
        for px in img.pixels:
            assert px[2] == 255

    def test_grayscale_uniform(self, tmp_path):
        p = tmp_path / "gray.ppm"
        pixels = [(128, 128, 128)] * 9
        write_ppm(pixels, 3, 3, 255, str(p))
        img = parse_ppm_strict(str(p))
        for px in img.pixels:
            assert px[0] == px[1] == px[2] == 128

    def test_gradient_red_channel(self, tmp_path):
        p = tmp_path / "grad.ppm"
        pixels = [(i * 25, 0, 0) for i in range(10)]
        write_ppm(pixels, 10, 1, 255, str(p))
        img = parse_ppm_strict(str(p))
        for i, px in enumerate(img.pixels):
            assert px[0] == i * 25

    def test_max_channel_values(self, tmp_path):
        p = tmp_path / "max.ppm"
        pixels = [(255, 255, 255)]
        write_ppm(pixels, 1, 1, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert img.pixels[0] == (255, 255, 255)

    def test_min_channel_values(self, tmp_path):
        p = tmp_path / "min.ppm"
        pixels = [(0, 0, 0)]
        write_ppm(pixels, 1, 1, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert img.pixels[0] == (0, 0, 0)

    def test_channel_independence(self, tmp_path):
        p = tmp_path / "indep.ppm"
        pixels = [(100, 0, 0), (0, 100, 0), (0, 0, 100)]
        write_ppm(pixels, 3, 1, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert img.pixels[0] == (100, 0, 0)
        assert img.pixels[1] == (0, 100, 0)
        assert img.pixels[2] == (0, 0, 100)

    def test_pixel_count_matches(self, tmp_path):
        p = tmp_path / "count.ppm"
        pixels = [(i, i, i) for i in range(25)]
        write_ppm(pixels, 5, 5, 255, str(p))
        img = parse_ppm_strict(str(p))
        assert len(img.pixels) == 25

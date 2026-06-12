"""R113 FOSS: PPM grayscale conversion and roundtrip."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from ppm.ppm_parser import parse_ppm, parse_ppm_strict, write_ppm


class TestR113PpmGrayscaleRoundtrip:
    def test_write_read_uniform_color(self):
        pixels = [(100, 100, 100)] * 4
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 2, 2, 255, path)
            img = parse_ppm_strict(path)
            assert all(p == (100, 100, 100) for p in img.pixels)
        finally:
            os.unlink(path)

    def test_write_read_gradient(self):
        pixels = [(i * 25, i * 25, i * 25) for i in range(10)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 5, 2, 255, path)
            result = parse_ppm(path)
            assert result["ok"] is True
            assert result["pixel_count"] == 10
        finally:
            os.unlink(path)

    def test_mixed_colors_roundtrip(self):
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255),
                  (255, 255, 0), (0, 255, 255), (255, 0, 255)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 3, 2, 255, path)
            img = parse_ppm_strict(path)
            for i, px in enumerate(pixels):
                assert img.pixels[i] == px
        finally:
            os.unlink(path)

    def test_single_pixel_colors(self):
        for color in [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0), (255, 255, 255)]:
            pixels = [color]
            with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
                path = f.name
            try:
                write_ppm(pixels, 1, 1, 255, path)
                img = parse_ppm_strict(path)
                assert img.pixels[0] == color
            finally:
                os.unlink(path)

    def test_large_image_roundtrip(self):
        pixels = [(i % 256, (i * 2) % 256, (i * 3) % 256) for i in range(100)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 10, 10, 255, path)
            result = parse_ppm(path)
            assert result["ok"] is True
            assert result["pixel_count"] == 100
        finally:
            os.unlink(path)

    def test_maxval_boundary(self):
        pixels = [(255, 255, 255), (0, 0, 0)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 2, 1, 255, path)
            img = parse_ppm_strict(path)
            assert img.maxval == 255
        finally:
            os.unlink(path)

    def test_file_is_valid_p3_format(self):
        pixels = [(1, 2, 3)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 1, 1, 255, path)
            with open(path, "r") as f:
                content = f.read()
            assert content.startswith("P3")
            assert "255" in content
        finally:
            os.unlink(path)

    def test_write_read_wide_image(self):
        pixels = [(50, 100, 150)] * 20
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 20, 1, 255, path)
            result = parse_ppm(path)
            assert result["width"] == 20
            assert result["height"] == 1
        finally:
            os.unlink(path)

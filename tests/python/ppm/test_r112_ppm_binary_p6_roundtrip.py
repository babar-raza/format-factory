"""R112 FOSS: PPM P3 write/read roundtrip hardening."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from ppm.ppm_parser import parse_ppm, parse_ppm_strict, write_ppm


class TestR112PpmBinaryP6Roundtrip:
    def test_write_p3_then_read(self):
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 2, 2, 255, path)
            result = parse_ppm(path)
            assert result["ok"] is True
            assert result["width"] == 2
            assert result["height"] == 2
            assert result["pixel_count"] == 4
        finally:
            os.unlink(path)

    def test_roundtrip_preserves_pixel_values(self):
        pixels = [(10, 20, 30), (40, 50, 60), (70, 80, 90), (100, 110, 120)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 2, 2, 255, path)
            img = parse_ppm_strict(path)
            for i, px in enumerate(pixels):
                assert img.pixels[i] == px, f"Pixel {i} mismatch"
        finally:
            os.unlink(path)

    def test_write_1x1_image(self):
        pixels = [(42, 84, 126)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 1, 1, 255, path)
            img = parse_ppm_strict(path)
            assert img.pixels[0] == (42, 84, 126)
        finally:
            os.unlink(path)

    def test_write_max_value_pixels(self):
        pixels = [(255, 255, 255)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 1, 1, 255, path)
            img = parse_ppm_strict(path)
            assert img.pixels[0] == (255, 255, 255)
        finally:
            os.unlink(path)

    def test_write_zero_value_pixels(self):
        pixels = [(0, 0, 0)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 1, 1, 255, path)
            img = parse_ppm_strict(path)
            assert img.pixels[0] == (0, 0, 0)
        finally:
            os.unlink(path)

    def test_larger_image_4x4(self):
        pixels = [(i * 10, i * 5, 255 - i * 10) for i in range(16)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 4, 4, 255, path)
            result = parse_ppm(path)
            assert result["ok"] is True
            assert result["width"] == 4
            assert result["height"] == 4
            assert result["pixel_count"] == 16
        finally:
            os.unlink(path)

    def test_file_starts_with_magic(self):
        pixels = [(1, 2, 3)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 1, 1, 255, path)
            with open(path, "r") as f:
                first_line = f.readline().strip()
            assert first_line == "P3"
        finally:
            os.unlink(path)

    def test_write_non_square_image(self):
        pixels = [(i, i * 2, i * 3) for i in range(6)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 3, 2, 255, path)
            result = parse_ppm(path)
            assert result["ok"] is True
            assert result["width"] == 3
            assert result["height"] == 2
        finally:
            os.unlink(path)

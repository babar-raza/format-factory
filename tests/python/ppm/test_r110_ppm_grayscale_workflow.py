# R110 Wave 5: PPM Grayscale Workflow Tests
# FOSS depth: write→read→verify pixel values (workflow)

import os
import tempfile
import ppm


class TestR110PpmGrayscaleWorkflow:
    """PPM write→read→verify workflow tests."""

    def test_write_read_roundtrip_basic(self):
        """Write a PPM file and read it back, verify dimensions."""
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            ppm.write_ppm(pixels, 3, 1, 255, path)
            result = ppm.parse_ppm(path)
            assert result["ok"] is True
            assert result["width"] == 3
            assert result["height"] == 1
        finally:
            os.unlink(path)

    def test_write_read_dimensions_2x2(self):
        """Write 2x2 PPM and verify dimensions."""
        pixels = [(128, 128, 128)] * 4
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            ppm.write_ppm(pixels, 2, 2, 255, path)
            result = ppm.parse_ppm(path)
            assert result["width"] == 2
            assert result["height"] == 2
            assert result["pixel_count"] == 4
        finally:
            os.unlink(path)

    def test_write_read_maxval_preserved(self):
        """Write with maxval=255 and verify on read."""
        pixels = [(255, 255, 255)] * 6
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            ppm.write_ppm(pixels, 3, 2, 255, path)
            result = ppm.parse_ppm(path)
            assert result["maxval"] == 255
        finally:
            os.unlink(path)

    def test_write_creates_file(self):
        """write_ppm creates a file on disk."""
        pixels = [(100, 100, 100)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            ppm.write_ppm(pixels, 1, 1, 255, path)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0
        finally:
            os.unlink(path)

    def test_probe_written_file(self):
        """probe_ppm returns valid info for a written file."""
        pixels = [(50, 100, 150)] * 4
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            ppm.write_ppm(pixels, 2, 2, 255, path)
            info = ppm.probe_ppm(path)
            assert isinstance(info, dict)
            assert info.get("width") == 2
            assert info.get("height") == 2
        finally:
            os.unlink(path)

    def test_write_pixel_count_correct(self):
        """Written file has correct pixel count."""
        pixels = [(10, 20, 30)] * 12
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            ppm.write_ppm(pixels, 4, 3, 255, path)
            result = ppm.parse_ppm(path)
            assert result["pixel_count"] == 12
        finally:
            os.unlink(path)

    def test_write_magic_is_p3_or_p6(self):
        """Written file uses P3 or P6 magic."""
        pixels = [(0, 0, 0)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            ppm.write_ppm(pixels, 1, 1, 255, path)
            result = ppm.parse_ppm(path)
            assert result["magic"] in ("P3", "P6")
        finally:
            os.unlink(path)

    def test_write_overwrite_existing(self):
        """Writing to same path overwrites file."""
        pixels1 = [(100, 0, 0)]
        pixels2 = [(0, 100, 0)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            ppm.write_ppm(pixels1, 1, 1, 255, path)
            ppm.write_ppm(pixels2, 1, 1, 255, path)
            result = ppm.parse_ppm(path)
            assert result["ok"] is True
        finally:
            os.unlink(path)

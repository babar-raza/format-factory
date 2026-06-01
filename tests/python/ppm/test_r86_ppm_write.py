"""
test_r86_ppm_write.py — Tests for write_ppm (P3 ASCII PPM writer)

Sprint: FORMAT-FACTORY-R86-SUPERVISOR-TRUTH-POC-PRODUCT-FACTORY-DEEPENING-NETPBM-FODS-FODT-FOSS-DOGFOOD-MEGA-TRAIN-001
Train K: Netpbm Python deepening — write_ppm
"""

import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from ppm.ppm_parser import write_ppm, parse_ppm_strict, PpmSizeError


class TestWritePpmBasic:
    """Basic write_ppm functionality."""

    def test_single_red_pixel(self):
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm([(255, 0, 0)], 1, 1, 255, path)
            img = parse_ppm_strict(path)
            assert img.width == 1
            assert img.height == 1
            assert img.pixels == [(255, 0, 0)]
        finally:
            Path(path).unlink(missing_ok=True)

    def test_roundtrip_2x2(self):
        pixels = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (128, 128, 128)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 2, 2, 255, path)
            img = parse_ppm_strict(path)
            assert img.width == 2
            assert img.height == 2
            assert img.pixels == pixels
        finally:
            Path(path).unlink(missing_ok=True)

    def test_custom_maxval(self):
        pixels = [(100, 50, 75)]
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 1, 1, 200, path)
            img = parse_ppm_strict(path)
            assert img.maxval == 200
            assert img.pixels == [(100, 50, 75)]
        finally:
            Path(path).unlink(missing_ok=True)

    def test_comment_preserved_in_output(self):
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm([(0, 0, 0)], 1, 1, 255, path, comment="test comment")
            content = Path(path).read_text(encoding="ascii")
            assert "# test comment" in content
        finally:
            Path(path).unlink(missing_ok=True)

    def test_output_starts_with_p3(self):
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm([(0, 0, 0)], 1, 1, 255, path)
            content = Path(path).read_text(encoding="ascii")
            assert content.startswith("P3\n")
        finally:
            Path(path).unlink(missing_ok=True)


class TestWritePpmValidation:
    """Validation and error handling for write_ppm."""

    def test_pixel_count_mismatch_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            with pytest.raises(ValueError, match="does not match"):
                write_ppm([(0, 0, 0)], 2, 2, 255, path)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_maxval_zero_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            with pytest.raises(ValueError, match="maxval"):
                write_ppm([(0, 0, 0)], 1, 1, 0, path)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_maxval_too_large_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            with pytest.raises(ValueError, match="maxval"):
                write_ppm([(0, 0, 0)], 1, 1, 70000, path)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_oversized_dimension_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            with pytest.raises(PpmSizeError):
                write_ppm([], 100000, 1, 255, path)
        finally:
            Path(path).unlink(missing_ok=True)

    def test_comment_newline_stripped(self):
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm([(0, 0, 0)], 1, 1, 255, path, comment="line1\nline2")
            content = Path(path).read_text(encoding="ascii")
            # Newline in comment should be replaced with space
            assert "# line1 line2" in content
        finally:
            Path(path).unlink(missing_ok=True)


class TestWritePpmLarger:
    """Larger image round-trip tests."""

    def test_3x3_gradient(self):
        pixels = []
        for i in range(9):
            v = i * 28
            pixels.append((v, v, v))
        with tempfile.NamedTemporaryFile(suffix=".ppm", delete=False) as f:
            path = f.name
        try:
            write_ppm(pixels, 3, 3, 255, path)
            img = parse_ppm_strict(path)
            assert img.width == 3
            assert img.height == 3
            assert len(img.pixels) == 9
            assert img.pixels == pixels
        finally:
            Path(path).unlink(missing_ok=True)

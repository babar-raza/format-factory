"""
test_r87_pgm_to_ppm_dogfood.py — Dogfood export tests: PGM to PPM

Sprint: FORMAT-FACTORY-R87-CLEAN-SUPERVISOR-CLOSEOUT-REVIEW-PACKAGE-POC-PRODUCT-FACTORY-DEEPENING-MEGA-TRAIN-001
Train N: PGM to PPM dogfood export using FF write_ppm
Train O: Dogfood enforcement tests
"""

import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from pgm.pgm_to_ppm import convert_pgm_to_ppm, pgm_pixels_to_ppm_pixels
from pgm.pgm_parser import write_pgm
from ppm.ppm_parser import parse_ppm_strict


class TestPgmPixelsToPpmPixels:
    """Test pixel conversion logic."""

    def test_gray_maps_to_equal_rgb(self):
        result = pgm_pixels_to_ppm_pixels([128])
        assert result == [(128, 128, 128)]

    def test_black_maps_to_black_rgb(self):
        result = pgm_pixels_to_ppm_pixels([0])
        assert result == [(0, 0, 0)]

    def test_white_maps_to_white_rgb(self):
        result = pgm_pixels_to_ppm_pixels([255])
        assert result == [(255, 255, 255)]

    def test_gradient(self):
        result = pgm_pixels_to_ppm_pixels([0, 64, 128, 192, 255])
        assert len(result) == 5
        assert result[2] == (128, 128, 128)

    def test_invalid_maxval_raises(self):
        with pytest.raises(ValueError, match="maxval"):
            pgm_pixels_to_ppm_pixels([0], maxval=0)


class TestConvertPgmToPpm:
    """Integration test: full PGM to PPM roundtrip via dogfood."""

    def test_roundtrip_2x2(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pgm_path = Path(tmpdir) / "test.pgm"
            ppm_path = Path(tmpdir) / "test.ppm"

            write_pgm([0, 64, 128, 255], 2, 2, 255, pgm_path)
            result = convert_pgm_to_ppm(pgm_path, ppm_path)

            assert result["status"] == "success"
            assert result["dogfood"] is True
            assert result["width"] == 2
            assert result["height"] == 2

            ppm_img = parse_ppm_strict(ppm_path)
            assert ppm_img.width == 2
            assert ppm_img.height == 2
            # Gray 0 -> (0, 0, 0)
            assert ppm_img.pixels[0] == (0, 0, 0)

    def test_single_pixel(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pgm_path = Path(tmpdir) / "one.pgm"
            ppm_path = Path(tmpdir) / "one.ppm"

            write_pgm([200], 1, 1, 255, pgm_path)
            result = convert_pgm_to_ppm(pgm_path, ppm_path)
            assert result["status"] == "success"

            ppm_img = parse_ppm_strict(ppm_path)
            assert ppm_img.pixels == [(200, 200, 200)]

    def test_output_has_dogfood_comment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pgm_path = Path(tmpdir) / "c.pgm"
            ppm_path = Path(tmpdir) / "c.ppm"

            write_pgm([100], 1, 1, 255, pgm_path)
            convert_pgm_to_ppm(pgm_path, ppm_path)

            content = ppm_path.read_text(encoding="ascii")
            assert "dogfood" in content.lower()


class TestDogfoodEnforcement:
    """Train O: Verify dogfood exports use FF write backends, not external libs."""

    def test_pgm_to_ppm_uses_ff_write_ppm(self):
        """The convert function must import from ppm.ppm_parser.write_ppm (FF library)."""
        import inspect
        from pgm.pgm_to_ppm import convert_pgm_to_ppm
        source = inspect.getsource(convert_pgm_to_ppm)
        assert "write_ppm" in source
        assert "from ppm" in source or "ppm_parser" in source

    def test_pbm_to_ppm_uses_ff_write_ppm(self):
        """Existing dogfood: PBM to PPM must use FF write_ppm."""
        import inspect
        from pbm.pbm_to_ppm import convert_pbm_to_ppm
        source = inspect.getsource(convert_pbm_to_ppm)
        assert "write_ppm" in source

    def test_pbm_to_pgm_uses_ff_write_pgm(self):
        """Existing dogfood: PBM to PGM must use FF write_pgm."""
        import inspect
        from pbm.pbm_to_pgm import convert_pbm_to_pgm
        source = inspect.getsource(convert_pbm_to_pgm)
        assert "write_pgm" in source

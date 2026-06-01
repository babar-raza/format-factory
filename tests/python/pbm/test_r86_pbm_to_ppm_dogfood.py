"""
test_r86_pbm_to_ppm_dogfood.py — Dogfood export tests: PBM → PPM

Sprint: FORMAT-FACTORY-R86-SUPERVISOR-TRUTH-POC-PRODUCT-FACTORY-DEEPENING-NETPBM-FODS-FODT-FOSS-DOGFOOD-MEGA-TRAIN-001
Train M: Close dogfood gap (PBM→PPM using FF write_ppm)
Train N: Dogfood enforcement tests
"""

import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from pbm.pbm_to_ppm import convert_pbm_to_ppm, pbm_pixels_to_ppm_pixels
from pbm.pbm_parser import write_pbm
from ppm.ppm_parser import parse_ppm_strict


class TestPbmPixelsToPpmPixels:
    """Test pixel conversion logic."""

    def test_black_maps_to_zero_rgb(self):
        result = pbm_pixels_to_ppm_pixels([1])
        assert result == [(0, 0, 0)]

    def test_white_maps_to_maxval_rgb(self):
        result = pbm_pixels_to_ppm_pixels([0])
        assert result == [(255, 255, 255)]

    def test_custom_maxval(self):
        result = pbm_pixels_to_ppm_pixels([0, 1], maxval=100)
        assert result == [(100, 100, 100), (0, 0, 0)]

    def test_checkerboard_pattern(self):
        result = pbm_pixels_to_ppm_pixels([0, 1, 1, 0])
        assert result == [(255, 255, 255), (0, 0, 0), (0, 0, 0), (255, 255, 255)]

    def test_invalid_maxval_raises(self):
        with pytest.raises(ValueError, match="maxval"):
            pbm_pixels_to_ppm_pixels([0], maxval=0)


class TestConvertPbmToPpm:
    """Integration test: full PBM → PPM roundtrip via dogfood."""

    def test_roundtrip_2x2(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pbm_path = Path(tmpdir) / "test.pbm"
            ppm_path = Path(tmpdir) / "test.ppm"

            write_pbm([0, 1, 1, 0], 2, 2, pbm_path)
            result = convert_pbm_to_ppm(pbm_path, ppm_path)

            assert result["status"] == "success"
            assert result["dogfood"] is True
            assert result["width"] == 2
            assert result["height"] == 2

            ppm_img = parse_ppm_strict(ppm_path)
            assert ppm_img.width == 2
            assert ppm_img.height == 2
            # White pixel (PBM 0) → (255, 255, 255)
            assert ppm_img.pixels[0] == (255, 255, 255)
            # Black pixel (PBM 1) → (0, 0, 0)
            assert ppm_img.pixels[1] == (0, 0, 0)

    def test_single_pixel(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pbm_path = Path(tmpdir) / "one.pbm"
            ppm_path = Path(tmpdir) / "one.ppm"

            write_pbm([1], 1, 1, pbm_path)
            result = convert_pbm_to_ppm(pbm_path, ppm_path)
            assert result["status"] == "success"

            ppm_img = parse_ppm_strict(ppm_path)
            assert ppm_img.pixels == [(0, 0, 0)]

    def test_output_has_dogfood_comment(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pbm_path = Path(tmpdir) / "c.pbm"
            ppm_path = Path(tmpdir) / "c.ppm"

            write_pbm([0], 1, 1, pbm_path)
            convert_pbm_to_ppm(pbm_path, ppm_path)

            content = ppm_path.read_text(encoding="ascii")
            assert "dogfood" in content.lower()


class TestDogfoodEnforcement:
    """Train N: Verify dogfood exports use FF write backends, not external libs."""

    def test_pbm_to_ppm_uses_ff_write_ppm(self):
        """The convert function must import from ppm.ppm_parser.write_ppm (FF library)."""
        import inspect
        from pbm.pbm_to_ppm import convert_pbm_to_ppm
        source = inspect.getsource(convert_pbm_to_ppm)
        assert "write_ppm" in source
        assert "from ppm" in source or "ppm_parser" in source

    def test_pbm_to_pgm_uses_ff_write_pgm(self):
        """Existing dogfood: PBM→PGM must use FF write_pgm."""
        import inspect
        from pbm.pbm_to_pgm import convert_pbm_to_pgm
        source = inspect.getsource(convert_pbm_to_pgm)
        assert "write_pgm" in source

"""
test_r85_pbm_to_pgm_dogfood.py

R85 Train M + Train P: Python Netpbm dogfood export — PBM→PGM using FF libraries.

dogfood_status: IMPLEMENTED
Uses: format-factory-pbm (parse_pbm_strict) + format-factory-pgm (write_pgm)

Sprint: FORMAT-FACTORY-R85
"""
from __future__ import annotations

import sys
from pathlib import Path
import pytest

# Add src/python to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))


class TestPbmPixelsToPgmPixels:
    """Unit tests for pixel conversion (no file I/O)."""

    def test_black_pixel_maps_to_zero(self):
        from pbm.pbm_to_pgm import pbm_pixels_to_pgm_pixels
        result = pbm_pixels_to_pgm_pixels([1], maxval=255)
        assert result == [0]

    def test_white_pixel_maps_to_maxval(self):
        from pbm.pbm_to_pgm import pbm_pixels_to_pgm_pixels
        result = pbm_pixels_to_pgm_pixels([0], maxval=255)
        assert result == [255]

    def test_mixed_pixels(self):
        from pbm.pbm_to_pgm import pbm_pixels_to_pgm_pixels
        result = pbm_pixels_to_pgm_pixels([0, 1, 0, 1], maxval=255)
        assert result == [255, 0, 255, 0]

    def test_custom_maxval(self):
        from pbm.pbm_to_pgm import pbm_pixels_to_pgm_pixels
        result = pbm_pixels_to_pgm_pixels([0, 1], maxval=100)
        assert result == [100, 0]

    def test_empty_list(self):
        from pbm.pbm_to_pgm import pbm_pixels_to_pgm_pixels
        result = pbm_pixels_to_pgm_pixels([], maxval=255)
        assert result == []

    def test_all_black(self):
        from pbm.pbm_to_pgm import pbm_pixels_to_pgm_pixels
        result = pbm_pixels_to_pgm_pixels([1, 1, 1, 1], maxval=255)
        assert all(p == 0 for p in result)

    def test_all_white(self):
        from pbm.pbm_to_pgm import pbm_pixels_to_pgm_pixels
        result = pbm_pixels_to_pgm_pixels([0, 0, 0, 0], maxval=255)
        assert all(p == 255 for p in result)

    def test_invalid_maxval_raises(self):
        from pbm.pbm_to_pgm import pbm_pixels_to_pgm_pixels
        with pytest.raises(ValueError):
            pbm_pixels_to_pgm_pixels([0], maxval=0)

    def test_invalid_maxval_too_large_raises(self):
        from pbm.pbm_to_pgm import pbm_pixels_to_pgm_pixels
        with pytest.raises(ValueError):
            pbm_pixels_to_pgm_pixels([0], maxval=300)


class TestConvertPbmToPgmFile:
    """Integration tests using real PBM files and FF PGM writer."""

    def _write_pbm(self, content: str, tmp_dir: Path) -> Path:
        p = tmp_dir / "test.pbm"
        p.write_text(content, encoding="ascii")
        return p

    def test_simple_2x2_conversion(self, tmp_path):
        pbm_content = "P1\n2 2\n0 1\n1 0\n"
        pbm_path = self._write_pbm(pbm_content, tmp_path)
        pgm_path = tmp_path / "out.pgm"

        from pbm.pbm_to_pgm import convert_pbm_to_pgm
        result = convert_pbm_to_pgm(pbm_path, pgm_path)

        assert pgm_path.exists()
        assert result["width"] == 2
        assert result["height"] == 2
        assert result["pixel_count"] == 4

    def test_output_is_valid_pgm(self, tmp_path):
        pbm_content = "P1\n3 2\n0 1 0\n1 0 1\n"
        pbm_path = self._write_pbm(pbm_content, tmp_path)
        pgm_path = tmp_path / "out.pgm"

        from pbm.pbm_to_pgm import convert_pbm_to_pgm
        convert_pbm_to_pgm(pbm_path, pgm_path)

        content = pgm_path.read_text(encoding="ascii")
        assert content.startswith("P2")

    def test_roundtrip_pixel_correctness(self, tmp_path):
        pbm_content = "P1\n2 2\n0 1\n1 0\n"
        pbm_path = self._write_pbm(pbm_content, tmp_path)
        pgm_path = tmp_path / "out.pgm"

        from pbm.pbm_to_pgm import convert_pbm_to_pgm
        convert_pbm_to_pgm(pbm_path, pgm_path)

        # Parse the output PGM and verify pixel mapping
        from pgm.pgm_parser import parse_pgm_strict
        pgm_img = parse_pgm_strict(pgm_path)
        # PBM: 0 1 1 0 → PGM: 255 0 0 255
        assert pgm_img.pixels[0] == 255  # white
        assert pgm_img.pixels[1] == 0    # black
        assert pgm_img.pixels[2] == 0    # black
        assert pgm_img.pixels[3] == 255  # white

    def test_dogfood_status_in_result(self, tmp_path):
        pbm_content = "P1\n1 1\n0\n"
        pbm_path = self._write_pbm(pbm_content, tmp_path)
        pgm_path = tmp_path / "out.pgm"

        from pbm.pbm_to_pgm import convert_pbm_to_pgm
        result = convert_pbm_to_pgm(pbm_path, pgm_path)

        assert result["dogfood_status"] == "IMPLEMENTED"
        assert "pgm" in result["dogfood_library"].lower()

    def test_custom_maxval_in_output(self, tmp_path):
        pbm_content = "P1\n2 1\n0 1\n"
        pbm_path = self._write_pbm(pbm_content, tmp_path)
        pgm_path = tmp_path / "out.pgm"

        from pbm.pbm_to_pgm import convert_pbm_to_pgm
        convert_pbm_to_pgm(pbm_path, pgm_path, maxval=127)

        from pgm.pgm_parser import parse_pgm_strict
        pgm_img = parse_pgm_strict(pgm_path)
        assert pgm_img.maxval == 127
        assert pgm_img.pixels[0] == 127  # white
        assert pgm_img.pixels[1] == 0    # black

    def test_pbm_to_pgm_exported_from_init(self):
        """Verify convert_pbm_to_pgm is exported from pbm package __init__."""
        import pbm
        assert hasattr(pbm, "convert_pbm_to_pgm")
        assert hasattr(pbm, "pbm_pixels_to_pgm_pixels")


class TestDogfoodLibraryUsage:
    """Verify dogfooding — FF libraries used, not external ones."""

    def test_no_external_image_library_imported(self):
        """pbm_to_pgm must not import PIL, cv2, or other external image libs."""
        import pbm.pbm_to_pgm as mod
        import inspect
        source = inspect.getsource(mod)
        forbidden = ["PIL", "cv2", "imageio", "skimage", "matplotlib"]
        for lib in forbidden:
            assert lib not in source, f"External library '{lib}' found in pbm_to_pgm.py"

    def test_dogfood_uses_ff_pgm_writer(self):
        """pbm_to_pgm must import write_pgm from FF pgm library."""
        import pbm.pbm_to_pgm as mod
        import inspect
        source = inspect.getsource(mod)
        assert "write_pgm" in source, "Must use FF write_pgm from format-factory-pgm"
        assert "pgm_parser" in source or "pgm.pgm_parser" in source, (
            "Must import from pgm library"
        )

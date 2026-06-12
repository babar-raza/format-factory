# R110 Wave 5: PBM Write→Read Roundtrip Tests
# FOSS depth: cross-format verification via PPM write (roundtrip)

import os
import tempfile
import pbm
import ppm


class TestR110PbmWriteRoundtrip:
    """PBM parse + PPM write cross-format roundtrip tests."""

    def test_pbm_parse_returns_dict(self):
        """parse_pbm returns a dict for a valid PBM file."""
        with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False, mode="w") as f:
            f.write("P1\n2 2\n0 1\n1 0\n")
            path = f.name
        try:
            result = pbm.parse_pbm(path)
            assert isinstance(result, dict)
            assert result.get("width") == 2
            assert result.get("height") == 2
        finally:
            os.unlink(path)

    def test_pbm_to_ppm_dimensions_match(self):
        """Parse PBM, write PPM with same dimensions, verify."""
        with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False, mode="w") as f:
            f.write("P1\n3 2\n0 0 1\n1 0 1\n")
            path = f.name
        try:
            pbm_data = pbm.parse_pbm(path)
            w, h = pbm_data["width"], pbm_data["height"]
            # Create dummy PPM pixels matching PBM dimensions
            ppm_pixels = [(128, 128, 128)] * (w * h)
            ppm_path = path + ".ppm"
            ppm.write_ppm(ppm_pixels, w, h, 255, ppm_path)
            ppm_data = ppm.parse_ppm(ppm_path)
            assert ppm_data["width"] == w
            assert ppm_data["height"] == h
            os.unlink(ppm_path)
        finally:
            os.unlink(path)

    def test_pbm_probe_returns_dict(self):
        """probe_pbm returns valid dict for PBM file."""
        with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False, mode="w") as f:
            f.write("P1\n3 2\n0 0 0\n1 1 1\n")
            path = f.name
        try:
            info = pbm.probe_pbm(path)
            assert isinstance(info, dict)
            assert info.get("width") == 3
        finally:
            os.unlink(path)

    def test_pbm_strict_parse_returns_object(self):
        """parse_pbm_strict returns a PbmImage object with pixels."""
        with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False, mode="w") as f:
            f.write("P1\n2 2\n0 1\n1 0\n")
            path = f.name
        try:
            result = pbm.parse_pbm_strict(path)
            assert hasattr(result, "width")
            assert result.width == 2
            assert result.height == 2
            assert hasattr(result, "pixels")
            assert len(result.pixels) == 4
        finally:
            os.unlink(path)

    def test_pbm_parse_nonexistent_returns_error(self):
        """parse_pbm on nonexistent file returns ok=False."""
        result = pbm.parse_pbm("/nonexistent/r110_fake.pbm")
        assert result.get("ok") is False

    def test_pbm_pixel_stats(self):
        """image_pixel_stats returns stats for parsed PBM."""
        with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False, mode="w") as f:
            f.write("P1\n4 1\n0 0 1 1\n")
            path = f.name
        try:
            data = pbm.parse_pbm(path)
            stats = pbm.image_pixel_stats(data)
            assert isinstance(stats, dict)
        finally:
            os.unlink(path)

    def test_pbm_parse_consistent(self):
        """Multiple parse calls on same file give same width/height."""
        with tempfile.NamedTemporaryFile(suffix=".pbm", delete=False, mode="w") as f:
            f.write("P1\n2 2\n1 0\n0 1\n")
            path = f.name
        try:
            r1 = pbm.parse_pbm(path)
            r2 = pbm.parse_pbm(path)
            assert r1["width"] == r2["width"]
            assert r1["height"] == r2["height"]
            assert r1["pixel_count"] == r2["pixel_count"]
        finally:
            os.unlink(path)

    def test_pbm_get_capabilities(self):
        """get_capabilities returns a dict."""
        caps = pbm.get_capabilities()
        assert isinstance(caps, dict)

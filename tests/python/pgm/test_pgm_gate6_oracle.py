"""Gate 6 oracle tests for PGM parser — deterministic expected-value verification."""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from pgm.pgm_parser import parse_pgm_strict, parse_pgm, probe_pgm, get_capabilities

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "pgm")


class TestPgmGate6Oracle:
    def test_1x1_white_oracle(self):
        img = parse_pgm_strict(os.path.join(SAMPLES, "valid", "1x1-white.pgm"))
        assert img.width == 1
        assert img.height == 1
        assert img.maxval == 255
        assert img.magic == "P2"
        assert img.pixels == [255]

    def test_2x2_gradient_oracle(self):
        img = parse_pgm_strict(os.path.join(SAMPLES, "valid", "2x2-gradient.pgm"))
        assert img.width == 2
        assert img.height == 2
        assert img.maxval == 255
        assert img.pixels == [0, 85, 170, 255]

    def test_3x1_ramp_oracle(self):
        img = parse_pgm_strict(os.path.join(SAMPLES, "valid", "3x1-ramp.pgm"))
        assert img.width == 3
        assert img.height == 1
        assert img.pixels == [0, 128, 255]

    def test_synthetic_single_black_pixel(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pgm", delete=False) as f:
            f.write("P2\n1 1\n255\n0\n")
            f.flush()
            img = parse_pgm_strict(f.name)
        assert img.pixels == [0]
        os.unlink(f.name)

    def test_synthetic_uniform_gray(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pgm", delete=False) as f:
            f.write("P2\n2 2\n255\n128 128\n128 128\n")
            f.flush()
            img = parse_pgm_strict(f.name)
        assert img.pixels == [128, 128, 128, 128]
        os.unlink(f.name)

    def test_synthetic_low_maxval(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pgm", delete=False) as f:
            f.write("P2\n2 1\n3\n0 3\n")
            f.flush()
            img = parse_pgm_strict(f.name)
        assert img.maxval == 3
        assert img.pixels == [0, 3]
        os.unlink(f.name)

    def test_synthetic_with_comment(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pgm", delete=False) as f:
            f.write("P2\n# A comment\n1 1\n255\n100\n")
            f.flush()
            img = parse_pgm_strict(f.name)
        assert img.pixels == [100]
        os.unlink(f.name)

    def test_dict_api_oracle(self):
        result = parse_pgm(os.path.join(SAMPLES, "valid", "2x2-gradient.pgm"))
        assert result["ok"] is True
        assert result["width"] == 2
        assert result["height"] == 2
        assert result["pixel_count"] == 4
        assert result["magic"] == "P2"

    def test_probe_parse_consistency(self):
        path = os.path.join(SAMPLES, "valid", "2x2-gradient.pgm")
        probe = probe_pgm(path)
        img = parse_pgm_strict(path)
        assert probe["width"] == img.width
        assert probe["height"] == img.height
        assert probe["maxval"] == img.maxval

    def test_capabilities_oracle(self):
        caps = get_capabilities()
        assert caps["format"] == "pgm"
        assert caps["gate"] == 5
        assert len(caps["supported"]) >= 6
        assert len(caps["unsupported"]) >= 8

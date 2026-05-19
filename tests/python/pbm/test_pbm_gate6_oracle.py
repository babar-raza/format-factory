"""Gate 6 oracle tests for PBM parser — deterministic expected-value verification."""

import sys
import os
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from pbm.pbm_parser import parse_pbm_strict, parse_pbm, probe_pbm, get_capabilities

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "pbm")


class TestPbmGate6Oracle:
    def test_1x1_black_oracle(self):
        img = parse_pbm_strict(os.path.join(SAMPLES, "valid", "1x1-black.pbm"))
        assert img.width == 1
        assert img.height == 1
        assert img.magic == "P1"
        assert img.pixels == [1]

    def test_2x2_checker_oracle(self):
        img = parse_pbm_strict(os.path.join(SAMPLES, "valid", "2x2-checker.pbm"))
        assert img.width == 2
        assert img.height == 2
        assert img.pixels == [1, 0, 0, 1]

    def test_3x2_pattern_oracle(self):
        img = parse_pbm_strict(os.path.join(SAMPLES, "valid", "3x2-pattern.pbm"))
        assert img.width == 3
        assert img.height == 2
        assert img.pixels == [1, 0, 1, 0, 1, 0]

    def test_synthetic_all_white(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pbm", delete=False) as f:
            f.write("P1\n2 2\n0 0\n0 0\n")
            f.flush()
            img = parse_pbm_strict(f.name)
        assert img.pixels == [0, 0, 0, 0]
        os.unlink(f.name)

    def test_synthetic_all_black(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pbm", delete=False) as f:
            f.write("P1\n2 2\n1 1\n1 1\n")
            f.flush()
            img = parse_pbm_strict(f.name)
        assert img.pixels == [1, 1, 1, 1]
        os.unlink(f.name)

    def test_synthetic_single_white(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pbm", delete=False) as f:
            f.write("P1\n1 1\n0\n")
            f.flush()
            img = parse_pbm_strict(f.name)
        assert img.pixels == [0]
        os.unlink(f.name)

    def test_synthetic_with_comment(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".pbm", delete=False) as f:
            f.write("P1\n# comment\n1 1\n1\n")
            f.flush()
            img = parse_pbm_strict(f.name)
        assert img.pixels == [1]
        os.unlink(f.name)

    def test_dict_api_oracle(self):
        result = parse_pbm(os.path.join(SAMPLES, "valid", "2x2-checker.pbm"))
        assert result["ok"] is True
        assert result["width"] == 2
        assert result["height"] == 2
        assert result["pixel_count"] == 4

    def test_probe_parse_consistency(self):
        path = os.path.join(SAMPLES, "valid", "3x2-pattern.pbm")
        probe = probe_pbm(path)
        img = parse_pbm_strict(path)
        assert probe["width"] == img.width
        assert probe["height"] == img.height

    def test_capabilities_oracle(self):
        caps = get_capabilities()
        assert caps["format"] == "pbm"
        assert caps["gate"] == 5
        assert len(caps["supported"]) >= 5
        assert len(caps["unsupported"]) >= 8

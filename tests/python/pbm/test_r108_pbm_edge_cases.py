# R108 Lane F: PBM edge-case hardening
# 8 tests — probe, parse, strict, error paths

import importlib
import os
import pytest

pbm = importlib.import_module("pbm")

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "pbm")


class TestPbmEdgeCases:
    """PBM module edge-case hardening."""

    def test_module_importable(self):
        assert pbm is not None

    def test_parse_sample_if_exists(self):
        if not os.path.isdir(SAMPLES_DIR):
            pytest.skip("No PBM sample directory")
        samples = [f for f in os.listdir(SAMPLES_DIR) if f.endswith(".pbm")]
        if not samples:
            pytest.skip("No PBM sample files")
        result = pbm.parse_pbm(os.path.join(SAMPLES_DIR, samples[0]))
        assert isinstance(result, dict)
        assert result.get("ok") is True

    def test_probe_sample_if_exists(self):
        if not os.path.isdir(SAMPLES_DIR):
            pytest.skip("No PBM sample directory")
        samples = [f for f in os.listdir(SAMPLES_DIR) if f.endswith(".pbm")]
        if not samples:
            pytest.skip("No PBM sample files")
        result = pbm.probe_pbm(os.path.join(SAMPLES_DIR, samples[0]))
        assert isinstance(result, dict)

    def test_parse_nonexistent_returns_error(self):
        result = pbm.parse_pbm("/nonexistent/file.pbm")
        assert isinstance(result, dict)
        assert result.get("ok") is False

    def test_probe_returns_dict(self):
        if not os.path.isdir(SAMPLES_DIR):
            pytest.skip("No PBM sample directory")
        samples = [f for f in os.listdir(SAMPLES_DIR) if f.endswith(".pbm")]
        if not samples:
            pytest.skip("No PBM sample files")
        result = pbm.probe_pbm(os.path.join(SAMPLES_DIR, samples[0]))
        assert "magic" in result or "width" in result or len(result) > 0

    def test_parse_has_dimensions(self):
        if not os.path.isdir(SAMPLES_DIR):
            pytest.skip("No PBM sample directory")
        samples = [f for f in os.listdir(SAMPLES_DIR) if f.endswith(".pbm")]
        if not samples:
            pytest.skip("No PBM sample files")
        result = pbm.parse_pbm(os.path.join(SAMPLES_DIR, samples[0]))
        if result.get("ok"):
            assert "width" in result
            assert "height" in result

    def test_strict_valid_if_exists(self):
        if not os.path.isdir(SAMPLES_DIR):
            pytest.skip("No PBM sample directory")
        samples = [f for f in os.listdir(SAMPLES_DIR) if f.endswith(".pbm")]
        if not samples:
            pytest.skip("No PBM sample files")
        # strict_pbm should not raise on valid files
        result = pbm.strict_pbm(os.path.join(SAMPLES_DIR, samples[0]))
        assert isinstance(result, dict)

    def test_strict_nonexistent_raises(self):
        with pytest.raises(Exception):
            pbm.strict_pbm("/nonexistent/file.pbm")

# R107 Wave 3: PBM parse hardening and probe verification
# 10 tests — parse edge cases, probe output, error handling

import importlib
import os
import pytest

pbm = importlib.import_module("pbm")

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "pbm")
VALID_DIR = os.path.join(SAMPLES_DIR, "valid")
INVALID_DIR = os.path.join(SAMPLES_DIR, "invalid")


def _get_valid_sample():
    if os.path.isdir(VALID_DIR):
        for f in os.listdir(VALID_DIR):
            if f.endswith(".pbm"):
                return os.path.join(VALID_DIR, f)
    if os.path.isdir(SAMPLES_DIR):
        for f in os.listdir(SAMPLES_DIR):
            if f.endswith(".pbm"):
                return os.path.join(SAMPLES_DIR, f)
    pytest.skip("No PBM sample files")


class TestPbmParseHardening:
    """PBM parse edge cases and probe verification."""

    def test_parse_valid_returns_ok(self):
        path = _get_valid_sample()
        result = pbm.parse_pbm(path)
        assert result.get("ok") is True

    def test_parse_valid_has_dimensions(self):
        path = _get_valid_sample()
        result = pbm.parse_pbm(path)
        assert "width" in result
        assert "height" in result
        assert result["width"] > 0
        assert result["height"] > 0

    def test_parse_nonexistent_returns_error(self):
        result = pbm.parse_pbm("/nonexistent/file.pbm")
        assert result.get("ok") is False
        assert "error" in result

    def test_probe_returns_dict(self):
        path = _get_valid_sample()
        result = pbm.probe_pbm(path)
        assert isinstance(result, dict)

    def test_probe_has_magic(self):
        path = _get_valid_sample()
        result = pbm.probe_pbm(path)
        assert "magic" in result or "format" in result

    def test_parse_strict_valid_returns_object(self):
        path = _get_valid_sample()
        result = pbm.parse_pbm_strict(path)
        assert result is not None

    def test_parse_strict_nonexistent_raises(self):
        with pytest.raises(Exception):
            pbm.parse_pbm_strict("/nonexistent/file.pbm")

    def test_parse_result_has_pixel_count(self):
        path = _get_valid_sample()
        result = pbm.parse_pbm(path)
        if result.get("ok"):
            assert "pixel_count" in result
            assert result["pixel_count"] > 0

    def test_image_pixel_stats(self):
        path = _get_valid_sample()
        result = pbm.image_pixel_stats(path)
        assert isinstance(result, dict)

    def test_parse_multiple_consistent(self):
        path = _get_valid_sample()
        r1 = pbm.parse_pbm(path)
        r2 = pbm.parse_pbm(path)
        assert r1["width"] == r2["width"]
        assert r1["height"] == r2["height"]

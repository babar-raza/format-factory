"""Gate 4 prototype tests for PGM parser."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from pgm.pgm_parser import (
    parse_pgm_strict, parse_pgm, probe_pgm,
    PgmError, PgmInvalidMagicError,
)

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "pgm")


class TestPgmParser:
    def test_parse_1x1_white(self):
        img = parse_pgm_strict(os.path.join(SAMPLES, "valid", "1x1-white.pgm"))
        assert img.width == 1
        assert img.height == 1
        assert img.maxval == 255
        assert img.pixels == [255]

    def test_parse_2x2_gradient(self):
        img = parse_pgm_strict(os.path.join(SAMPLES, "valid", "2x2-gradient.pgm"))
        assert img.width == 2
        assert img.height == 2
        assert img.pixels == [0, 85, 170, 255]

    def test_parse_3x1_ramp(self):
        img = parse_pgm_strict(os.path.join(SAMPLES, "valid", "3x1-ramp.pgm"))
        assert img.width == 3
        assert img.height == 1
        assert img.pixels == [0, 128, 255]

    def test_invalid_magic(self):
        with pytest.raises(PgmInvalidMagicError):
            parse_pgm_strict(os.path.join(SAMPLES, "invalid", "wrong-magic.pgm"))

    def test_file_not_found(self):
        with pytest.raises(PgmError):
            parse_pgm_strict("/nonexistent/path.pgm")

    def test_dict_api_success(self):
        result = parse_pgm(os.path.join(SAMPLES, "valid", "1x1-white.pgm"))
        assert result["ok"] is True
        assert result["width"] == 1
        assert result["height"] == 1
        assert result["pixel_count"] == 1

    def test_dict_api_failure(self):
        result = parse_pgm(os.path.join(SAMPLES, "invalid", "wrong-magic.pgm"))
        assert result["ok"] is False
        assert "error" in result

    def test_probe_valid(self):
        result = probe_pgm(os.path.join(SAMPLES, "valid", "2x2-gradient.pgm"))
        assert result["valid_header"] is True
        assert result["magic"] == "P2"
        assert result["width"] == 2
        assert result["height"] == 2

    def test_probe_invalid(self):
        result = probe_pgm(os.path.join(SAMPLES, "invalid", "wrong-magic.pgm"))
        assert result["valid_header"] is False

    def test_probe_nonexistent(self):
        result = probe_pgm("/nonexistent/path.pgm")
        assert result["exists"] is False

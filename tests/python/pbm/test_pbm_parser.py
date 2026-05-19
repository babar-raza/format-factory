"""Gate 4 prototype tests for PBM parser."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from pbm.pbm_parser import (
    parse_pbm_strict, parse_pbm, probe_pbm,
    PbmError, PbmInvalidMagicError, PbmInvalidHeaderError, PbmSizeError, PbmDecodeError,
    PbmImage,
)

SAMPLES = os.path.join(os.path.dirname(__file__), "..", "..", "..", "samples", "by-format", "pbm")


class TestPbmParser:
    def test_parse_1x1_black(self):
        img = parse_pbm_strict(os.path.join(SAMPLES, "valid", "1x1-black.pbm"))
        assert img.width == 1
        assert img.height == 1
        assert img.pixels == [1]

    def test_parse_2x2_checker(self):
        img = parse_pbm_strict(os.path.join(SAMPLES, "valid", "2x2-checker.pbm"))
        assert img.width == 2
        assert img.height == 2
        assert img.pixels == [1, 0, 0, 1]

    def test_parse_3x2_pattern(self):
        img = parse_pbm_strict(os.path.join(SAMPLES, "valid", "3x2-pattern.pbm"))
        assert img.width == 3
        assert img.height == 2
        assert img.pixels == [1, 0, 1, 0, 1, 0]

    def test_invalid_magic(self):
        with pytest.raises(PbmInvalidMagicError):
            parse_pbm_strict(os.path.join(SAMPLES, "invalid", "wrong-magic.pbm"))

    def test_file_not_found(self):
        with pytest.raises(PbmError):
            parse_pbm_strict("/nonexistent/path.pbm")

    def test_dict_api_success(self):
        result = parse_pbm(os.path.join(SAMPLES, "valid", "1x1-black.pbm"))
        assert result["ok"] is True
        assert result["width"] == 1
        assert result["pixel_count"] == 1

    def test_dict_api_failure(self):
        result = parse_pbm(os.path.join(SAMPLES, "invalid", "wrong-magic.pbm"))
        assert result["ok"] is False

    def test_probe_valid(self):
        result = probe_pbm(os.path.join(SAMPLES, "valid", "2x2-checker.pbm"))
        assert result["valid_header"] is True
        assert result["magic"] == "P1"
        assert result["width"] == 2

    def test_probe_invalid(self):
        result = probe_pbm(os.path.join(SAMPLES, "invalid", "wrong-magic.pbm"))
        assert result["valid_header"] is False

    def test_probe_nonexistent(self):
        result = probe_pbm("/nonexistent/path.pbm")
        assert result["exists"] is False

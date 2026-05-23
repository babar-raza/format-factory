"""Gate 7 fuzz guard tests for PBM parser — malformed input handling."""

import sys
import os
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from pbm.pbm_parser import (
    parse_pbm_strict, parse_pbm,
    PbmError, PbmInvalidMagicError, PbmInvalidHeaderError, PbmSizeError, PbmDecodeError,
)


def _write_temp(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".pbm", delete=False)
    f.write(content)
    f.close()
    return f.name


class TestPbmGate7FuzzGuard:
    def test_empty_file(self):
        p = _write_temp("")
        with pytest.raises(PbmInvalidMagicError):
            parse_pbm_strict(p)
        os.unlink(p)

    def test_wrong_magic(self):
        p = _write_temp("P9\n1 1\n1\n")
        with pytest.raises(PbmInvalidMagicError):
            parse_pbm_strict(p)
        os.unlink(p)

    def test_truncated_header(self):
        p = _write_temp("P1\n1\n")
        with pytest.raises(PbmInvalidHeaderError):
            parse_pbm_strict(p)
        os.unlink(p)

    def test_huge_dimensions(self):
        p = _write_temp("P1\n99999 99999\n0\n")
        with pytest.raises((PbmSizeError, PbmDecodeError)):
            parse_pbm_strict(p)
        os.unlink(p)

    def test_negative_dimensions(self):
        p = _write_temp("P1\n-1 1\n0\n")
        with pytest.raises(PbmInvalidHeaderError):
            parse_pbm_strict(p)
        os.unlink(p)

    def test_truncated_pixel_data(self):
        p = _write_temp("P1\n2 2\n0 1\n")
        with pytest.raises(PbmDecodeError):
            parse_pbm_strict(p)
        os.unlink(p)

    def test_dict_api_safety(self):
        p = _write_temp("NOT A PBM FILE")
        result = parse_pbm(p)
        assert result["ok"] is False
        os.unlink(p)

    def test_binary_garbage(self):
        f = tempfile.NamedTemporaryFile(mode="wb", suffix=".pbm", delete=False)
        f.write(bytes(range(256)))
        f.close()
        result = parse_pbm(f.name)
        assert result["ok"] is False
        os.unlink(f.name)

    def test_invalid_pixel_value(self):
        p = _write_temp("P1\n1 1\n5\n")
        with pytest.raises(PbmDecodeError):
            parse_pbm_strict(p)
        os.unlink(p)

    def test_non_numeric_pixel(self):
        p = _write_temp("P1\n1 1\nabc\n")
        with pytest.raises(PbmDecodeError):
            parse_pbm_strict(p)
        os.unlink(p)

    # Note: P4 binary is now supported (R55 Train F).
    # P4 truncated-data guard is covered in tests/python/pbm/test_r55_pbm_p4_binary.py
    # using binary-mode file writes that are reliably truncated on all platforms.

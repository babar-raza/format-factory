"""Gate 7 fuzz guard tests for PGM parser — malformed input handling."""

import sys
import os
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "python"))
from pgm.pgm_parser import (
    parse_pgm_strict, parse_pgm,
    PgmError, PgmInvalidMagicError, PgmInvalidHeaderError, PgmSizeError, PgmDecodeError,
)


def _write_temp(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".pgm", delete=False)
    f.write(content)
    f.close()
    return f.name


class TestPgmGate7FuzzGuard:
    def test_empty_file(self):
        p = _write_temp("")
        with pytest.raises(PgmInvalidMagicError):
            parse_pgm_strict(p)
        os.unlink(p)

    def test_wrong_magic(self):
        p = _write_temp("P9\n1 1\n255\n0\n")
        with pytest.raises(PgmInvalidMagicError):
            parse_pgm_strict(p)
        os.unlink(p)

    def test_truncated_header(self):
        p = _write_temp("P2\n1\n")
        with pytest.raises(PgmInvalidHeaderError):
            parse_pgm_strict(p)
        os.unlink(p)

    def test_huge_dimensions(self):
        p = _write_temp("P2\n99999 99999\n255\n0\n")
        with pytest.raises((PgmSizeError, PgmDecodeError)):
            parse_pgm_strict(p)
        os.unlink(p)

    def test_negative_dimensions(self):
        p = _write_temp("P2\n-1 1\n255\n0\n")
        with pytest.raises(PgmInvalidHeaderError):
            parse_pgm_strict(p)
        os.unlink(p)

    def test_zero_maxval(self):
        p = _write_temp("P2\n1 1\n0\n0\n")
        with pytest.raises(PgmInvalidHeaderError):
            parse_pgm_strict(p)
        os.unlink(p)

    def test_truncated_pixel_data(self):
        p = _write_temp("P2\n2 2\n255\n0 1\n")
        with pytest.raises(PgmDecodeError):
            parse_pgm_strict(p)
        os.unlink(p)

    def test_dict_api_safety(self):
        p = _write_temp("GARBAGE DATA NOT PGM")
        result = parse_pgm(p)
        assert result["ok"] is False
        os.unlink(p)

    def test_binary_garbage(self):
        f = tempfile.NamedTemporaryFile(mode="wb", suffix=".pgm", delete=False)
        f.write(bytes(range(256)))
        f.close()
        result = parse_pgm(f.name)
        assert result["ok"] is False
        os.unlink(f.name)

    def test_out_of_range_pixel(self):
        p = _write_temp("P2\n1 1\n255\n300\n")
        with pytest.raises(PgmDecodeError):
            parse_pgm_strict(p)
        os.unlink(p)

    def test_non_numeric_pixel(self):
        p = _write_temp("P2\n1 1\n255\nabc\n")
        with pytest.raises(PgmDecodeError):
            parse_pgm_strict(p)
        os.unlink(p)

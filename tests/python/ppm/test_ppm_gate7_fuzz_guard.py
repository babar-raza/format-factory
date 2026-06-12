"""Gate 7 security and fuzz guard tests for PPM parser.

Deterministic malformed input guards. No heavy fuzzing.
"""

import sys
import tempfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

import pytest
from ppm.ppm_parser import (
    PpmDecodeError,
    PpmInvalidHeaderError,
    PpmInvalidMagicError,
    PpmSizeError,
    parse_ppm,
    parse_ppm_strict,
)


def _write_ppm(content: str) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".ppm", delete=False, mode="w",
                                      encoding="ascii")
    tmp.write(content)
    tmp.close()
    return tmp.name


class TestPpmFuzzGuards:
    """Malformed input guards for PPM parser."""

    def test_empty_file(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".ppm", delete=False)
        tmp.close()
        with pytest.raises(PpmInvalidMagicError):
            parse_ppm_strict(tmp.name)

    def test_wrong_magic(self):
        path = _write_ppm("P9\n1 1\n255\n0 0 0\n")
        with pytest.raises(PpmInvalidMagicError):
            parse_ppm_strict(path)

    def test_truncated_header(self):
        path = _write_ppm("P3\n1\n")
        with pytest.raises(PpmInvalidHeaderError):
            parse_ppm_strict(path)

    def test_huge_dimensions(self):
        path = _write_ppm("P3\n999999 999999\n255\n0 0 0\n")
        with pytest.raises(PpmSizeError):
            parse_ppm_strict(path)

    def test_negative_dimensions(self):
        path = _write_ppm("P3\n-1 1\n255\n0 0 0\n")
        with pytest.raises(PpmInvalidHeaderError):
            parse_ppm_strict(path)

    def test_zero_maxval(self):
        path = _write_ppm("P3\n1 1\n0\n0 0 0\n")
        with pytest.raises(PpmInvalidHeaderError):
            parse_ppm_strict(path)

    def test_truncated_pixel_data(self):
        path = _write_ppm("P3\n2 2\n255\n0 0 0\n")
        with pytest.raises(PpmDecodeError):
            parse_ppm_strict(path)

    def test_dict_api_never_raises(self):
        result = parse_ppm("/nonexistent/file.ppm")
        assert isinstance(result, dict)
        assert result["ok"] is False

    def test_binary_garbage(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".ppm", delete=False)
        tmp.write(bytes(range(256)))
        tmp.close()
        result = parse_ppm(tmp.name)
        assert result["ok"] is False

    def test_pixel_value_out_of_range(self):
        path = _write_ppm("P3\n1 1\n255\n999 0 0\n")
        with pytest.raises(PpmDecodeError):
            parse_ppm_strict(path)

    def test_non_numeric_pixel_data(self):
        path = _write_ppm("P3\n1 1\n255\nabc def ghi\n")
        with pytest.raises(PpmDecodeError):
            parse_ppm_strict(path)

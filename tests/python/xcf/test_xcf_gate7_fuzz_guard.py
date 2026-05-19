"""Gate 7 security and fuzz guard tests for XCF parser.

Deterministic malformed input guards. No heavy fuzzing.
"""

import struct
import sys
import tempfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

import pytest
from xcf.xcf_parser import (
    XcfError,
    XcfInvalidHeaderError,
    XcfInvalidMagicError,
    XcfParseError,
    XcfSizeError,
    parse_xcf,
    parse_xcf_strict,
)


class TestXcfFuzzGuards:
    """Malformed input guards for XCF parser."""

    def test_empty_file(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".xcf", delete=False)
        tmp.close()
        with pytest.raises(XcfParseError):
            parse_xcf_strict(tmp.name)

    def test_random_bytes(self):
        import random
        random.seed(99)
        data = bytes(random.randint(0, 255) for _ in range(100))
        tmp = tempfile.NamedTemporaryFile(suffix=".xcf", delete=False)
        tmp.write(data)
        tmp.close()
        result = parse_xcf(tmp.name)
        assert result["ok"] is False

    def test_wrong_magic(self):
        data = b"NOT XCF!" + b"\x00" * 50
        tmp = tempfile.NamedTemporaryFile(suffix=".xcf", delete=False)
        tmp.write(data)
        tmp.close()
        with pytest.raises(XcfInvalidMagicError):
            parse_xcf_strict(tmp.name)

    def test_truncated_header(self):
        """Only magic bytes, no canvas properties."""
        data = b"gimp xcf v011\x00"  # 14 bytes, need 26
        tmp = tempfile.NamedTemporaryFile(suffix=".xcf", delete=False)
        tmp.write(data)
        tmp.close()
        with pytest.raises(XcfParseError):
            parse_xcf_strict(tmp.name)

    def test_huge_dimensions(self):
        header = b"gimp xcf v011\x00"
        header += struct.pack(">III", 999999, 999999, 0)
        header += struct.pack(">II", 0, 0)  # PROP_END
        header += struct.pack(">I", 0)  # layer sentinel
        tmp = tempfile.NamedTemporaryFile(suffix=".xcf", delete=False)
        tmp.write(header)
        tmp.close()
        with pytest.raises(XcfSizeError):
            parse_xcf_strict(tmp.name)

    def test_zero_width(self):
        header = b"gimp xcf v011\x00"
        header += struct.pack(">III", 0, 100, 0)
        header += struct.pack(">II", 0, 0)
        header += struct.pack(">I", 0)
        tmp = tempfile.NamedTemporaryFile(suffix=".xcf", delete=False)
        tmp.write(header)
        tmp.close()
        with pytest.raises(XcfInvalidHeaderError):
            parse_xcf_strict(tmp.name)

    def test_invalid_image_type(self):
        header = b"gimp xcf v011\x00"
        header += struct.pack(">III", 1, 1, 99)
        header += struct.pack(">II", 0, 0)
        header += struct.pack(">I", 0)
        tmp = tempfile.NamedTemporaryFile(suffix=".xcf", delete=False)
        tmp.write(header)
        tmp.close()
        with pytest.raises(XcfInvalidHeaderError):
            parse_xcf_strict(tmp.name)

    def test_dict_api_never_raises(self):
        result = parse_xcf("/nonexistent/file.xcf")
        assert isinstance(result, dict)
        assert result["ok"] is False

    def test_missing_nul_terminator(self):
        """NUL byte at offset 13 replaced with non-zero."""
        header = b"gimp xcf v011\xFF"  # 0xFF instead of 0x00
        header += struct.pack(">III", 1, 1, 0)
        header += struct.pack(">II", 0, 0)
        header += struct.pack(">I", 0)
        tmp = tempfile.NamedTemporaryFile(suffix=".xcf", delete=False)
        tmp.write(header)
        tmp.close()
        with pytest.raises(XcfInvalidHeaderError):
            parse_xcf_strict(tmp.name)

    def test_property_list_truncated(self):
        """Property with payload_len exceeding file size."""
        header = b"gimp xcf v011\x00"
        header += struct.pack(">III", 1, 1, 0)
        # Property with huge payload length
        header += struct.pack(">II", 17, 999999)  # PROP_COMPRESSION with bad length
        tmp = tempfile.NamedTemporaryFile(suffix=".xcf", delete=False)
        tmp.write(header)
        tmp.close()
        with pytest.raises(XcfParseError):
            parse_xcf_strict(tmp.name)

    def test_all_zeros_file(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".xcf", delete=False)
        tmp.write(b"\x00" * 100)
        tmp.close()
        result = parse_xcf(tmp.name)
        assert result["ok"] is False

    def test_binary_garbage_after_valid_header(self):
        """Valid header but garbage instead of property list."""
        header = b"gimp xcf v011\x00"
        header += struct.pack(">III", 1, 1, 0)
        header += bytes(range(256))  # garbage
        tmp = tempfile.NamedTemporaryFile(suffix=".xcf", delete=False)
        tmp.write(header)
        tmp.close()
        # May parse partially or fail — must not crash
        result = parse_xcf(tmp.name)
        assert isinstance(result, dict)

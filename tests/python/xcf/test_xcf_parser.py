"""Tests for the XCF Gate 4 prototype parser."""

import struct
import sys
import tempfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from xcf.xcf_parser import (
    XcfImage,
    XcfError,
    XcfInvalidMagicError,
    parse_xcf,
    parse_xcf_strict,
    probe_xcf,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "xcf"


class TestXcfParserValidSamples:
    """Parse tests against valid XCF samples."""

    def test_1x1_red_rgb(self):
        img = parse_xcf_strict(SAMPLES / "valid" / "1x1-red-rgb.xcf")
        assert isinstance(img, XcfImage)
        assert img.width == 1
        assert img.height == 1
        assert img.image_type == 0  # RGB
        assert img.version == "v011"
        assert img.num_layers >= 1

    def test_2x2_gray(self):
        img = parse_xcf_strict(SAMPLES / "valid" / "2x2-gray.xcf")
        assert img.width == 2
        assert img.height == 2
        assert img.image_type == 1  # Grayscale
        assert img.num_layers >= 1

    def test_1x1_rgba_blue(self):
        img = parse_xcf_strict(SAMPLES / "valid" / "1x1-rgba-blue.xcf")
        assert img.width == 1
        assert img.height == 1
        assert img.image_type == 0  # RGB (RGBA is still image_type 0 in XCF)
        assert img.num_layers >= 1

    def test_all_valid_samples_parse(self):
        """All valid samples should parse without error."""
        valid_dir = SAMPLES / "valid"
        count = 0
        for f in valid_dir.glob("*.xcf"):
            result = parse_xcf(f)
            assert result["ok"], f"Failed to parse {f.name}: {result.get('error')}"
            count += 1
        assert count >= 3, f"Expected at least 3 valid samples, found {count}"


class TestXcfParserInvalid:
    """Tests for invalid inputs and error handling."""

    def test_wrong_magic(self):
        result = parse_xcf(SAMPLES / "invalid" / "wrong-magic.xcf")
        assert result["ok"] is False
        assert "magic" in result["error"].lower() or "Invalid" in result["error"]

    def test_wrong_magic_strict_raises(self):
        try:
            parse_xcf_strict(SAMPLES / "invalid" / "wrong-magic.xcf")
            assert 1 == 0, "Expected XcfInvalidMagicError"

        except XcfInvalidMagicError:
            pass

    def test_nonexistent_file(self):
        result = parse_xcf(Path("/nonexistent/file.xcf"))
        assert result["ok"] is False

    def test_nonexistent_strict_raises(self):
        try:
            parse_xcf_strict(Path("/nonexistent/file.xcf"))
            assert 1 == 0, "Expected XcfError"

        except XcfError:
            pass

    def test_short_file(self):
        """File shorter than 26 bytes (header size) should fail."""
        with tempfile.NamedTemporaryFile(suffix=".xcf", delete=False) as f:
            f.write(b"gimp xcf v01")  # Only 12 bytes
            f.flush()
            result = parse_xcf(f.name)
        assert result["ok"] is False
        assert "short" in result["error"].lower() or "bytes" in result["error"].lower()
        Path(f.name).unlink(missing_ok=True)


class TestXcfProbe:
    """Tests for probe_xcf."""

    def test_probe_valid(self):
        result = probe_xcf(SAMPLES / "valid" / "1x1-red-rgb.xcf")
        assert result["valid_header"] is True
        assert result["width"] == 1
        assert result["height"] == 1
        assert result["image_type"] == 0
        assert result["version"] == "v011"
        assert "file_size" in result

    def test_probe_nonexistent(self):
        result = probe_xcf(Path("/nonexistent/file.xcf"))
        assert result["exists"] is False
        assert "valid_header" not in result

    def test_probe_invalid_magic(self):
        result = probe_xcf(SAMPLES / "invalid" / "wrong-magic.xcf")
        assert result["valid_header"] is False


class TestXcfDictOutput:
    """Tests for dict output structure."""

    def test_dict_has_expected_keys(self):
        result = parse_xcf(SAMPLES / "valid" / "1x1-red-rgb.xcf")
        assert result["ok"] is True
        expected_keys = {"ok", "path", "width", "height", "image_type",
                         "image_type_name", "version", "num_layers"}
        assert expected_keys.issubset(result.keys())

    def test_error_dict_has_expected_keys(self):
        result = parse_xcf(Path("/nonexistent/file.xcf"))
        assert result["ok"] is False
        assert "error" in result
        assert "error_type" in result


class TestXcfValidation:
    """Tests for dimension and image_type validation."""

    def _make_xcf_header(self, width=1, height=1, image_type=0,
                         magic=b"gimp xcf ", version=b"v011"):
        """Build a minimal XCF header + PROP_END + empty layer table."""
        header = magic + version + b"\x00"
        header += struct.pack(">III", width, height, image_type)
        # PROP_END: type=0, length=0
        header += struct.pack(">II", 0, 0)
        # Layer offset sentinel (0)
        header += struct.pack(">I", 0)
        return header

    def test_dimension_too_large(self):
        data = self._make_xcf_header(width=262145, height=1)
        with tempfile.NamedTemporaryFile(suffix=".xcf", delete=False) as f:
            f.write(data)
            f.flush()
            result = parse_xcf(f.name)
        assert result["ok"] is False
        assert "exceed" in result["error"].lower() or "limit" in result["error"].lower()
        Path(f.name).unlink(missing_ok=True)

    def test_invalid_image_type(self):
        data = self._make_xcf_header(image_type=99)
        with tempfile.NamedTemporaryFile(suffix=".xcf", delete=False) as f:
            f.write(data)
            f.flush()
            result = parse_xcf(f.name)
        assert result["ok"] is False
        assert "image_type" in result["error"].lower() or "invalid" in result["error"].lower()
        Path(f.name).unlink(missing_ok=True)

    def test_zero_dimension(self):
        data = self._make_xcf_header(width=0, height=1)
        with tempfile.NamedTemporaryFile(suffix=".xcf", delete=False) as f:
            f.write(data)
            f.flush()
            result = parse_xcf(f.name)
        assert result["ok"] is False
        Path(f.name).unlink(missing_ok=True)

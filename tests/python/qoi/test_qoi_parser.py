"""Tests for the QOI Gate 4 prototype parser."""

import sys
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from qoi.qoi_parser import (
    QoiImage,
    QoiInvalidMagicError,
    parse_qoi,
    parse_qoi_strict,
    probe_qoi,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "qoi"


class TestQoiParserBasic:
    """Basic parse tests against valid samples."""

    def test_1x1_red(self):
        img = parse_qoi_strict(SAMPLES / "valid" / "1x1-red.qoi")
        assert isinstance(img, QoiImage)
        assert img.width == 1
        assert img.height == 1
        assert img.channels == 4
        assert len(img.pixels) == 1
        assert img.pixels[0] == (255, 0, 0, 255)

    def test_2x2_black(self):
        img = parse_qoi_strict(SAMPLES / "valid" / "2x2-black.qoi")
        assert img.width == 2
        assert img.height == 2
        assert len(img.pixels) == 4
        # All black pixels
        for px in img.pixels:
            assert px[0] == 0 and px[1] == 0 and px[2] == 0

    def test_4x1_gradient(self):
        img = parse_qoi_strict(SAMPLES / "valid" / "4x1-gradient.qoi")
        assert img.width == 4
        assert img.height == 1
        assert len(img.pixels) == 4


class TestQoiParserInvalid:
    """Tests for invalid/malformed QOI files."""

    def test_wrong_magic(self):
        result = parse_qoi(SAMPLES / "invalid" / "wrong-magic.qoi")
        assert result["ok"] is False
        assert "magic" in result["error"].lower() or "Magic" in result["error"]

    def test_wrong_magic_raises_strict(self):
        import pytest
        with pytest.raises(QoiInvalidMagicError):
            parse_qoi_strict(SAMPLES / "invalid" / "wrong-magic.qoi")

    def test_nonexistent_file(self):
        result = parse_qoi("/nonexistent/fake.qoi")
        assert result["ok"] is False

    def test_short_file(self):
        """File too short to contain a valid header."""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".qoi", delete=False) as f:
            f.write(b"qoi")  # Only 3 bytes, need 14
            f.flush()
            result = parse_qoi(f.name)
        assert result["ok"] is False


class TestQoiProbe:
    """Tests for probe_qoi."""

    def test_probe_valid(self):
        result = probe_qoi(SAMPLES / "valid" / "1x1-red.qoi")
        assert result["valid_header"] is True
        assert result["width"] == 1
        assert result["height"] == 1
        assert result["channels"] == 4

    def test_probe_nonexistent(self):
        result = probe_qoi("/nonexistent/fake.qoi")
        assert result["exists"] is False


class TestQoiMalformedInput:
    """Hardening tests for malformed / adversarial QOI input (R28 Lane F)."""

    def test_empty_file(self, tmp_path):
        """A zero-byte file must fail gracefully."""
        f = tmp_path / "empty.qoi"
        f.write_bytes(b"")
        result = parse_qoi(str(f))
        assert result["ok"] is False

    def test_empty_file_strict(self, tmp_path):
        import pytest
        f = tmp_path / "empty.qoi"
        f.write_bytes(b"")
        with pytest.raises(Exception):
            parse_qoi_strict(str(f))

    def test_wrong_magic_bytes(self, tmp_path):
        """File with wrong magic bytes must be rejected."""
        import struct
        f = tmp_path / "badmagic.qoi"
        # 'PNG\x89' + valid dimensions + channels + colorspace + padding
        data = b"PNG\x89" + struct.pack(">II", 1, 1) + bytes([4, 0]) + b"\x00" * 20
        f.write_bytes(data)
        result = parse_qoi(str(f))
        assert result["ok"] is False
        assert "magic" in result.get("error", "").lower() or "Magic" in result.get("error", "")

    def test_truncated_header(self, tmp_path):
        """File with only magic and partial header (10 bytes) must fail."""
        f = tmp_path / "short.qoi"
        f.write_bytes(b"qoif\x00\x00\x00\x01\x00\x00")  # 10 bytes, need 14
        result = parse_qoi(str(f))
        assert result["ok"] is False

    def test_zero_width(self, tmp_path):
        """Header claiming 0 width must be rejected."""
        import struct
        f = tmp_path / "zero-w.qoi"
        data = b"qoif" + struct.pack(">II", 0, 1) + bytes([4, 0])
        f.write_bytes(data)
        result = parse_qoi(str(f))
        assert result["ok"] is False

    def test_zero_height(self, tmp_path):
        """Header claiming 0 height must be rejected."""
        import struct
        f = tmp_path / "zero-h.qoi"
        data = b"qoif" + struct.pack(">II", 1, 0) + bytes([4, 0])
        f.write_bytes(data)
        result = parse_qoi(str(f))
        assert result["ok"] is False

    def test_oversized_dimensions(self, tmp_path):
        """Header claiming 65535x65535 dimensions must be rejected."""
        import struct
        f = tmp_path / "huge.qoi"
        data = b"qoif" + struct.pack(">II", 65535, 65535) + bytes([4, 0])
        f.write_bytes(data)
        result = parse_qoi(str(f))
        assert result["ok"] is False
        assert "QoiSizeError" in result.get("error_type", "") or "exceed" in result.get("error", "").lower()

    def test_invalid_channels(self, tmp_path):
        """Header with channels=5 (only 3 or 4 valid) must be rejected."""
        import struct
        f = tmp_path / "bad-chan.qoi"
        data = b"qoif" + struct.pack(">II", 1, 1) + bytes([5, 0])
        f.write_bytes(data)
        result = parse_qoi(str(f))
        assert result["ok"] is False

    def test_invalid_colorspace(self, tmp_path):
        """Header with colorspace=2 (only 0 or 1 valid) must be rejected."""
        import struct
        f = tmp_path / "bad-cs.qoi"
        data = b"qoif" + struct.pack(">II", 1, 1) + bytes([4, 2])
        f.write_bytes(data)
        result = parse_qoi(str(f))
        assert result["ok"] is False

    def test_truncated_pixel_data(self, tmp_path):
        """Valid header but pixel data cut short (no end marker, no pixels)."""
        import struct
        f = tmp_path / "trunc-px.qoi"
        # Valid header for 2x2 image but only header bytes, no pixel data
        data = b"qoif" + struct.pack(">II", 2, 2) + bytes([4, 0])
        f.write_bytes(data)
        result = parse_qoi(str(f))
        assert result["ok"] is False

    def test_probe_short_file(self, tmp_path):
        """probe_qoi on a 5-byte file must report valid_header=False."""
        f = tmp_path / "tiny.qoi"
        f.write_bytes(b"qoif\x00")
        result = probe_qoi(str(f))
        assert result["valid_header"] is False


class TestQoiParserDict:
    """Tests for the dict-returning parse_qoi."""

    def test_dict_output(self):
        result = parse_qoi(SAMPLES / "valid" / "1x1-red.qoi")
        assert result["ok"] is True
        assert result["width"] == 1
        assert result["height"] == 1
        assert result["pixel_count"] == 1

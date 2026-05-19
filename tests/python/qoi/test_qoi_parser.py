"""Tests for the QOI Gate 4 prototype parser."""

import sys
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from qoi.qoi_parser import (
    QoiImage,
    QoiInvalidMagicError,
    QoiSizeError,
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


class TestQoiParserDict:
    """Tests for the dict-returning parse_qoi."""

    def test_dict_output(self):
        result = parse_qoi(SAMPLES / "valid" / "1x1-red.qoi")
        assert result["ok"] is True
        assert result["width"] == 1
        assert result["height"] == 1
        assert result["pixel_count"] == 1

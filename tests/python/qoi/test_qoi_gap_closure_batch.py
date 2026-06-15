"""Gap closure tests for QOI — covering open gaps.

Gaps: GAP-QOI-FOSS-PARSE_QOI-001, GAP-QOI-FOSS-PARSE_QOI_ST-001,
      GAP-QOI-FOSS-GET_CAPABILI-001, GAP-QOI-FOSS-QOI_UNIQUE_C-001,
      GAP-QOI-FOSS-QOI_CHANNEL_-001, GAP-QOI-FOSS-QOI_AVERAGE_-001,
      GAP-QOI-FOSS-QOIIMAGE-001, GAP-QOI-FOSS-ENCODE_QOI-001,
      GAP-QOI-FOSS-ENCODE_QOI_T-001, GAP-QOI-FOSS-GET_ENCODER_-001,
      GAP-QOI-FOSS-PROBE_QOI-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import (
    QoiError,
    QoiImage,
    get_capabilities,
    parse_qoi,
    parse_qoi_strict,
    probe_qoi,
    qoi_average_brightness,
    qoi_channel_count,
    qoi_unique_color_count,
)
from src.python.qoi.qoi_encoder import (
    QoiEncodeError,
    encode_qoi,
    encode_qoi_to_file,
    get_encoder_capabilities,
)


@pytest.fixture
def tiny_qoi(tmp_path):
    """Create a minimal 2x2 RGB QOI file via the encoder."""
    img = QoiImage(
        width=2, height=2, channels=3, colorspace=0,
        pixels=[
            (255, 0, 0),    # red
            (0, 255, 0),    # green
            (0, 0, 255),    # blue
            (255, 255, 0),  # yellow
        ],
    )
    out = tmp_path / "tiny.qoi"
    encode_qoi_to_file(img, str(out))
    return out


@pytest.fixture
def rgba_qoi(tmp_path):
    """Create a 1x2 RGBA QOI file."""
    img = QoiImage(
        width=1, height=2, channels=4, colorspace=0,
        pixels=[
            (255, 0, 0, 255),  # opaque red
            (0, 0, 0, 128),    # semi-transparent black
        ],
    )
    out = tmp_path / "rgba.qoi"
    encode_qoi_to_file(img, str(out))
    return out


class TestParseQoi:
    def test_parse_returns_dict(self, tiny_qoi):
        result = parse_qoi(str(tiny_qoi))
        assert isinstance(result, dict)

    def test_parse_has_dimensions(self, tiny_qoi):
        result = parse_qoi(str(tiny_qoi))
        assert result.get("width") == 2
        assert result.get("height") == 2


class TestParseQoiStrict:
    def test_returns_qoi_image(self, tiny_qoi):
        img = parse_qoi_strict(str(tiny_qoi))
        assert isinstance(img, QoiImage)
        assert img.width == 2
        assert img.height == 2

    def test_pixels_present(self, tiny_qoi):
        img = parse_qoi_strict(str(tiny_qoi))
        assert len(img.pixels) == 4  # 2x2 = 4 pixels


class TestProbeQoi:
    def test_probe_valid_file(self, tiny_qoi):
        result = probe_qoi(str(tiny_qoi))
        assert isinstance(result, dict)
        assert result.get("width") == 2

    def test_probe_invalid_file(self, tmp_path):
        bad = tmp_path / "bad.qoi"
        bad.write_bytes(b"not a qoi file")
        result = probe_qoi(str(bad))
        assert result.get("valid_header") is False


class TestGetCapabilities:
    def test_returns_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert len(caps) > 0

    def test_includes_parse(self):
        caps = get_capabilities()
        cap_str = str(caps).lower()
        assert "parse" in cap_str or "qoi" in cap_str


class TestQoiUniqueColorCount:
    def test_four_colors(self, tiny_qoi):
        count = qoi_unique_color_count(str(tiny_qoi))
        assert count == 4  # red, green, blue, yellow


class TestQoiChannelCount:
    def test_rgb_has_3_channels(self, tiny_qoi):
        assert qoi_channel_count(str(tiny_qoi)) == 3

    def test_rgba_has_4_channels(self, rgba_qoi):
        assert qoi_channel_count(str(rgba_qoi)) == 4


class TestQoiAverageBrightness:
    def test_brightness_in_range(self, tiny_qoi):
        brightness = qoi_average_brightness(str(tiny_qoi))
        assert 0.0 <= brightness <= 255.0

    def test_brightness_not_zero(self, tiny_qoi):
        brightness = qoi_average_brightness(str(tiny_qoi))
        assert brightness > 0


class TestQoiImage:
    def test_dataclass_fields(self):
        img = QoiImage(width=1, height=1, channels=3, colorspace=0,
                       pixels=[(128, 128, 128)])
        assert img.width == 1
        assert img.height == 1
        assert img.channels == 3


class TestEncodeQoi:
    def test_encode_produces_bytes(self):
        img = QoiImage(width=1, height=1, channels=3, colorspace=0,
                       pixels=[(0, 0, 0)])
        data = encode_qoi(img)
        assert isinstance(data, bytes)
        assert len(data) > 14  # header is 14 bytes

    def test_encode_starts_with_magic(self):
        img = QoiImage(width=1, height=1, channels=3, colorspace=0,
                       pixels=[(0, 0, 0)])
        data = encode_qoi(img)
        assert data[:4] == b"qoif"


class TestEncodeQoiToFile:
    def test_creates_file(self, tmp_path):
        img = QoiImage(width=1, height=1, channels=3, colorspace=0,
                       pixels=[(255, 0, 0)])
        out = tmp_path / "encoded.qoi"
        encode_qoi_to_file(img, str(out))
        assert out.exists()
        assert out.stat().st_size > 0

    def test_roundtrip(self, tmp_path):
        img = QoiImage(width=2, height=1, channels=3, colorspace=0,
                       pixels=[(10, 20, 30), (40, 50, 60)])
        out = tmp_path / "rt.qoi"
        encode_qoi_to_file(img, str(out))
        decoded = parse_qoi_strict(str(out))
        assert decoded.width == 2
        assert decoded.height == 1
        assert len(decoded.pixels) == 2


class TestGetEncoderCapabilities:
    def test_returns_dict(self):
        caps = get_encoder_capabilities()
        assert isinstance(caps, dict)
        assert len(caps) > 0

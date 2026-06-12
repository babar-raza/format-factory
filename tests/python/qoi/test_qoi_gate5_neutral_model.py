"""Gate 5 neutral model and API hardening tests for QOI parser."""

import struct
import sys
import tempfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from qoi.qoi_parser import (
    SUPPORTED_FEATURES,
    UNSUPPORTED_FEATURES,
    QOI_END_MARKER,
    QOI_MAGIC,
    QoiInvalidHeaderError,
    get_capabilities,
    parse_qoi,
    parse_qoi_strict,
    probe_qoi,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "qoi"


def _make_qoi(width: int, height: int, channels: int, colorspace: int,
               pixel_data: bytes) -> Path:
    """Build a minimal QOI file with given header and pixel data."""
    header = QOI_MAGIC + struct.pack(">II", width, height) + bytes([channels, colorspace])
    data = header + pixel_data + QOI_END_MARKER
    tmp = tempfile.NamedTemporaryFile(suffix=".qoi", delete=False)
    tmp.write(data)
    tmp.flush()
    tmp.close()
    return Path(tmp.name)


class TestQoiCapabilities:
    """Verify Gate 5 capability declarations."""

    def test_get_capabilities_returns_dict(self):
        caps = get_capabilities()
        assert isinstance(caps, dict)
        assert caps["format"] == "qoi"
        assert caps["gate"] == 5

    def test_commercial_product_ready_false(self):
        caps = get_capabilities()
        assert caps["commercial_product_ready"] is False

    def test_supported_features_nonempty(self):
        assert len(SUPPORTED_FEATURES) > 0
        caps = get_capabilities()
        assert len(caps["supported"]) == len(SUPPORTED_FEATURES)

    def test_unsupported_features_nonempty(self):
        assert len(UNSUPPORTED_FEATURES) > 0
        caps = get_capabilities()
        assert len(caps["unsupported"]) == len(UNSUPPORTED_FEATURES)

    def test_no_overlap_supported_unsupported(self):
        overlap = SUPPORTED_FEATURES & UNSUPPORTED_FEATURES
        assert len(overlap) == 0, f"Overlap: {overlap}"

    def test_animation_explicitly_unsupported(self):
        assert "animation" in UNSUPPORTED_FEATURES

    def test_encoding_explicitly_unsupported(self):
        assert "encoding" in UNSUPPORTED_FEATURES

    def test_all_ops_in_supported(self):
        for op in ["op_rgb", "op_rgba", "op_index", "op_diff", "op_luma", "op_run"]:
            assert op in SUPPORTED_FEATURES

    def test_limits_in_capabilities(self):
        caps = get_capabilities()
        assert caps["max_file_size"] == 64 * 1024 * 1024
        assert caps["max_dimension"] == 16384
        assert caps["max_pixels"] == 16384 * 16384


class TestQoiEdgeCases:
    """Edge-case tests for Gate 5 hardening."""

    def test_3_channel_mode(self):
        # 1x1 pixel, channels=3, QOI_OP_RGB (0xFE) + R G B
        pixel_data = bytes([0xFE, 128, 64, 32])
        path = _make_qoi(1, 1, 3, 0, pixel_data)
        img = parse_qoi_strict(path)
        assert img.channels == 3
        assert img.pixels[0] == (128, 64, 32)

    def test_colorspace_1_linear(self):
        # 1x1, colorspace=1 (all-linear)
        pixel_data = bytes([0xFE, 100, 100, 100])
        path = _make_qoi(1, 1, 4, 1, pixel_data)
        img = parse_qoi_strict(path)
        assert img.colorspace == 1

    def test_zero_width_raises(self):
        import pytest
        header = QOI_MAGIC + struct.pack(">II", 0, 1) + bytes([4, 0])
        tmp = tempfile.NamedTemporaryFile(suffix=".qoi", delete=False)
        tmp.write(header + QOI_END_MARKER)
        tmp.close()
        with pytest.raises(QoiInvalidHeaderError, match="dimensions"):
            parse_qoi_strict(tmp.name)

    def test_zero_height_raises(self):
        import pytest
        header = QOI_MAGIC + struct.pack(">II", 1, 0) + bytes([4, 0])
        tmp = tempfile.NamedTemporaryFile(suffix=".qoi", delete=False)
        tmp.write(header + QOI_END_MARKER)
        tmp.close()
        with pytest.raises(QoiInvalidHeaderError, match="dimensions"):
            parse_qoi_strict(tmp.name)

    def test_invalid_channels_raises(self):
        import pytest
        header = QOI_MAGIC + struct.pack(">II", 1, 1) + bytes([5, 0])
        tmp = tempfile.NamedTemporaryFile(suffix=".qoi", delete=False)
        tmp.write(header + QOI_END_MARKER)
        tmp.close()
        with pytest.raises(QoiInvalidHeaderError, match="channels"):
            parse_qoi_strict(tmp.name)

    def test_invalid_colorspace_raises(self):
        import pytest
        header = QOI_MAGIC + struct.pack(">II", 1, 1) + bytes([4, 2])
        tmp = tempfile.NamedTemporaryFile(suffix=".qoi", delete=False)
        tmp.write(header + QOI_END_MARKER)
        tmp.close()
        with pytest.raises(QoiInvalidHeaderError, match="colorspace"):
            parse_qoi_strict(tmp.name)

    def test_parse_qoi_dict_error_has_error_type(self):
        result = parse_qoi("/nonexistent/fake.qoi")
        assert result["ok"] is False
        assert "error_type" in result

    def test_probe_nonexistent_returns_exists_false(self):
        result = probe_qoi("/nonexistent/fake.qoi")
        assert result["exists"] is False

    def test_run_length_decode(self):
        # 1x1 pixel using OP_RUN: 0xC0 means run of 1 (bias of +1)
        # Previous pixel starts as (0,0,0,255) so first pixel = (0,0,0,255)
        pixel_data = bytes([0xC0])  # run of 1 with default pixel
        path = _make_qoi(1, 1, 4, 0, pixel_data)
        img = parse_qoi_strict(path)
        assert img.pixels[0] == (0, 0, 0, 255)

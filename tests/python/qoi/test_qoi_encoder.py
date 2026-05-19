"""Tests for QOI encoder — R33 deepening deliverable."""

import sys
import tempfile
from pathlib import Path

import pytest

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from qoi.qoi_parser import (
    QoiImage,
    QOI_MAGIC,
    QOI_END_MARKER,
    parse_qoi_strict,
)
from qoi.qoi_encoder import (
    encode_qoi,
    encode_qoi_to_file,
    get_encoder_capabilities,
    QoiEncodeError,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "qoi"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_image(w: int, h: int, pixels: list, channels: int = 4, colorspace: int = 0) -> QoiImage:
    return QoiImage(width=w, height=h, channels=channels, colorspace=colorspace, pixels=pixels)


# ---------------------------------------------------------------------------
# 1. Header validation
# ---------------------------------------------------------------------------

class TestEncoderHeader:

    def test_magic_bytes(self):
        img = _make_image(1, 1, [(255, 0, 0, 255)])
        data = encode_qoi(img)
        assert data[:4] == QOI_MAGIC

    def test_header_dimensions(self):
        import struct
        img = _make_image(3, 2, [(0, 0, 0, 255)] * 6)
        data = encode_qoi(img)
        w, h = struct.unpack(">II", data[4:12])
        assert w == 3
        assert h == 2

    def test_header_channels(self):
        img = _make_image(1, 1, [(128, 128, 128)], channels=3)
        data = encode_qoi(img)
        assert data[12] == 3

    def test_header_colorspace(self):
        img = _make_image(1, 1, [(0, 0, 0, 255)], colorspace=1)
        data = encode_qoi(img)
        assert data[13] == 1

    def test_end_marker(self):
        img = _make_image(1, 1, [(255, 0, 0, 255)])
        data = encode_qoi(img)
        assert data[-8:] == QOI_END_MARKER


# ---------------------------------------------------------------------------
# 2. Round-trip (encode -> decode)
# ---------------------------------------------------------------------------

class TestEncoderRoundTrip:

    def test_single_red_pixel(self):
        pixels = [(255, 0, 0, 255)]
        img = _make_image(1, 1, pixels)
        data = encode_qoi(img)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.qoi"
            path.write_bytes(data)
            decoded = parse_qoi_strict(path)
            assert decoded.pixels == pixels

    def test_single_pixel_rgb(self):
        pixels = [(128, 64, 32)]
        img = _make_image(1, 1, pixels, channels=3)
        data = encode_qoi(img)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.qoi"
            path.write_bytes(data)
            decoded = parse_qoi_strict(path)
            assert decoded.pixels == pixels

    def test_2x2_uniform(self):
        pixels = [(100, 200, 50, 255)] * 4
        img = _make_image(2, 2, pixels)
        data = encode_qoi(img)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.qoi"
            path.write_bytes(data)
            decoded = parse_qoi_strict(path)
            assert decoded.pixels == pixels

    def test_gradient_roundtrip(self):
        """Gradient image exercises DIFF and LUMA chunks."""
        pixels = [(i, i, i, 255) for i in range(256)]
        img = _make_image(16, 16, pixels)
        data = encode_qoi(img)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.qoi"
            path.write_bytes(data)
            decoded = parse_qoi_strict(path)
            assert decoded.pixels == pixels

    def test_mixed_colors_roundtrip(self):
        """Diverse color palette exercises INDEX, DIFF, LUMA, RGB chunks."""
        pixels = [
            (255, 0, 0, 255), (0, 255, 0, 255), (0, 0, 255, 255),
            (255, 255, 0, 255), (0, 255, 255, 255), (255, 0, 255, 255),
            (128, 128, 128, 255), (64, 32, 16, 255), (200, 100, 50, 255),
        ]
        img = _make_image(3, 3, pixels)
        data = encode_qoi(img)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.qoi"
            path.write_bytes(data)
            decoded = parse_qoi_strict(path)
            assert decoded.pixels == pixels

    def test_alpha_variation_roundtrip(self):
        """Pixels with varying alpha exercise RGBA chunk."""
        pixels = [
            (255, 0, 0, 255), (255, 0, 0, 128),
            (255, 0, 0, 64), (255, 0, 0, 0),
        ]
        img = _make_image(2, 2, pixels)
        data = encode_qoi(img)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.qoi"
            path.write_bytes(data)
            decoded = parse_qoi_strict(path)
            assert decoded.pixels == pixels

    def test_run_length_roundtrip(self):
        """Long run of same pixel exercises RUN chunk."""
        pixels = [(42, 42, 42, 255)] * 100
        img = _make_image(10, 10, pixels)
        data = encode_qoi(img)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.qoi"
            path.write_bytes(data)
            decoded = parse_qoi_strict(path)
            assert decoded.pixels == pixels

    def test_large_image_roundtrip(self):
        """64x64 image with pattern exercises all chunk types."""
        pixels = []
        for y in range(64):
            for x in range(64):
                r = (x * 4) & 0xFF
                g = (y * 4) & 0xFF
                b = ((x + y) * 2) & 0xFF
                pixels.append((r, g, b, 255))
        img = _make_image(64, 64, pixels)
        data = encode_qoi(img)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.qoi"
            path.write_bytes(data)
            decoded = parse_qoi_strict(path)
            assert decoded.pixels == pixels


# ---------------------------------------------------------------------------
# 3. Corpus round-trip
# ---------------------------------------------------------------------------

class TestEncoderCorpusRoundTrip:

    def test_roundtrip_all_valid_samples(self):
        """Decode -> encode -> decode all valid QOI samples."""
        valid_dir = SAMPLES / "valid"
        if not valid_dir.exists():
            pytest.skip("valid samples dir not found")
        for qoi_file in valid_dir.glob("*.qoi"):
            original = parse_qoi_strict(qoi_file)
            encoded = encode_qoi(original)
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "roundtrip.qoi"
                path.write_bytes(encoded)
                decoded = parse_qoi_strict(path)
                assert decoded.width == original.width
                assert decoded.height == original.height
                assert decoded.channels == original.channels
                assert decoded.pixels == original.pixels, f"Round-trip failed for {qoi_file.name}"


# ---------------------------------------------------------------------------
# 4. Compression efficiency
# ---------------------------------------------------------------------------

class TestEncoderEfficiency:

    def test_run_encoding_compresses(self):
        """Run-length encoded data should be smaller than raw pixels."""
        pixels = [(0, 0, 0, 255)] * 1000
        img = _make_image(100, 10, pixels)
        data = encode_qoi(img)
        raw_size = 14 + 1000 * 4 + 8  # header + pixels + end
        assert len(data) < raw_size

    def test_index_reuse_compresses(self):
        """Alternating between 2 colors should use INDEX chunks."""
        a, b = (255, 0, 0, 255), (0, 255, 0, 255)
        pixels = [a, b] * 50
        img = _make_image(10, 10, pixels)
        data = encode_qoi(img)
        raw_size = 14 + 100 * 4 + 8
        assert len(data) < raw_size


# ---------------------------------------------------------------------------
# 5. Validation errors
# ---------------------------------------------------------------------------

class TestEncoderValidation:

    def test_zero_width(self):
        with pytest.raises(QoiEncodeError):
            encode_qoi(_make_image(0, 1, []))

    def test_zero_height(self):
        with pytest.raises(QoiEncodeError):
            encode_qoi(_make_image(1, 0, []))

    def test_wrong_pixel_count(self):
        with pytest.raises(QoiEncodeError):
            encode_qoi(_make_image(2, 2, [(0, 0, 0, 255)]))  # only 1 pixel

    def test_wrong_channel_count(self):
        with pytest.raises(QoiEncodeError):
            encode_qoi(_make_image(1, 1, [(0, 0, 0, 255)], channels=5))

    def test_wrong_colorspace(self):
        with pytest.raises(QoiEncodeError):
            encode_qoi(_make_image(1, 1, [(0, 0, 0, 255)], colorspace=2))

    def test_pixel_channel_mismatch(self):
        with pytest.raises(QoiEncodeError):
            encode_qoi(_make_image(1, 1, [(0, 0, 0)], channels=4))

    def test_oversized_dimensions(self):
        with pytest.raises(QoiEncodeError):
            encode_qoi(_make_image(20000, 1, [(0, 0, 0, 255)] * 20000))


# ---------------------------------------------------------------------------
# 6. File output
# ---------------------------------------------------------------------------

class TestEncoderFileOutput:

    def test_write_qoi_file(self):
        pixels = [(255, 128, 0, 255)] * 4
        img = _make_image(2, 2, pixels)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "output.qoi"
            result_path = encode_qoi_to_file(img, path)
            assert Path(result_path).exists()
            decoded = parse_qoi_strict(result_path)
            assert decoded.pixels == pixels


# ---------------------------------------------------------------------------
# 7. Capabilities
# ---------------------------------------------------------------------------

class TestEncoderCapabilities:

    def test_capabilities_structure(self):
        caps = get_encoder_capabilities()
        assert caps["format"] == "qoi"
        assert caps["operation"] == "encode"
        assert "greedy_encoding" in caps["features"]
        assert "round_trip_with_decoder" in caps["features"]
        assert len(caps["chunk_types"]) == 6

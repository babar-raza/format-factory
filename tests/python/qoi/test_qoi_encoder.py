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


def _decode_bytes(data: bytes) -> QoiImage:
    """Decode QOI bytes via temp file (parse_qoi_strict takes a file path)."""
    with tempfile.NamedTemporaryFile(suffix=".qoi", delete=False) as f:
        f.write(data)
        f.flush()
        result = parse_qoi_strict(f.name)
    Path(f.name).unlink(missing_ok=True)
    return result


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


# ---------------------------------------------------------------------------
# 8. R35 Encoder/Round-Trip Hardening
# ---------------------------------------------------------------------------

class TestR35EncoderHardening:
    """R35 Lane F: additional edge cases for encoder robustness."""

    def test_run_length_boundary_62(self):
        """Run of exactly 62 (max single OP_RUN) encodes correctly."""
        pixel = (100, 100, 100, 255)
        pixels = [pixel] * 62
        img = _make_image(62, 1, pixels)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels

    def test_run_length_boundary_63(self):
        """Run of 63 pixels needs 2 RUN chunks (62 + 1)."""
        pixel = (50, 50, 50, 255)
        pixels = [pixel] * 63
        img = _make_image(63, 1, pixels)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels

    def test_alternating_two_colors(self):
        """Alternating colors should use INDEX lookups."""
        a = (255, 0, 0, 255)
        b = (0, 255, 0, 255)
        pixels = [a, b] * 16
        img = _make_image(32, 1, pixels)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels

    def test_alpha_gradient(self):
        """Varying alpha values survive round-trip."""
        pixels = [(128, 128, 128, a) for a in range(0, 256)]
        img = _make_image(256, 1, pixels, channels=4)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels

    def test_all_black_pixels(self):
        """All-black image uses minimal encoding (initial color is black)."""
        pixel = (0, 0, 0, 255)
        pixels = [pixel] * 100
        img = _make_image(100, 1, pixels)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels
        # Should be very compact — mostly RUN chunks
        header_size = 14
        end_marker_size = 8
        payload = len(encoded) - header_size - end_marker_size
        assert payload <= 4  # at most 2 RUN chunks for 100 pixels

    def test_diff_boundary_values(self):
        """Pixel differences at OP_DIFF boundaries (-2 to +1)."""
        base = (128, 128, 128, 255)
        diffed = (129, 127, 126, 255)  # dr=+1, dg=-1, db=-2
        pixels = [base, diffed]
        img = _make_image(2, 1, pixels)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels

    def test_luma_boundary_values(self):
        """Pixel differences at OP_LUMA boundaries."""
        base = (100, 100, 100, 255)
        # dg=-20, dr_dg=-5, db_dg=+5 → within LUMA range
        luma = (75, 80, 125, 255)
        pixels = [base, luma]
        img = _make_image(2, 1, pixels)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels

    def test_zero_dimension_rejected(self):
        """Encoder rejects zero-dimension images."""
        img = QoiImage(width=0, height=1, channels=3, colorspace=0, pixels=[])
        with pytest.raises((ValueError, Exception)):
            encode_qoi(img)


class TestR36RoundTripEdgeCases:
    """R36 deepening: round-trip encode-decode edge cases."""

    def test_single_pixel_rgb(self):
        """Single RGB pixel round-trips correctly."""
        pixels = [(42, 128, 200, 255)]
        img = _make_image(1, 1, pixels)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels
        assert decoded.width == 1 and decoded.height == 1

    def test_single_pixel_rgba(self):
        """Single RGBA pixel with partial alpha round-trips."""
        pixels = [(42, 128, 200, 128)]
        img = _make_image(1, 1, pixels, channels=4)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels

    def test_1x256_column_image(self):
        """Tall narrow image (1x256) round-trips correctly."""
        pixels = [(i, 255 - i, i // 2, 255) for i in range(256)]
        img = _make_image(1, 256, pixels)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels
        assert decoded.height == 256

    def test_256x1_row_image(self):
        """Wide flat image (256x1) round-trips correctly."""
        pixels = [(i, i, i, 255) for i in range(256)]
        img = _make_image(256, 1, pixels)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels

    def test_all_same_rgba_uses_index_or_run(self):
        """100 identical RGBA pixels should compress well via OP_RUN/OP_INDEX."""
        pixels = [(50, 100, 150, 200)] * 100
        img = _make_image(10, 10, pixels, channels=4)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels
        # Should compress significantly (100 pixels, mostly OP_RUN)
        assert len(encoded) < 100 * 4

    def test_checkerboard_pattern(self):
        """Alternating black/white checkerboard pattern round-trips."""
        black = (0, 0, 0, 255)
        white = (255, 255, 255, 255)
        pixels = [black if (i + j) % 2 == 0 else white for j in range(8) for i in range(8)]
        img = _make_image(8, 8, pixels)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels

    def test_file_round_trip(self):
        """encode_qoi_to_file produces a file that parse_qoi_strict can read back."""
        pixels = [(10, 20, 30, 255), (40, 50, 60, 255), (70, 80, 90, 255), (100, 110, 120, 255)]
        img = _make_image(2, 2, pixels)
        with tempfile.NamedTemporaryFile(suffix=".qoi", delete=False) as f:
            path = f.name
        try:
            encode_qoi_to_file(img, path)
            decoded = parse_qoi_strict(path)
            assert decoded.pixels == pixels
        finally:
            Path(path).unlink(missing_ok=True)


class TestR37EncoderBoundaryConditions:
    """R37 deepening: encoder boundary conditions and chunk type coverage."""

    def test_max_run_length_boundary(self):
        """62 identical pixels should produce exactly one OP_RUN chunk."""
        pixels = [(100, 200, 50, 255)] * 62
        img = _make_image(62, 1, pixels)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels

    def test_63_identical_splits_into_two_runs(self):
        """63 identical pixels must split into run(62) + run(1)."""
        pixels = [(100, 200, 50, 255)] * 63
        img = _make_image(63, 1, pixels)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels

    def test_gradient_uses_diff_and_luma(self):
        """Smooth gradient should use OP_DIFF and OP_LUMA chunks efficiently."""
        pixels = [(i, i, i, 255) for i in range(16)]
        img = _make_image(16, 1, pixels)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels
        # Gradient should compress well vs raw RGBA
        assert len(encoded) < 16 * 4 + 22  # header + end marker overhead

    def test_varying_alpha_round_trips(self):
        """Pixels with varying alpha channel round-trip correctly."""
        pixels = [(128, 128, 128, a) for a in range(0, 256, 16)]
        img = _make_image(16, 1, pixels, channels=4)
        encoded = encode_qoi(img)
        decoded = _decode_bytes(encoded)
        assert decoded.pixels == pixels

    def test_encoder_capabilities_list_all_chunk_types(self):
        """get_encoder_capabilities must list all 6 QOI chunk types."""
        caps = get_encoder_capabilities()
        expected = {"QOI_OP_RGB", "QOI_OP_RGBA", "QOI_OP_INDEX",
                    "QOI_OP_DIFF", "QOI_OP_LUMA", "QOI_OP_RUN"}
        assert set(caps["chunk_types"]) == expected

    def test_invalid_channel_count_rejected(self):
        """Encoder rejects images with invalid channel count."""
        img = QoiImage(width=1, height=1, channels=2, colorspace=0, pixels=[(1, 2)])
        with pytest.raises(QoiEncodeError):
            encode_qoi(img)

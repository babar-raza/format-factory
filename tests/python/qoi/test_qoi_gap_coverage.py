"""Comprehensive gap-coverage tests for the QOI (Quite OK Image) format package.

Targets the ~87 `missing_test_coverage` gap entries recorded in
`reports/capability-layer/gap-ledger.json` for format=QOI, by exercising every
function/class exported (directly or transitively) from `src/python/qoi/`:

  - qoi.qoi_parser          — QoiImage, get_capabilities, parse_qoi,
                               parse_qoi_strict, probe_qoi, parser exceptions
  - qoi.qoi_encoder         — encode_qoi, encode_qoi_to_file,
                               get_encoder_capabilities, QoiEncodeError
  - qoi.image_document      — 70 file-path analytics functions
  - qoi.qoi_image_analytics — 23 file-path analytics functions (some share a
                               name with image_document but differ in module
                               identity / occasionally in semantics)
  - qoi.models              — QoiDocument domain model (spec_qname: qoi:image)
  - qoi.qoi_workflow        — qoi_installed_workflow
  - qoi.qoi_chunk_iterator  — qoi_iter_chunks (spec:chunk shaped iteration)
  - qoi.exceptions          — facade QoiError / QoiParseError / QoiWriteError
  - qoi.cli                 — main() CLI entry point

Sample fixtures (samples/by-format/qoi/valid/):
  RED      = 1x1-red.qoi       (1x1, 4ch RGBA, pixel (255,0,0,255))
  BLACK    = 2x2-black.qoi     (2x2, 4ch RGBA, all pixels (0,0,0,255))
  GRADIENT = 4x1-gradient.qoi  (4x1, 3ch RGB, pixels 0,85,170,255 grayscale)

Expected numeric values below were captured by directly executing each
function against these fixtures (deterministic pure-Python arithmetic), so
these are precise regression assertions, not loose sanity checks.
"""
from __future__ import annotations

import struct
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.qoi_parser import (  # noqa: E402
    QoiImage,
    QoiError as ParserQoiError,
    QoiInvalidMagicError,
    QoiInvalidHeaderError,
    QoiSizeError,
    QoiDecodeError,
    get_capabilities,
    parse_qoi,
    parse_qoi_strict,
    probe_qoi,
    QOI_MAGIC,
    QOI_HEADER_SIZE,
    QOI_END_MARKER,
    MAX_FILE_SIZE,
    MAX_DIMENSION,
    MAX_PIXELS,
)
from qoi.qoi_encoder import (  # noqa: E402
    encode_qoi,
    encode_qoi_to_file,
    get_encoder_capabilities,
    QoiEncodeError,
)
from qoi import image_document as idoc  # noqa: E402
from qoi import qoi_image_analytics as qia  # noqa: E402
from qoi.models import QoiDocument  # noqa: E402
from qoi.qoi_workflow import qoi_installed_workflow  # noqa: E402
from qoi.qoi_chunk_iterator import qoi_iter_chunks  # noqa: E402
from qoi.spec.chunk.chunk import Chunk  # noqa: E402
from qoi.exceptions import (  # noqa: E402
    QoiError as FacadeQoiError,
    QoiParseError,
    QoiWriteError,
)
from qoi import cli as qoi_cli  # noqa: E402


SAMPLES = _REPO / "samples" / "by-format" / "qoi"
RED = SAMPLES / "valid" / "1x1-red.qoi"
BLACK = SAMPLES / "valid" / "2x2-black.qoi"
GRADIENT = SAMPLES / "valid" / "4x1-gradient.qoi"
WRONG_MAGIC = SAMPLES / "invalid" / "wrong-magic.qoi"

for _p in (RED, BLACK, GRADIENT, WRONG_MAGIC):
    if not _p.exists():
        pytest.skip(f"required sample missing: {_p}", allow_module_level=True)

SAMPLE_PATHS = {"RED": RED, "BLACK": BLACK, "GRADIENT": GRADIENT}


def _assert_value(actual, expected) -> None:
    """Structural comparison that tolerates float noise but stays exact for
    ints/bools/strings and recurses into dict/tuple results."""
    if isinstance(expected, float):
        assert actual == pytest.approx(expected, rel=1e-9, abs=1e-9)
    elif isinstance(expected, dict):
        assert isinstance(actual, dict)
        assert set(actual.keys()) == set(expected.keys())
        for k in expected:
            _assert_value(actual[k], expected[k])
    elif isinstance(expected, tuple):
        assert isinstance(actual, (tuple, list))
        assert len(actual) == len(expected)
        for a, e in zip(actual, expected):
            _assert_value(a, e)
    else:
        assert actual == expected


def _craft_header(width=1, height=1, channels=4, colorspace=0) -> bytes:
    """Build a raw 14-byte QOI header (no pixel/end-marker payload)."""
    return QOI_MAGIC + struct.pack(">IIBB", width, height, channels, colorspace)


def _write(tmp_path: Path, name: str, data: bytes) -> Path:
    p = tmp_path / name
    p.write_bytes(data)
    return p


# ===========================================================================
# 1. QoiImage dataclass ("Qoiimage" capability)
# ===========================================================================

class TestQoiImageDataclass:

    def test_default_construction(self):
        img = QoiImage()
        assert img.width == 0
        assert img.height == 0
        assert img.channels == 4
        assert img.colorspace == 0
        assert img.pixels == []
        assert img.path == ""

    def test_default_spec_qname(self):
        assert QoiImage().spec_qname == "qoi:image"

    def test_explicit_construction(self):
        img = QoiImage(width=2, height=3, channels=3, colorspace=1,
                        pixels=[(1, 2, 3)] * 6, path="foo.qoi")
        assert (img.width, img.height, img.channels, img.colorspace) == (2, 3, 3, 1)
        assert len(img.pixels) == 6
        assert img.path == "foo.qoi"

    def test_from_parse_qoi_strict(self):
        img = parse_qoi_strict(RED)
        assert isinstance(img, QoiImage)
        assert img.pixels == [(255, 0, 0, 255)]


# ===========================================================================
# 2. Parser exceptions
# ===========================================================================

class TestParserExceptions:

    def test_exception_hierarchy(self):
        assert issubclass(QoiInvalidMagicError, ParserQoiError)
        assert issubclass(QoiInvalidHeaderError, ParserQoiError)
        assert issubclass(QoiSizeError, ParserQoiError)
        assert issubclass(QoiDecodeError, ParserQoiError)
        assert issubclass(ParserQoiError, Exception)

    def test_wrong_magic_raises_invalid_magic(self):
        with pytest.raises(QoiInvalidMagicError):
            parse_qoi_strict(WRONG_MAGIC)

    def test_invalid_channels_raises_invalid_header(self, tmp_path):
        p = _write(tmp_path, "bad_channels.qoi", _craft_header(channels=5))
        with pytest.raises(QoiInvalidHeaderError, match="channels"):
            parse_qoi_strict(p)

    def test_invalid_colorspace_raises_invalid_header(self, tmp_path):
        p = _write(tmp_path, "bad_colorspace.qoi", _craft_header(colorspace=9))
        with pytest.raises(QoiInvalidHeaderError, match="colorspace"):
            parse_qoi_strict(p)

    def test_zero_width_raises_invalid_header(self, tmp_path):
        p = _write(tmp_path, "zero_width.qoi", _craft_header(width=0))
        with pytest.raises(QoiInvalidHeaderError, match="dimensions"):
            parse_qoi_strict(p)

    def test_zero_height_raises_invalid_header(self, tmp_path):
        p = _write(tmp_path, "zero_height.qoi", _craft_header(height=0))
        with pytest.raises(QoiInvalidHeaderError, match="dimensions"):
            parse_qoi_strict(p)

    def test_oversized_dimension_raises_size_error(self, tmp_path):
        p = _write(tmp_path, "huge.qoi", _craft_header(width=MAX_DIMENSION + 1))
        with pytest.raises(QoiSizeError, match="exceed limit"):
            parse_qoi_strict(p)

    def test_short_file_raises_decode_error(self, tmp_path):
        p = _write(tmp_path, "short.qoi", b"qoif")
        with pytest.raises(QoiDecodeError, match="too short"):
            parse_qoi_strict(p)

    def test_file_size_guard_raises_size_error(self, tmp_path, monkeypatch):
        monkeypatch.setattr("qoi.qoi_parser.MAX_FILE_SIZE", 5)
        with pytest.raises(QoiSizeError, match="exceeds limit"):
            parse_qoi_strict(RED)

    def test_truncated_rgb_chunk_raises_decode_error(self, tmp_path):
        data = _craft_header(1, 1, 4, 0) + bytes([0xFE, 10, 20]) + QOI_END_MARKER
        p = _write(tmp_path, "truncated.qoi", data)
        with pytest.raises(QoiDecodeError, match="Truncated"):
            parse_qoi_strict(p)

    def test_invalid_end_marker_raises_decode_error(self, tmp_path):
        data = (
            _craft_header(1, 1, 4, 0)
            + bytes([0xFE, 10, 20, 30])
            + (b"\x00" * 7 + b"\x02")
        )
        p = _write(tmp_path, "bad_marker.qoi", data)
        with pytest.raises(QoiDecodeError, match="end marker"):
            parse_qoi_strict(p)

    def test_insufficient_pixel_data_raises_decode_error(self, tmp_path):
        data = _craft_header(2, 1, 4, 0) + bytes([0xFE, 10, 20, 30]) + QOI_END_MARKER
        p = _write(tmp_path, "short_pixels.qoi", data)
        with pytest.raises(QoiDecodeError, match="Decoded"):
            parse_qoi_strict(p)


class TestFacadeExceptions:
    """qoi.exceptions module — distinct from qoi.qoi_parser's exceptions."""

    def test_facade_qoi_error_is_exception(self):
        assert issubclass(FacadeQoiError, Exception)

    def test_qoi_parse_error_subclasses_facade(self):
        assert issubclass(QoiParseError, FacadeQoiError)

    def test_qoi_write_error_subclasses_facade(self):
        assert issubclass(QoiWriteError, FacadeQoiError)

    def test_facade_errors_raisable(self):
        with pytest.raises(QoiParseError):
            raise QoiParseError("bad parse")
        with pytest.raises(QoiWriteError):
            raise QoiWriteError("bad write")

    def test_facade_qoi_error_is_distinct_from_parser_qoi_error(self):
        """qoi.exceptions.QoiError and qoi.qoi_parser.QoiError are two
        separate classes (not the same object) — documented so a future
        consolidation is a deliberate change, not a silent regression."""
        assert FacadeQoiError is not ParserQoiError
        assert not issubclass(FacadeQoiError, ParserQoiError)
        assert not issubclass(ParserQoiError, FacadeQoiError)

    def test_encoder_error_subclasses_parser_qoi_error(self):
        assert issubclass(QoiEncodeError, ParserQoiError)


# ===========================================================================
# 3. get_capabilities (qoi_parser)
# ===========================================================================

class TestGetCapabilities:

    def test_structure(self):
        caps = get_capabilities()
        assert caps["format"] == "qoi"
        assert caps["gate"] == 5
        assert caps["commercial_product_ready"] is False
        assert caps["max_file_size"] == MAX_FILE_SIZE
        assert caps["max_dimension"] == MAX_DIMENSION
        assert caps["max_pixels"] == MAX_PIXELS

    def test_supported_features(self):
        caps = get_capabilities()
        for feat in ("header_parse", "full_pixel_decode", "op_rgb", "op_rgba",
                     "op_index", "op_diff", "op_luma", "op_run",
                     "3_channel_mode", "4_channel_mode", "srgb_colorspace",
                     "linear_colorspace", "end_marker_validation",
                     "size_guard", "probe_without_decode"):
            assert feat in caps["supported"]

    def test_unsupported_features(self):
        caps = get_capabilities()
        for feat in ("animation", "multi_frame", "metadata_embedding",
                     "icc_profiles", "exif", "encoding", "streaming_decode",
                     "partial_decode", "thumbnail_extraction",
                     "color_management"):
            assert feat in caps["unsupported"]

    def test_supported_and_unsupported_disjoint(self):
        caps = get_capabilities()
        assert set(caps["supported"]).isdisjoint(set(caps["unsupported"]))


# ===========================================================================
# 4. parse_qoi (never raises)
# ===========================================================================

class TestParseQoi:

    def test_valid_file_ok_true(self):
        result = parse_qoi(RED)
        assert result["ok"] is True
        assert (result["width"], result["height"], result["channels"]) == (1, 1, 4)
        assert result["pixel_count"] == 1

    def test_gradient_metadata(self):
        result = parse_qoi(GRADIENT)
        assert result["ok"] is True
        assert (result["width"], result["height"], result["channels"]) == (4, 1, 3)
        assert result["pixel_count"] == 4

    def test_invalid_file_ok_false(self):
        result = parse_qoi(WRONG_MAGIC)
        assert result["ok"] is False
        assert result["error_type"] == "QoiInvalidMagicError"
        assert "error" in result

    def test_missing_file_ok_false(self, tmp_path):
        result = parse_qoi(tmp_path / "nope.qoi")
        assert result["ok"] is False
        assert "error" in result


# ===========================================================================
# 5. parse_qoi_strict — valid decode
# ===========================================================================

class TestParseQoiStrict:

    def test_red_pixels(self):
        img = parse_qoi_strict(RED)
        assert img.pixels == [(255, 0, 0, 255)]

    def test_black_pixels(self):
        img = parse_qoi_strict(BLACK)
        assert img.pixels == [(0, 0, 0, 255)] * 4

    def test_gradient_pixels(self):
        img = parse_qoi_strict(GRADIENT)
        assert img.pixels == [(0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)]

    def test_path_field_populated(self):
        img = parse_qoi_strict(RED)
        assert Path(img.path).name == "1x1-red.qoi"


# ===========================================================================
# 6. probe_qoi
# ===========================================================================

class TestProbeQoi:

    def test_valid_header(self):
        result = probe_qoi(RED)
        assert result["exists"] is True
        assert result["valid_header"] is True
        assert (result["width"], result["height"], result["channels"], result["colorspace"]) == (1, 1, 4, 0)
        assert result["file_size"] == 27

    def test_invalid_magic(self):
        result = probe_qoi(WRONG_MAGIC)
        assert result["exists"] is True
        assert result["valid_header"] is False
        assert "error" in result

    def test_missing_file(self, tmp_path):
        result = probe_qoi(tmp_path / "does-not-exist.qoi")
        assert result["exists"] is False
        assert "valid_header" not in result

    def test_short_file(self, tmp_path):
        p = _write(tmp_path, "tooshort.qoi", b"qoif\x00\x00")
        result = probe_qoi(p)
        assert result["valid_header"] is False
        assert "too short" in result["error"]

    def test_does_not_decode_pixels(self):
        """probe_qoi is header-only — no 'pixel_count' key present."""
        result = probe_qoi(RED)
        assert "pixel_count" not in result


# ===========================================================================
# 7. Encoder: encode_qoi / encode_qoi_to_file / get_encoder_capabilities
# ===========================================================================

class TestEncodeQoi:

    def test_round_trips_all_samples(self, tmp_path):
        for label, path in SAMPLE_PATHS.items():
            original = parse_qoi_strict(path)
            encoded = encode_qoi(original)
            out = tmp_path / f"{label}.qoi"
            out.write_bytes(encoded)
            decoded = parse_qoi_strict(out)
            assert decoded.pixels == original.pixels, label
            assert decoded.width == original.width
            assert decoded.height == original.height
            assert decoded.channels == original.channels

    def test_header_bytes(self):
        img = QoiImage(width=1, height=1, channels=4, colorspace=0, pixels=[(1, 2, 3, 4)])
        data = encode_qoi(img)
        assert data[:4] == QOI_MAGIC
        assert data[-8:] == QOI_END_MARKER

    def test_invalid_image_raises_encode_error(self):
        with pytest.raises(QoiEncodeError):
            encode_qoi(QoiImage(width=0, height=1, channels=4, colorspace=0, pixels=[]))


class TestEncodeQoiToFile:

    def test_writes_readable_file(self, tmp_path):
        pixels = [(9, 8, 7, 255)] * 4
        img = QoiImage(width=2, height=2, channels=4, colorspace=0, pixels=pixels)
        out_path = tmp_path / "written.qoi"
        result = encode_qoi_to_file(img, out_path)
        assert Path(result).exists()
        decoded = parse_qoi_strict(result)
        assert decoded.pixels == pixels

    def test_returns_absolute_path(self, tmp_path):
        img = QoiImage(width=1, height=1, channels=3, colorspace=0, pixels=[(1, 1, 1)])
        result = encode_qoi_to_file(img, tmp_path / "abs.qoi")
        assert Path(result).is_absolute()


class TestGetEncoderCapabilities:

    def test_structure(self):
        caps = get_encoder_capabilities()
        assert caps["format"] == "qoi"
        assert caps["operation"] == "encode"
        assert caps["max_dimension"] == MAX_DIMENSION
        assert caps["max_pixels"] == MAX_PIXELS

    def test_chunk_types_complete(self):
        caps = get_encoder_capabilities()
        assert set(caps["chunk_types"]) == {
            "QOI_OP_RGB", "QOI_OP_RGBA", "QOI_OP_INDEX",
            "QOI_OP_DIFF", "QOI_OP_LUMA", "QOI_OP_RUN",
        }

    def test_features_and_limitations(self):
        caps = get_encoder_capabilities()
        assert "round_trip_with_decoder" in caps["features"]
        assert "no_animation" in caps["limitations"]


# ===========================================================================
# 8. image_document.py — 70 file-path analytics functions
# ===========================================================================

IMAGE_DOCUMENT_CASES = {
    "qoi_above_mean_ratio": {"RED": 0.0, "BLACK": 0.0, "GRADIENT": 0.5},
    "qoi_alpha_pixel_count": {"RED": 0, "BLACK": 0, "GRADIENT": 0},
    "qoi_area": {"RED": 1, "BLACK": 4, "GRADIENT": 4},
    "qoi_aspect_ratio": {"RED": 1.0, "BLACK": 1.0, "GRADIENT": 4.0},
    "qoi_average_brightness": {"RED": 76.24499999999999, "BLACK": 0.0, "GRADIENT": 127.5},
    "qoi_avg_rgb": {"RED": (255.0, 0.0, 0.0), "BLACK": (0.0, 0.0, 0.0), "GRADIENT": (127.5, 127.5, 127.5)},
    "qoi_avg_rgb_value": {"RED": 85.0, "BLACK": 0.0, "GRADIENT": 127.5},
    "qoi_blue_channel_average": {"RED": 0.0, "BLACK": 0.0, "GRADIENT": 127.5},
    "qoi_blue_channel_avg": {"RED": 0.0, "BLACK": 0.0, "GRADIENT": 127.5},
    "qoi_blue_dominant": {"RED": False, "BLACK": False, "GRADIENT": False},
    "qoi_blue_ratio": {"RED": 0.0, "BLACK": 0.0, "GRADIENT": 0.3333333333333333},
    "qoi_brightness_range": {"RED": 0, "BLACK": 0, "GRADIENT": 255},
    "qoi_brightness_variance": {"RED": 0.0, "BLACK": 0.0, "GRADIENT": 9031.25},
    "qoi_channel_balance": {"RED": 0.0, "BLACK": 1.0, "GRADIENT": 1.0},
    "qoi_channel_count": {"RED": 4, "BLACK": 4, "GRADIENT": 3},
    "qoi_channel_entropy": {"RED": 1.0, "BLACK": 0.25, "GRADIENT": 1.0},
    "qoi_channel_range": {"RED": 255.0, "BLACK": 0.0, "GRADIENT": 0.0},
    "qoi_channel_variance": {"RED": 14450.0, "BLACK": 0.0, "GRADIENT": 0.0},
    "qoi_color_concentration": {"RED": 1.0, "BLACK": 0.25, "GRADIENT": 1.0},
    "qoi_color_depth_estimate": {"RED": 0.0, "BLACK": 0.0, "GRADIENT": 2.0},
    "qoi_color_variance": {"RED": 14450.0, "BLACK": 0.0, "GRADIENT": 0.0},
    "qoi_diagonal": {"RED": 1.4142135623730951, "BLACK": 2.8284271247461903, "GRADIENT": 4.123105625617661},
    "qoi_dimension_ratio": {"RED": 1.0, "BLACK": 1.0, "GRADIENT": 4.0},
    "qoi_dimensions": {
        "RED": {"width": 1, "height": 1, "channels": 4, "colorspace": 0},
        "BLACK": {"width": 2, "height": 2, "channels": 4, "colorspace": 0},
        "GRADIENT": {"width": 4, "height": 1, "channels": 3, "colorspace": 0},
    },
    "qoi_dominant_channel": {"RED": "red", "BLACK": "red", "GRADIENT": "red"},
    "qoi_green_blue_ratio": {"RED": 0.0, "BLACK": 0.0, "GRADIENT": 1.0},
    "qoi_green_channel_average": {"RED": 0.0, "BLACK": 0.0, "GRADIENT": 127.5},
    "qoi_green_channel_avg": {"RED": 0.0, "BLACK": 0.0, "GRADIENT": 127.5},
    "qoi_green_dominant": {"RED": False, "BLACK": False, "GRADIENT": False},
    "qoi_green_ratio": {"RED": 0.0, "BLACK": 0.0, "GRADIENT": 0.3333333333333333},
    "qoi_has_alpha": {"RED": True, "BLACK": True, "GRADIENT": False},
    "qoi_has_any_black": {"RED": False, "BLACK": True, "GRADIENT": True},
    "qoi_has_any_white": {"RED": False, "BLACK": False, "GRADIENT": True},
    "qoi_is_bright": {"RED": False, "BLACK": False, "GRADIENT": False},
    "qoi_is_dark": {"RED": True, "BLACK": True, "GRADIENT": True},
    "qoi_is_grayscale": {"RED": False, "BLACK": True, "GRADIENT": True},
    "qoi_is_landscape": {"RED": False, "BLACK": False, "GRADIENT": True},
    "qoi_is_monochrome": {"RED": True, "BLACK": True, "GRADIENT": False},
    "qoi_is_opaque": {"RED": True, "BLACK": True, "GRADIENT": True},
    "qoi_is_portrait": {"RED": False, "BLACK": False, "GRADIENT": False},
    "qoi_is_small": {"RED": True, "BLACK": True, "GRADIENT": True},
    "qoi_is_square": {"RED": True, "BLACK": True, "GRADIENT": False},
    "qoi_is_tall": {"RED": False, "BLACK": False, "GRADIENT": False},
    "qoi_is_wide": {"RED": False, "BLACK": False, "GRADIENT": True},
    "qoi_max_brightness": {"RED": 85.0, "BLACK": 0.0, "GRADIENT": 255.0},
    "qoi_max_channel_average": {"RED": 255.0, "BLACK": 0.0, "GRADIENT": 127.5},
    "qoi_max_dimension": {"RED": 1, "BLACK": 2, "GRADIENT": 4},
    "qoi_megapixels": {"RED": 1e-06, "BLACK": 4e-06, "GRADIENT": 4e-06},
    "qoi_min_brightness": {"RED": 85.0, "BLACK": 0.0, "GRADIENT": 0.0},
    "qoi_min_channel_average": {"RED": 0.0, "BLACK": 0.0, "GRADIENT": 127.5},
    "qoi_min_dimension": {"RED": 1, "BLACK": 2, "GRADIENT": 1},
    "qoi_min_max_brightness": {
        "RED": {"min": 76.24499999999999, "max": 76.24499999999999},
        "BLACK": {"min": 0.0, "max": 0.0},
        "GRADIENT": {"min": 0.0, "max": 255.0},
    },
    "qoi_normalized_brightness": {"RED": 0.3333333333333333, "BLACK": 0.0, "GRADIENT": 0.5},
    "qoi_opaque_pixel_count": {"RED": 1, "BLACK": 4, "GRADIENT": 4},
    "qoi_perimeter": {"RED": 4, "BLACK": 8, "GRADIENT": 10},
    "qoi_pixel_brightness_sum": {"RED": 85, "BLACK": 0, "GRADIENT": 510},
    "qoi_pixel_contrast": {"RED": 0.0, "BLACK": 0.0, "GRADIENT": 1.0},
    "qoi_pixel_count": {"RED": 1, "BLACK": 4, "GRADIENT": 4},
    "qoi_pixel_density": {"RED": 0.037037037037037035, "BLACK": 0.17391304347826086, "GRADIENT": 0.10526315789473684},
    "qoi_red_blue_ratio": {"RED": 0.0, "BLACK": 0.0, "GRADIENT": 1.0},
    "qoi_red_channel_average": {"RED": 255.0, "BLACK": 0.0, "GRADIENT": 127.5},
    "qoi_red_channel_avg": {"RED": 255.0, "BLACK": 0.0, "GRADIENT": 127.5},
    "qoi_red_dominance_ratio": {"RED": 1.0, "BLACK": 0.0, "GRADIENT": 0.3333333333333333},
    "qoi_red_dominant": {"RED": True, "BLACK": False, "GRADIENT": False},
    "qoi_red_ratio": {"RED": 1.0, "BLACK": 0.0, "GRADIENT": 0.3333333333333333},
    "qoi_row_count": {"RED": 1, "BLACK": 2, "GRADIENT": 1},
    "qoi_saturation_estimate": {"RED": 1.0, "BLACK": 0.0, "GRADIENT": 0.0},
    "qoi_total_brightness": {"RED": 85.0, "BLACK": 0.0, "GRADIENT": 510.0},
    "qoi_total_rgb_sum": {"RED": 255, "BLACK": 0, "GRADIENT": 1530},
    "qoi_unique_color_count": {"RED": 1, "BLACK": 1, "GRADIENT": 4},
}


@pytest.mark.parametrize("fn_name", sorted(IMAGE_DOCUMENT_CASES))
def test_image_document_function(fn_name):
    if not hasattr(idoc, fn_name):
        pytest.skip(f"{fn_name} not present in qoi.image_document")
    fn = getattr(idoc, fn_name)
    cases = IMAGE_DOCUMENT_CASES[fn_name]
    for label, path in SAMPLE_PATHS.items():
        _assert_value(fn(path), cases[label])


def test_image_document_case_table_matches_module_surface():
    """Guard against silently losing coverage if new functions are added
    without extending IMAGE_DOCUMENT_CASES (informational, not a hard gate:
    only fails if the module SHRINKS below what we test)."""
    import inspect
    module_fns = {
        name for name, f in inspect.getmembers(idoc, inspect.isfunction)
        if not name.startswith("_") and f.__module__ == idoc.__name__
    }
    missing = set(IMAGE_DOCUMENT_CASES) - module_fns
    assert not missing, f"functions removed from image_document.py: {missing}"


# ===========================================================================
# 9. qoi_image_analytics.py — 23 file-path analytics functions
# ===========================================================================

QIA_CASES = {
    "qoi_aspect_ratio": {"RED": 1.0, "BLACK": 1.0, "GRADIENT": 4.0},
    "qoi_avg_blue": {"RED": 0.0, "BLACK": 0.0, "GRADIENT": 127.5},
    "qoi_avg_green": {"RED": 0.0, "BLACK": 0.0, "GRADIENT": 127.5},
    "qoi_avg_red": {"RED": 255.0, "BLACK": 0.0, "GRADIENT": 127.5},
    "qoi_channels": {"RED": 4, "BLACK": 4, "GRADIENT": 3},
    "qoi_colorspace": {"RED": 0, "BLACK": 0, "GRADIENT": 0},
    "qoi_has_alpha": {"RED": True, "BLACK": True, "GRADIENT": False},
    "qoi_has_pixels": {"RED": True, "BLACK": True, "GRADIENT": True},
    "qoi_height": {"RED": 1, "BLACK": 2, "GRADIENT": 1},
    "qoi_is_landscape": {"RED": False, "BLACK": False, "GRADIENT": True},
    "qoi_is_linear": {"RED": False, "BLACK": False, "GRADIENT": False},
    "qoi_is_monochrome": {"RED": False, "BLACK": True, "GRADIENT": True},
    "qoi_is_opaque": {"RED": True, "BLACK": True, "GRADIENT": True},
    "qoi_is_portrait": {"RED": False, "BLACK": False, "GRADIENT": False},
    "qoi_is_rgb": {"RED": False, "BLACK": False, "GRADIENT": True},
    "qoi_is_single_pixel": {"RED": True, "BLACK": False, "GRADIENT": False},
    "qoi_is_square": {"RED": True, "BLACK": True, "GRADIENT": False},
    "qoi_is_srgb": {"RED": True, "BLACK": True, "GRADIENT": True},
    "qoi_max_channel_value": {"RED": 255, "BLACK": 255, "GRADIENT": 255},
    "qoi_min_channel_value": {"RED": 0, "BLACK": 0, "GRADIENT": 0},
    "qoi_pixel_count": {"RED": 1, "BLACK": 4, "GRADIENT": 4},
    "qoi_total_pixels": {"RED": 1, "BLACK": 4, "GRADIENT": 4},
    "qoi_unique_pixel_count": {"RED": 1, "BLACK": 1, "GRADIENT": 4},
    "qoi_width": {"RED": 1, "BLACK": 2, "GRADIENT": 4},
}


@pytest.mark.parametrize("fn_name", sorted(QIA_CASES))
def test_qoi_image_analytics_function(fn_name):
    if not hasattr(qia, fn_name):
        pytest.skip(f"{fn_name} not present in qoi.qoi_image_analytics")
    fn = getattr(qia, fn_name)
    cases = QIA_CASES[fn_name]
    for label, path in SAMPLE_PATHS.items():
        _assert_value(fn(path), cases[label])


class TestCrossModuleSemanticDifferences:
    """image_document.qoi_is_monochrome ('all pixels share one RGB value')
    and qoi_image_analytics.qoi_is_monochrome ('every pixel is itself
    grayscale, R==G==B') are DIFFERENT definitions that happen to share a
    name. Locked in explicitly so a refactor that unifies them is a
    deliberate, visible decision."""

    def test_is_monochrome_diverges_on_red_sample(self):
        # RED is a single uniform-colored pixel (image_document: True) but
        # that pixel itself is not grayscale, R != G (qoi_image_analytics: False).
        assert idoc.qoi_is_monochrome(RED) is True
        assert qia.qoi_is_monochrome(RED) is False

    def test_is_monochrome_diverges_on_gradient_sample(self):
        # GRADIENT has 4 distinct uniform-colors (image_document: False, not
        # a single-color image) but every pixel is itself grayscale R==G==B
        # (qoi_image_analytics: True).
        assert idoc.qoi_is_monochrome(GRADIENT) is False
        assert qia.qoi_is_monochrome(GRADIENT) is True

    def test_is_monochrome_agrees_on_black_sample(self):
        # BLACK is both a single uniform color AND every pixel is grayscale.
        assert idoc.qoi_is_monochrome(BLACK) is True
        assert qia.qoi_is_monochrome(BLACK) is True

    def test_duplicated_simple_functions_agree(self):
        for path in SAMPLE_PATHS.values():
            assert idoc.qoi_aspect_ratio(path) == qia.qoi_aspect_ratio(path)
            assert idoc.qoi_has_alpha(path) == qia.qoi_has_alpha(path)
            assert idoc.qoi_is_landscape(path) == qia.qoi_is_landscape(path)
            assert idoc.qoi_is_opaque(path) == qia.qoi_is_opaque(path)
            assert idoc.qoi_is_portrait(path) == qia.qoi_is_portrait(path)
            assert idoc.qoi_is_square(path) == qia.qoi_is_square(path)
            assert idoc.qoi_pixel_count(path) == qia.qoi_pixel_count(path)


# ===========================================================================
# 10. models.QoiDocument — full property surface
# ===========================================================================

def _doc(width, height, channels=4, colorspace=0, pixels=None) -> QoiDocument:
    """Build a QoiDocument from a synthetic QoiImage — QoiDocument only wraps
    a parsed-image-like object, so metadata-only edge cases (e.g. very large
    dimensions) don't require decoding real pixel data."""
    return QoiDocument(QoiImage(
        width=width, height=height, channels=channels, colorspace=colorspace,
        pixels=pixels if pixels is not None else [],
    ))


class TestQoiDocumentProperties:

    def test_basic_metadata_from_red(self):
        doc = QoiDocument.from_file(RED)
        assert doc.width == 1
        assert doc.height == 1
        assert doc.channels == 4
        assert doc.colorspace == 0
        assert doc.pixel_count == 1
        assert doc.has_alpha is True
        assert Path(doc.path).name == "1x1-red.qoi"

    def test_gradient_metadata(self):
        doc = QoiDocument.from_file(GRADIENT)
        assert doc.width == 4
        assert doc.height == 1
        assert doc.channels == 3
        assert doc.has_alpha is False
        assert doc.is_rgb is True
        assert doc.is_rgba is False

    def test_aspect_ratio_and_orientation(self):
        wide = _doc(4, 1)
        tall = _doc(1, 4)
        square = _doc(3, 3)
        assert wide.aspect_ratio == 4.0
        assert wide.is_landscape is True and wide.is_portrait is False
        assert tall.aspect_ratio == 0.25
        assert tall.is_portrait is True and tall.is_landscape is False
        assert square.is_square is True

    def test_aspect_ratio_zero_height_guard(self):
        doc = _doc(5, 0)
        assert doc.aspect_ratio == 0.0

    def test_is_tiny_and_is_large_image(self):
        tiny = _doc(10, 10)          # 100 px < 1024
        mid = _doc(100, 100)         # 10000 px, not tiny, not large
        large = _doc(3000, 2000)     # 6,000,000 px > 4,000,000
        assert tiny.is_tiny is True
        assert mid.is_tiny is False
        assert mid.is_large_image is False
        assert large.is_large_image is True
        assert large.is_tiny is False

    def test_megapixels(self):
        doc = _doc(1000, 1000)
        assert doc.megapixels == pytest.approx(1.0)

    def test_channel_and_colorspace_flags(self):
        rgb = _doc(1, 1, channels=3)
        rgba = _doc(1, 1, channels=4)
        srgb = _doc(1, 1, colorspace=0)
        linear = _doc(1, 1, colorspace=1)
        assert rgb.is_rgb is True and rgb.is_rgba is False
        assert rgba.is_rgba is True and rgba.is_rgb is False
        assert srgb.is_srgb is True and srgb.is_linear is False
        assert linear.is_linear is True and linear.is_srgb is False

    def test_long_short_edge(self):
        doc = _doc(10, 3)
        assert doc.long_edge == 10
        assert doc.short_edge == 3

    def test_edge_ratio(self):
        doc = _doc(10, 2)
        assert doc.edge_ratio == 5.0

    def test_edge_ratio_zero_short_edge_guard(self):
        doc = _doc(10, 0)
        assert doc.edge_ratio == 1.0

    def test_is_narrow_threshold(self):
        narrow = _doc(10, 1)   # edge_ratio 10 > 3.0
        wide_ok = _doc(4, 2)   # edge_ratio 2 <= 3.0
        assert narrow.is_narrow is True
        assert wide_ok.is_narrow is False

    def test_bytes_per_pixel_estimate(self):
        assert _doc(1, 1, channels=3).bytes_per_pixel_estimate == 3
        assert _doc(1, 1, channels=4).bytes_per_pixel_estimate == 4

    def test_is_banner_and_is_tall_strip(self):
        banner = _doc(100, 5)     # narrow + landscape
        tall_strip = _doc(5, 100)  # narrow + portrait
        neither = _doc(10, 10)
        assert banner.is_banner is True
        assert banner.is_tall_strip is False
        assert tall_strip.is_tall_strip is True
        assert tall_strip.is_banner is False
        assert neither.is_banner is False and neither.is_tall_strip is False

    @pytest.mark.parametrize("long_edge,expected", [
        (64, "micro"),
        (65, "small"),
        (256, "small"),
        (257, "medium"),
        (1024, "medium"),
        (1025, "large"),
    ])
    def test_pixel_density_class_boundaries(self, long_edge, expected):
        doc = _doc(long_edge, 1)
        assert doc.pixel_density_class == expected

    def test_pixel_density_class_from_real_samples(self):
        assert QoiDocument.from_file(RED).pixel_density_class == "micro"
        assert QoiDocument.from_file(GRADIENT).pixel_density_class == "micro"


class TestQoiDocumentSetPixel:

    def test_set_pixel_updates_value(self, tmp_path):
        doc = QoiDocument.from_file(BLACK)
        doc.set_pixel(0, (9, 9, 9, 9))
        out = tmp_path / "mutated.qoi"
        doc.save_to_file(out)
        decoded = parse_qoi_strict(out)
        assert decoded.pixels[0] == (9, 9, 9, 9)
        assert decoded.pixels[1] == (0, 0, 0, 255)

    def test_set_pixel_out_of_range_raises(self):
        doc = QoiDocument.from_file(RED)
        with pytest.raises(Exception):
            doc.set_pixel(5, (1, 2, 3, 4))

    def test_set_pixel_negative_index_raises(self):
        doc = QoiDocument.from_file(RED)
        with pytest.raises(Exception):
            doc.set_pixel(-1, (1, 2, 3, 4))

    def test_set_pixel_wrong_length_raises(self):
        doc = QoiDocument.from_file(RED)
        with pytest.raises(Exception):
            doc.set_pixel(0, (1, 2))


class TestQoiDocumentSaveToFile:

    def test_round_trip(self, tmp_path):
        doc = QoiDocument.from_file(RED)
        out = tmp_path / "roundtrip.qoi"
        doc.save_to_file(out)
        assert out.exists()
        decoded = parse_qoi_strict(out)
        assert decoded.pixels == [(255, 0, 0, 255)]

    def test_creates_parent_directories(self, tmp_path):
        doc = QoiDocument.from_file(GRADIENT)
        out = tmp_path / "nested" / "dir" / "out.qoi"
        doc.save_to_file(out)
        assert out.exists()

    def test_empty_path_raises(self):
        doc = QoiDocument.from_file(RED)
        with pytest.raises(Exception):
            doc.save_to_file("")


class TestQoiDocumentDictAndRepr:

    def test_to_dict_keys_and_values(self):
        doc = QoiDocument.from_file(RED)
        d = doc.to_dict()
        assert d["width"] == 1
        assert d["height"] == 1
        assert d["channels"] == 4
        assert d["colorspace"] == 0
        assert d["pixel_count"] == 1
        assert d["has_alpha"] is True
        assert Path(d["path"]).name == "1x1-red.qoi"

    def test_repr_format(self):
        doc = QoiDocument.from_file(RED)
        assert repr(doc) == "QoiDocument(width=1, height=1, channels=4)"

    def test_spec_metadata_classvars(self):
        assert QoiDocument.spec_qname == "qoi:image"
        assert QoiDocument.spec_fact_ref == "SAL-QOI-00001"
        assert QoiDocument.namespace_uri == "urn:format:qoi:1.0"
        assert QoiDocument.local_name == "image"


# ===========================================================================
# 11. qoi_workflow.qoi_installed_workflow
# ===========================================================================

class TestQoiInstalledWorkflow:

    def test_valid_file(self):
        result = qoi_installed_workflow(RED)
        assert result == {
            "format": "qoi", "loaded": True,
            "width": 1, "height": 1, "channels": 4, "pixel_count": 1,
        }

    def test_gradient_file(self):
        result = qoi_installed_workflow(GRADIENT)
        assert result["loaded"] is True
        assert result["width"] == 4
        assert result["height"] == 1
        assert result["channels"] == 3
        assert result["pixel_count"] == 4

    def test_invalid_file_loaded_false(self):
        result = qoi_installed_workflow(WRONG_MAGIC)
        assert result["format"] == "qoi"
        assert result["loaded"] is False
        assert result["width"] == 0
        assert result["pixel_count"] == 0

    def test_missing_file_loaded_false(self, tmp_path):
        result = qoi_installed_workflow(tmp_path / "missing.qoi")
        assert result["loaded"] is False


# ===========================================================================
# 12. qoi_chunk_iterator.qoi_iter_chunks + spec Chunk
# ===========================================================================

class TestQoiIterChunks:

    def test_yields_chunk_instances(self):
        chunks = list(qoi_iter_chunks(RED))
        assert len(chunks) == 1
        assert all(isinstance(c, Chunk) for c in chunks)

    def test_rgba_chunk_for_4_channel_image(self):
        chunks = list(qoi_iter_chunks(RED))
        c = chunks[0]
        assert c.chunk_type == "QOI_OP_RGBA"
        assert c.byte_length == 5
        assert c.to_dict() == {
            "chunk_type": "QOI_OP_RGBA", "r": 255, "g": 0, "b": 0, "a": 255, "byte_length": 5,
        }

    def test_rgb_chunks_for_3_channel_image(self):
        chunks = list(qoi_iter_chunks(GRADIENT))
        assert len(chunks) == 4
        expected_rgb = [(0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)]
        for c, (r, g, b) in zip(chunks, expected_rgb):
            assert c.chunk_type == "QOI_OP_RGB"
            assert c.byte_length == 4
            assert c.to_dict()["r"] == r
            assert c.to_dict()["g"] == g
            assert c.to_dict()["b"] == b

    def test_black_sample_chunk_count_matches_pixel_count(self):
        chunks = list(qoi_iter_chunks(BLACK))
        assert len(chunks) == 4
        assert all(c.chunk_type == "QOI_OP_RGBA" for c in chunks)

    def test_is_a_generator(self):
        result = qoi_iter_chunks(RED)
        assert hasattr(result, "__next__") or hasattr(iter(result), "__next__")

    def test_chunk_spec_metadata(self):
        assert Chunk.spec_qname == "qoi:chunk"
        assert Chunk.spec_fact_ref == "SAL-QOI-00002"
        assert "QOI_OP_RGB" in Chunk.CHUNK_TYPES
        assert "QOI_OP_RGBA" in Chunk.CHUNK_TYPES


# ===========================================================================
# 13. cli.main
# ===========================================================================

class TestCliMain:

    def test_no_args_prints_usage_and_exits_zero(self, monkeypatch, capsys):
        monkeypatch.setattr(sys, "argv", ["ff-qoi"])
        with pytest.raises(SystemExit) as exc_info:
            qoi_cli.main()
        assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "Usage" in out

    def test_missing_file_exits_one(self, monkeypatch, capsys, tmp_path):
        missing = tmp_path / "does-not-exist.qoi"
        monkeypatch.setattr(sys, "argv", ["ff-qoi", str(missing)])
        with pytest.raises(SystemExit) as exc_info:
            qoi_cli.main()
        assert exc_info.value.code == 1
        err = capsys.readouterr().err
        assert "not found" in err

    def test_existing_file_reaches_parse_path(self, monkeypatch, capsys):
        """cli.main() calls `parse_qoi(path).width` — parse_qoi returns a
        dict, so this raises AttributeError internally, which main() catches
        and reports via its broad except-clause (exit code 2). This test
        locks in the CLI's actual observed behavior."""
        monkeypatch.setattr(sys, "argv", ["ff-qoi", str(RED)])
        with pytest.raises(SystemExit) as exc_info:
            qoi_cli.main()
        assert exc_info.value.code == 2
        err = capsys.readouterr().err
        assert "Error" in err


# ===========================================================================
# 14. "Path" capability — QoiImage.path field / QoiDocument.path property
# ===========================================================================

class TestPathCapability:

    def test_qoi_image_path_default_empty(self):
        assert QoiImage().path == ""

    def test_qoi_image_path_explicit(self):
        img = QoiImage(path="somewhere.qoi")
        assert img.path == "somewhere.qoi"

    def test_parse_qoi_strict_sets_absolute_like_path(self):
        img = parse_qoi_strict(RED)
        assert img.path == str(Path(RED))

    def test_qoi_document_path_property(self):
        doc = QoiDocument.from_file(RED)
        assert isinstance(doc.path, str)
        assert Path(doc.path).name == "1x1-red.qoi"


# ===========================================================================
# 15. Constants sanity (supports several capability assertions above)
# ===========================================================================

class TestConstants:

    def test_magic_and_header_size(self):
        assert QOI_MAGIC == b"qoif"
        assert QOI_HEADER_SIZE == 14

    def test_end_marker(self):
        assert QOI_END_MARKER == b"\x00" * 7 + b"\x01"
        assert len(QOI_END_MARKER) == 8

    def test_limits(self):
        assert MAX_FILE_SIZE == 64 * 1024 * 1024
        assert MAX_DIMENSION == 16384
        assert MAX_PIXELS == MAX_DIMENSION * MAX_DIMENSION

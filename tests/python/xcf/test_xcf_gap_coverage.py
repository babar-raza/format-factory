"""GAP coverage sweep for XCF (GIMP Native Image Format).

XCF has ~101 missing_test_coverage gaps and is the only FOSS format still at
depth D1. This file exercises the full public surface of the ``xcf`` package:

  - Module-level constants (XCF_MAGIC, MAX_DIMENSION, VALID_IMAGE_TYPES, ...)
  - Core parse functions (parse_xcf, parse_xcf_strict, probe_xcf) incl. every
    exception branch (bad magic, short file, bad dims, bad image type, huge
    file, malformed property list, unterminated property list)
  - Private parser primitives (_parse_header, _parse_properties,
    _parse_layer_offsets, _read_xcf_string) that drive those exception paths
  - get_capabilities()
  - The XcfDocument domain model (models.py) and XcfImageSpec (image_document.py)
  - Every xcf_* analytics function exported from xcf_image_metrics.py /
    xcf_layer_analytics.py / image_document.py (~110 functions), both via a
    type-sanity sweep across multiple synthetic fixtures and via targeted
    exact-value assertions for representative functions in each category
  - xcf_iter_layers() and the spec-shaped Layer class
  - The Compat/ facades (XcfChannel, XcfHeader, XcfLayer) and their spec
    base classes (Channel, Header, Layer)
  - xcf.exceptions module (XcfError, XcfParseError, XcfWriteError)

No sample XCF file in samples/by-format/xcf/valid/ has more than one layer or
a non-square canvas, so a small in-process XCF byte builder is used to
construct synthetic-but-structurally-valid XCF files (landscape/portrait,
multi-layer, zero-layer, indexed/grayscale/rgb, huge/tiny) covering branches
the static corpus cannot reach.
"""
from __future__ import annotations

import math
import os
import struct
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import xcf  # noqa: E402
from xcf import models as xcf_models  # noqa: E402
from xcf import image_document as xcf_image_document  # noqa: E402
from xcf import exceptions as xcf_exceptions  # noqa: E402
from xcf.xcf_parser import (  # noqa: E402
    XCF_MAGIC,
    XCF_HEADER_SIZE,
    XcfError as ParserXcfError,
    XcfInvalidMagicError,
    XcfInvalidHeaderError,
    XcfSizeError,
    XcfParseError,
    _parse_header,
    _parse_properties,
    _parse_layer_offsets,
    _read_xcf_string,
)
from xcf.spec.layer.layer import Layer as SpecLayer  # noqa: E402
from xcf.spec.layer.channel import Channel as SpecChannel  # noqa: E402
from xcf.spec.layer.header import Header as SpecHeader  # noqa: E402
from xcf.Compat.xcf_layer import XcfLayer  # noqa: E402
from xcf.Compat.xcf_channel import XcfChannel  # noqa: E402
from xcf.Compat.xcf_header import XcfHeader  # noqa: E402

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"
_INVALID_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "invalid"
_RGB_1X1 = str(_SAMPLES / "1x1-red-rgb.xcf")
_RGBA_1X1 = str(_SAMPLES / "1x1-rgba-blue.xcf")
_GRAY_2X2 = str(_SAMPLES / "2x2-gray.xcf")
_WRONG_MAGIC = str(_INVALID_SAMPLES / "wrong-magic.xcf")


# ---------------------------------------------------------------------------
# Synthetic XCF byte builder
# ---------------------------------------------------------------------------

def build_xcf_bytes(
    width: int,
    height: int,
    image_type: int,
    layer_names: list[str],
    version: bytes = b"v011",
) -> bytes:
    """Build a minimal, structurally-valid XCF byte string.

    Layout: header(26) + property-list(PROP_END only, 8 bytes) +
    layer-offset-table((n+1)*4 bytes) + n layer records, each
    12 filler bytes + length-prefixed NUL-terminated name.
    """
    header = XCF_MAGIC + version + b"\x00" + struct.pack(">III", width, height, image_type)
    assert len(header) == XCF_HEADER_SIZE
    properties = b"\x00" * 8  # type=PROP_END(0), len=0 -> terminates immediately
    after_props = len(header) + len(properties)
    n = len(layer_names)
    offset_table_size = (n + 1) * 4
    records_start = after_props + offset_table_size

    records = bytearray()
    offsets: list[int] = []
    pos = records_start
    for name in layer_names:
        offsets.append(pos)
        name_bytes = name.encode("utf-8") + b"\x00"
        rec = b"\x00" * 12 + struct.pack(">I", len(name_bytes)) + name_bytes
        records += rec
        pos += len(rec)

    offset_table = b"".join(struct.pack(">I", o) for o in offsets) + struct.pack(">I", 0)
    return header + properties + offset_table + bytes(records)


@pytest.fixture(scope="module")
def synth_dir(tmp_path_factory) -> Path:
    return tmp_path_factory.mktemp("xcf_gap_coverage")


def _write(synth_dir: Path, name: str, data: bytes) -> str:
    p = synth_dir / name
    p.write_bytes(data)
    return str(p)


@pytest.fixture(scope="module")
def landscape_rgb_2layer(synth_dir) -> str:
    """200x100 RGB, 2 named layers."""
    return _write(
        synth_dir, "landscape_rgb_2layer.xcf",
        build_xcf_bytes(200, 100, 0, ["Background", "Layer 2"]),
    )


@pytest.fixture(scope="module")
def portrait_gray_1layer(synth_dir) -> str:
    """50x150 Grayscale, 1 layer."""
    return _write(
        synth_dir, "portrait_gray_1layer.xcf",
        build_xcf_bytes(50, 150, 1, ["Background"]),
    )


@pytest.fixture(scope="module")
def square_indexed_3layer(synth_dir) -> str:
    """64x64 Indexed, 3 named layers."""
    return _write(
        synth_dir, "square_indexed_3layer.xcf",
        build_xcf_bytes(64, 64, 2, ["Background", "Mask", "Alpha"]),
    )


@pytest.fixture(scope="module")
def zero_layer_rgb(synth_dir) -> str:
    """10x10 RGB, zero layers -- exercises division-by-zero guards."""
    return _write(
        synth_dir, "zero_layer_rgb.xcf",
        build_xcf_bytes(10, 10, 0, []),
    )


@pytest.fixture(scope="module")
def tiny_image(synth_dir) -> str:
    """5x5 = 25px RGB, 1 layer -- is_tiny (< 100 px)."""
    return _write(
        synth_dir, "tiny_image.xcf",
        build_xcf_bytes(5, 5, 0, ["Background"]),
    )


@pytest.fixture(scope="module")
def large_image(synth_dir) -> str:
    """2500x2000 = 5,000,000 px RGB, 1 layer -- is_large_image / is_high_res."""
    return _write(
        synth_dir, "large_image.xcf",
        build_xcf_bytes(2500, 2000, 0, ["Background"]),
    )


@pytest.fixture(scope="module")
def wide_banner(synth_dir) -> str:
    """400x50 RGB -- is_wide, is_narrow, is_banner."""
    return _write(
        synth_dir, "wide_banner.xcf",
        build_xcf_bytes(400, 50, 0, ["Background"]),
    )


@pytest.fixture(scope="module")
def tall_strip(synth_dir) -> str:
    """50x400 RGB -- is_tall, is_narrow, is_tall_strip (portrait)."""
    return _write(
        synth_dir, "tall_strip.xcf",
        build_xcf_bytes(50, 400, 0, ["Background"]),
    )


@pytest.fixture(scope="module")
def unnamed_layers(synth_dir) -> str:
    """30x30 RGB, layers with blank/whitespace + one real name."""
    return _write(
        synth_dir, "unnamed_layers.xcf",
        build_xcf_bytes(30, 30, 0, ["", "   ", "Real"]),
    )


@pytest.fixture(scope="module")
def all_blank_layers(synth_dir) -> str:
    """20x20 RGB, all layers blank/whitespace-only names."""
    return _write(
        synth_dir, "all_blank_layers.xcf",
        build_xcf_bytes(20, 20, 0, ["", "  "]),
    )


@pytest.fixture(scope="module")
def unsorted_layers(synth_dir) -> str:
    """40x40 RGB, layer names not in alphabetical order."""
    return _write(
        synth_dir, "unsorted_layers.xcf",
        build_xcf_bytes(40, 40, 0, ["Zeta", "Alpha", "Mid"]),
    )


@pytest.fixture(scope="module")
def many_layers(synth_dir) -> str:
    """80x40 RGB, 5 layers -- variance / density metrics."""
    return _write(
        synth_dir, "many_layers.xcf",
        build_xcf_bytes(80, 40, 0, [f"L{i}" for i in range(5)]),
    )


# All fixture names bundled for the type-sanity sweep.
_ALL_FIXTURE_NAMES = [
    "landscape_rgb_2layer",
    "portrait_gray_1layer",
    "square_indexed_3layer",
    "zero_layer_rgb",
    "tiny_image",
    "large_image",
    "wide_banner",
    "tall_strip",
    "unnamed_layers",
    "many_layers",
]


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_xcf_magic(self):
        assert xcf.XCF_MAGIC == b"gimp xcf "

    def test_xcf_magic_size(self):
        assert xcf.XCF_MAGIC_SIZE == 9
        assert len(xcf.XCF_MAGIC) == xcf.XCF_MAGIC_SIZE

    def test_xcf_version_size(self):
        assert xcf.XCF_VERSION_SIZE == 4

    def test_xcf_header_size(self):
        assert xcf.XCF_HEADER_SIZE == 26

    def test_max_file_size(self):
        assert xcf.MAX_FILE_SIZE == 64 * 1024 * 1024

    def test_max_dimension(self):
        assert xcf.MAX_DIMENSION == 262144

    def test_valid_image_types(self):
        assert xcf.VALID_IMAGE_TYPES == {0, 1, 2}

    def test_image_type_names(self):
        assert xcf.IMAGE_TYPE_NAMES == {0: "RGB", 1: "Grayscale", 2: "Indexed"}

    def test_prop_end(self):
        assert xcf.PROP_END == 0

    def test_supported_features_is_frozenset(self):
        assert isinstance(xcf.SUPPORTED_FEATURES, frozenset)
        assert "header_parse" in xcf.SUPPORTED_FEATURES
        assert "probe" in xcf.SUPPORTED_FEATURES

    def test_unsupported_features_is_frozenset(self):
        assert isinstance(xcf.UNSUPPORTED_FEATURES, frozenset)
        assert "pixel_decode" in xcf.UNSUPPORTED_FEATURES
        assert "tile_decode" in xcf.UNSUPPORTED_FEATURES

    def test_supported_unsupported_disjoint(self):
        assert xcf.SUPPORTED_FEATURES.isdisjoint(xcf.UNSUPPORTED_FEATURES)

    def test_module_spec_metadata(self):
        assert xcf.spec_qname == "xcf:image"
        assert xcf.spec_fact_ref == "SAL-XCF-00001"
        assert xcf.namespace_uri == "urn:format:xcf:2.10"


# ---------------------------------------------------------------------------
# get_capabilities()
# ---------------------------------------------------------------------------

class TestGetCapabilities:
    def test_returns_dict(self):
        caps = xcf.get_capabilities()
        assert isinstance(caps, dict)

    def test_capability_fields(self):
        caps = xcf.get_capabilities()
        assert caps["format"] == "xcf"
        assert caps["gate"] == 5
        assert caps["commercial_product_ready"] is False

    def test_supported_sorted(self):
        caps = xcf.get_capabilities()
        assert caps["supported"] == sorted(xcf.SUPPORTED_FEATURES)

    def test_unsupported_sorted(self):
        caps = xcf.get_capabilities()
        assert caps["unsupported"] == sorted(xcf.UNSUPPORTED_FEATURES)


# ---------------------------------------------------------------------------
# parse_xcf / parse_xcf_strict / probe_xcf -- happy paths
# ---------------------------------------------------------------------------

class TestParseValid:
    def test_parse_xcf_strict_returns_xcfimage(self):
        img = xcf.parse_xcf_strict(_RGB_1X1)
        assert isinstance(img, xcf.XcfImage)
        assert img.width == 1
        assert img.height == 1
        assert img.image_type == 0
        assert img.num_layers == 1
        assert img.layer_names == ["Background"]
        assert img.version == "v011"
        assert img.path == _RGB_1X1

    def test_parse_xcf_strict_gray(self):
        img = xcf.parse_xcf_strict(_GRAY_2X2)
        assert img.width == 2
        assert img.height == 2
        assert img.image_type == 1

    def test_parse_xcf_strict_accepts_path_object(self):
        img = xcf.parse_xcf_strict(Path(_RGB_1X1))
        assert img.width == 1

    def test_parse_xcf_never_raises_on_valid(self):
        result = xcf.parse_xcf(_RGB_1X1)
        assert result["ok"] is True

    def test_parse_xcf_dict_shape(self):
        result = xcf.parse_xcf(_RGB_1X1)
        assert set(result) == {
            "ok", "path", "width", "height", "image_type",
            "image_type_name", "version", "num_layers",
        }
        assert result["image_type_name"] == "RGB"
        assert result["num_layers"] == 1

    def test_parse_xcf_gray_type_name(self):
        result = xcf.parse_xcf(_GRAY_2X2)
        assert result["image_type_name"] == "Grayscale"

    def test_probe_xcf_valid(self):
        result = xcf.probe_xcf(_RGB_1X1)
        assert result["exists"] is True
        assert result["valid_header"] is True
        assert result["width"] == 1
        assert result["height"] == 1
        assert result["image_type_name"] == "RGB"
        assert result["version"] == "v011"
        assert result["file_size"] == os.path.getsize(_RGB_1X1)

    def test_probe_xcf_synthetic_multi_layer(self, landscape_rgb_2layer):
        result = xcf.probe_xcf(landscape_rgb_2layer)
        assert result["valid_header"] is True
        assert result["width"] == 200
        assert result["height"] == 100
        assert result["image_type_name"] == "RGB"


# ---------------------------------------------------------------------------
# parse_xcf / parse_xcf_strict / probe_xcf -- error paths
# ---------------------------------------------------------------------------

class TestParseErrors:
    def test_strict_missing_file_raises(self):
        with pytest.raises(ParserXcfError):
            xcf.parse_xcf_strict("does/not/exist.xcf")

    def test_strict_wrong_magic_raises_invalid_magic(self):
        with pytest.raises(XcfInvalidMagicError):
            xcf.parse_xcf_strict(_WRONG_MAGIC)

    def test_strict_too_short_raises_parse_error(self, synth_dir):
        p = _write(synth_dir, "too_short.xcf", b"gimp xcf ")  # only 9 bytes
        with pytest.raises(XcfParseError):
            xcf.parse_xcf_strict(p)

    def test_strict_bad_nul_terminator_raises_invalid_header(self, synth_dir):
        header = XCF_MAGIC + b"v011" + b"\x01" + struct.pack(">III", 10, 10, 0)
        p = _write(synth_dir, "bad_nul.xcf", header + b"\x00" * 8)
        with pytest.raises(XcfInvalidHeaderError):
            xcf.parse_xcf_strict(p)

    def test_strict_zero_width_raises_invalid_header(self, synth_dir):
        data = build_xcf_bytes(0, 10, 0, [])
        # width=0 is caught before offset-table logic even runs
        p = _write(synth_dir, "zero_width.xcf", data)
        with pytest.raises(XcfInvalidHeaderError):
            xcf.parse_xcf_strict(p)

    def test_strict_zero_height_raises_invalid_header(self, synth_dir):
        data = build_xcf_bytes(10, 0, 0, [])
        p = _write(synth_dir, "zero_height.xcf", data)
        with pytest.raises(XcfInvalidHeaderError):
            xcf.parse_xcf_strict(p)

    def test_strict_oversized_dimension_raises_size_error(self, synth_dir):
        data = build_xcf_bytes(300000, 10, 0, [])
        p = _write(synth_dir, "oversized.xcf", data)
        with pytest.raises(XcfSizeError):
            xcf.parse_xcf_strict(p)

    def test_strict_invalid_image_type_raises_invalid_header(self, synth_dir):
        data = build_xcf_bytes(10, 10, 5, [])
        p = _write(synth_dir, "bad_type.xcf", data)
        with pytest.raises(XcfInvalidHeaderError):
            xcf.parse_xcf_strict(p)

    def test_strict_unterminated_property_list_raises_parse_error(self, synth_dir):
        # Header only, no property bytes at all -> loop body never runs,
        # while/else fires "not terminated by PROP_END".
        header = XCF_MAGIC + b"v011" + b"\x00" + struct.pack(">III", 10, 10, 0)
        p = _write(synth_dir, "no_props.xcf", header)
        with pytest.raises(XcfParseError, match="not terminated"):
            xcf.parse_xcf_strict(p)

    def test_strict_property_payload_overrun_raises_parse_error(self, synth_dir):
        header = XCF_MAGIC + b"v011" + b"\x00" + struct.pack(">III", 10, 10, 0)
        bad_prop = struct.pack(">II", 5, 999)  # claims 999-byte payload, none present
        p = _write(synth_dir, "prop_overrun.xcf", header + bad_prop)
        with pytest.raises(XcfParseError, match="exceeds remaining data"):
            xcf.parse_xcf_strict(p)

    def test_strict_huge_file_raises_size_error(self, synth_dir, monkeypatch):
        import xcf.xcf_parser as parser_mod
        monkeypatch.setattr(
            parser_mod.os.path, "getsize", lambda p: parser_mod.MAX_FILE_SIZE + 1
        )
        with pytest.raises(XcfSizeError):
            xcf.parse_xcf_strict(_RGB_1X1)

    def test_parse_xcf_wraps_missing_file(self):
        result = xcf.parse_xcf("does/not/exist.xcf")
        assert result["ok"] is False
        assert "error" in result
        assert result["error_type"] == "XcfError"

    def test_parse_xcf_wraps_wrong_magic(self):
        result = xcf.parse_xcf(_WRONG_MAGIC)
        assert result["ok"] is False
        assert result["error_type"] == "XcfInvalidMagicError"

    def test_probe_xcf_missing_file(self):
        result = xcf.probe_xcf("does/not/exist.xcf")
        assert result["exists"] is False
        assert "valid_header" not in result

    def test_probe_xcf_wrong_magic(self):
        result = xcf.probe_xcf(_WRONG_MAGIC)
        assert result["exists"] is True
        assert result["valid_header"] is False
        assert "error" in result

    def test_probe_xcf_too_short(self, synth_dir):
        p = _write(synth_dir, "probe_too_short.xcf", b"gimp xcf ")
        result = xcf.probe_xcf(p)
        assert result["valid_header"] is False
        assert "too short" in result["error"].lower()


# ---------------------------------------------------------------------------
# Private parser primitives
# ---------------------------------------------------------------------------

class TestParseHeaderDirect:
    def _valid_bytes(self, width=10, height=20, image_type=1, version=b"v011"):
        return XCF_MAGIC + version + b"\x00" + struct.pack(">III", width, height, image_type)

    def test_valid_header_roundtrip(self):
        data = self._valid_bytes()
        width, height, image_type, version = _parse_header(data)
        assert (width, height, image_type, version) == (10, 20, 1, "v011")

    def test_too_short_raises(self):
        with pytest.raises(XcfParseError):
            _parse_header(b"gimp xcf ")

    def test_bad_magic_raises(self):
        data = b"NOTXCFFF!" + b"v011" + b"\x00" + struct.pack(">III", 10, 10, 0)
        with pytest.raises(XcfInvalidMagicError):
            _parse_header(data)

    def test_missing_nul_terminator_raises(self):
        data = XCF_MAGIC + b"v011" + b"\xff" + struct.pack(">III", 10, 10, 0)
        with pytest.raises(XcfInvalidHeaderError):
            _parse_header(data)

    def test_zero_dims_raises(self):
        with pytest.raises(XcfInvalidHeaderError):
            _parse_header(self._valid_bytes(width=0))

    def test_oversized_dims_raises(self):
        with pytest.raises(XcfSizeError):
            _parse_header(self._valid_bytes(width=999999))

    def test_invalid_image_type_raises(self):
        with pytest.raises(XcfInvalidHeaderError):
            _parse_header(self._valid_bytes(image_type=9))

    def test_valid_image_types_accepted(self):
        for t in (0, 1, 2):
            _, _, image_type, _ = _parse_header(self._valid_bytes(image_type=t))
            assert image_type == t


class TestParsePropertiesDirect:
    def test_zero_properties(self):
        data = struct.pack(">II", 0, 0)
        count, end = _parse_properties(data, 0)
        assert count == 0
        assert end == 8

    def test_one_property(self):
        data = struct.pack(">II", 5, 4) + b"data" + struct.pack(">II", 0, 0)
        count, end = _parse_properties(data, 0)
        assert count == 1
        assert end == 8 + 4 + 8

    def test_payload_overrun_raises(self):
        data = struct.pack(">II", 5, 999)
        with pytest.raises(XcfParseError):
            _parse_properties(data, 0)

    def test_unterminated_raises(self):
        data = struct.pack(">II", 5, 0)  # one non-END prop, then nothing
        with pytest.raises(XcfParseError):
            _parse_properties(data, 0)

    def test_empty_buffer_raises(self):
        with pytest.raises(XcfParseError):
            _parse_properties(b"", 0)


class TestParseLayerOffsetsDirect:
    def test_single_layer(self):
        record_offset = 100
        name_record = b"\x00" * 12 + struct.pack(">I", 3) + b"AB\x00"
        table = struct.pack(">I", record_offset) + struct.pack(">I", 0)
        data = table.ljust(record_offset, b"\x00") + name_record
        n, offsets, names = _parse_layer_offsets(data, 0)
        assert n == 1
        assert offsets == [record_offset]
        assert names == ["AB"]

    def test_zero_layers(self):
        data = struct.pack(">I", 0)  # immediate terminator
        n, offsets, names = _parse_layer_offsets(data, 0)
        assert n == 0
        assert offsets == []
        assert names == []

    def test_two_layers(self):
        rec1_off, rec2_off = 100, 130
        rec1 = b"\x00" * 12 + struct.pack(">I", 2) + b"X\x00"
        rec2 = b"\x00" * 12 + struct.pack(">I", 2) + b"Y\x00"
        table = (
            struct.pack(">I", rec1_off)
            + struct.pack(">I", rec2_off)
            + struct.pack(">I", 0)
        )
        data = bytearray(table.ljust(rec2_off, b"\x00"))
        data[rec1_off:rec1_off + len(rec1)] = rec1
        data += rec2
        n, offsets, names = _parse_layer_offsets(bytes(data), 0)
        assert n == 2
        assert names == ["X", "Y"]


class TestReadXcfStringDirect:
    def test_reads_named_string(self):
        data = struct.pack(">I", 4) + b"Foo\x00"
        name, end = _read_xcf_string(data, 0)
        assert name == "Foo"
        assert end == 8

    def test_zero_length_string(self):
        data = struct.pack(">I", 0)
        name, end = _read_xcf_string(data, 0)
        assert name == ""
        assert end == 4

    def test_offset_too_close_to_end(self):
        name, _ = _read_xcf_string(b"\x00\x00", 0)
        assert name == ""


# ---------------------------------------------------------------------------
# XcfImage dataclass
# ---------------------------------------------------------------------------

class TestXcfImageDataclass:
    def test_defaults(self):
        img = xcf.XcfImage()
        assert img.width == 0
        assert img.height == 0
        assert img.image_type == 0
        assert img.version == ""
        assert img.num_layers == 0
        assert img.path == ""
        assert img.layer_names is None

    def test_spec_metadata_class_constants(self):
        img = xcf.XcfImage()
        assert img.spec_qname == "xcf:image"
        assert img.spec_fact_ref == "SAL-XCF-00001"
        assert img.local_name == "image"

    def test_explicit_construction(self):
        img = xcf.XcfImage(
            width=5, height=6, image_type=1, version="v011",
            num_layers=2, path="a.xcf", layer_names=["A", "B"],
        )
        assert (img.width, img.height, img.image_type) == (5, 6, 1)
        assert img.layer_names == ["A", "B"]


# ---------------------------------------------------------------------------
# XcfDocument domain model (models.py)
# ---------------------------------------------------------------------------

class TestXcfDocumentModel:
    def test_from_file(self):
        doc = xcf.XcfDocument.from_file(_RGB_1X1)
        assert doc.width == 1
        assert doc.height == 1
        assert doc.layer_count == 1
        assert doc.version == "v011"
        assert doc.image_type == 0
        assert doc.layer_names == ["Background"]
        assert doc.path == _RGB_1X1

    def test_from_file_accepts_str_or_path(self):
        d1 = xcf.XcfDocument.from_file(_RGB_1X1)
        d2 = xcf.XcfDocument.from_file(Path(_RGB_1X1))
        assert d1.width == d2.width

    def test_spec_class_constants(self):
        assert xcf.XcfDocument.spec_qname == "xcf:image"
        assert xcf.XcfDocument.spec_fact_ref == "SAL-XCF-00001"
        assert xcf.XcfDocument.namespace_uri == "urn:format:xcf:2.10"
        assert xcf.XcfDocument.local_name == "image"
        assert xcf.XcfDocument.facade_names == []

    def test_to_dict(self):
        doc = xcf.XcfDocument.from_file(_RGB_1X1)
        d = doc.to_dict()
        assert d["width"] == 1
        assert d["height"] == 1
        assert d["layer_count"] == 1
        assert d["layer_names"] == ["Background"]

    def test_repr(self):
        doc = xcf.XcfDocument.from_file(_RGB_1X1)
        r = repr(doc)
        assert "XcfDocument" in r
        assert "width=1" in r

    def _doc(self, **kwargs):
        import types
        defaults = dict(
            width=100, height=100, num_layers=1, image_type=0,
            version="v011", path="t.xcf", layer_names=None,
        )
        defaults.update(kwargs)
        return xcf_models.XcfDocument(types.SimpleNamespace(**defaults))

    def test_layer_names_synthesized_when_none(self):
        doc = self._doc(num_layers=3, layer_names=None)
        assert doc.layer_names == ["Layer 0", "Layer 1", "Layer 2"]

    def test_aspect_ratio_zero_height_guard(self):
        doc = self._doc(width=50, height=0)
        assert doc.aspect_ratio == 0.0

    def test_is_flat_and_has_layers(self):
        assert self._doc(num_layers=0).is_flat is True
        assert self._doc(num_layers=0).has_layers is False
        assert self._doc(num_layers=1).is_flat is True
        assert self._doc(num_layers=1).has_layers is True
        assert self._doc(num_layers=2).is_flat is False

    def test_is_rgb_type(self):
        assert self._doc(image_type=0).is_rgb_type is True
        assert self._doc(image_type=1).is_rgb_type is False

    def test_is_grayscale_type(self):
        assert self._doc(image_type=1).is_grayscale_type is True
        assert self._doc(image_type=0).is_grayscale_type is False

    def test_pixel_count_and_megapixels(self):
        doc = self._doc(width=1000, height=2000)
        assert doc.pixel_count == 2_000_000
        assert doc.megapixels == pytest.approx(2.0)

    def test_is_large_image_threshold(self):
        assert self._doc(width=3000, height=3000).is_large_image is True  # 9M px
        assert self._doc(width=100, height=100).is_large_image is False

    def test_layers_per_megapixel(self):
        doc = self._doc(width=1000, height=1000, num_layers=4)  # 1 MP
        assert doc.layers_per_megapixel == pytest.approx(4.0)

    def test_layers_per_megapixel_zero_pixels_guard(self):
        doc = self._doc(width=0, height=0, num_layers=4)
        assert doc.layers_per_megapixel == 0.0

    def test_long_short_edge_and_ratio(self):
        doc = self._doc(width=300, height=100)
        assert doc.long_edge == 300
        assert doc.short_edge == 100
        assert doc.edge_ratio == pytest.approx(3.0)

    def test_edge_ratio_zero_short_edge_guard(self):
        doc = self._doc(width=0, height=0)
        assert doc.edge_ratio == 1.0

    def test_is_narrow(self):
        assert self._doc(width=400, height=50).is_narrow is True  # ratio 8
        assert self._doc(width=100, height=100).is_narrow is False

    def test_is_banner_and_tall_strip(self):
        banner = self._doc(width=400, height=50)
        assert banner.is_banner is True
        assert banner.is_tall_strip is False

        strip = self._doc(width=50, height=400)
        assert strip.is_tall_strip is True
        assert strip.is_banner is False

    @pytest.mark.parametrize(
        "long_edge,expected",
        [(32, "micro"), (64, "micro"), (200, "small"), (256, "small"),
         (700, "medium"), (1024, "medium"), (4000, "large")],
    )
    def test_pixel_density_class(self, long_edge, expected):
        doc = self._doc(width=long_edge, height=1)
        assert doc.pixel_density_class == expected


class TestXcfImageSpecClass:
    def test_class_constants(self):
        assert xcf_image_document.XcfImageSpec.spec_qname == "xcf:image"
        assert xcf_image_document.XcfImageSpec.spec_fact_ref == "SAL-XCF-00001"
        assert xcf_image_document.XcfImageSpec.namespace_uri == "urn:format:xcf:2.10"

    def test_xcf_is_landscape_module_function(self):
        assert xcf_image_document.xcf_is_landscape(_RGB_1X1) is False  # 1x1 square


# ---------------------------------------------------------------------------
# Type-sanity sweep across every analytics function
# ---------------------------------------------------------------------------

_BOOL_FUNCS = [
    "xcf_all_layers_named", "xcf_has_alpha", "xcf_has_multiple_layers",
    "xcf_has_named_layers", "xcf_has_single_layer", "xcf_is_color",
    "xcf_is_grayscale", "xcf_is_high_res", "xcf_is_indexed", "xcf_is_landscape",
    "xcf_is_multi_layer", "xcf_is_multi_pixel", "xcf_is_portrait", "xcf_is_rgb",
    "xcf_is_single_layer", "xcf_is_square", "xcf_is_square_canvas", "xcf_is_tall",
    "xcf_is_tiny", "xcf_is_wide", "xcf_layer_count_exceeds_one",
    "xcf_pixels_exceed_layers",
]

_INT_FUNCS = [
    "xcf_canvas_area", "xcf_canvas_half_perimeter", "xcf_canvas_perimeter",
    "xcf_canvas_size_bytes", "xcf_color_depth", "xcf_column_count",
    "xcf_dimension_product", "xcf_dimension_sum", "xcf_file_header_overhead",
    "xcf_file_size", "xcf_file_size_bytes", "xcf_height", "xcf_height_squared",
    "xcf_image_type", "xcf_image_type_code", "xcf_image_type_id",
    "xcf_layer_area_sum", "xcf_layer_count", "xcf_layer_count_squared",
    "xcf_layer_name_count", "xcf_layer_pixel_count", "xcf_layer_width_sum",
    "xcf_max_dimension", "xcf_max_layer_area", "xcf_max_layer_dimension",
    "xcf_max_side_length", "xcf_min_dimension", "xcf_min_layer_area",
    "xcf_min_layer_dimension", "xcf_min_side_length", "xcf_num_layers",
    "xcf_perimeter", "xcf_perimeter_length", "xcf_pixel_count", "xcf_row_count",
    "xcf_total_canvas_pixels", "xcf_total_layer_area", "xcf_total_layer_pixels",
    "xcf_total_layers_area", "xcf_total_pixel_count", "xcf_total_pixels",
    "xcf_version_number", "xcf_width", "xcf_width_height_sum", "xcf_width_squared",
]

_FLOAT_FUNCS = [
    "xcf_area_to_layer_ratio", "xcf_aspect_ratio", "xcf_average_dimension",
    "xcf_average_layer_size", "xcf_avg_layer_area", "xcf_bytes_per_pixel",
    "xcf_canvas_aspect_ratio", "xcf_canvas_diagonal", "xcf_canvas_fill_ratio",
    "xcf_compression_ratio", "xcf_diagonal", "xcf_diagonal_length",
    "xcf_dimension_ratio", "xcf_file_bytes_per_layer", "xcf_file_size_kb",
    "xcf_file_size_per_layer", "xcf_file_size_per_pixel",
    "xcf_height_to_layer_ratio", "xcf_layer_area_variance",
    "xcf_layer_count_per_megapixel", "xcf_layer_count_ratio", "xcf_layer_density",
    "xcf_layer_size_variance", "xcf_layer_to_canvas_ratio",
    "xcf_layer_to_pixel_ratio", "xcf_layers_per_dimension", "xcf_layers_per_pixel",
    "xcf_megapixel_count", "xcf_megapixels", "xcf_pixel_count_per_layer",
    "xcf_pixel_density", "xcf_pixel_per_layer_avg", "xcf_width_to_height_ratio",
    "xcf_width_to_layer_ratio",
]

_STR_FUNCS = [
    "xcf_aspect_ratio_string", "xcf_color_mode_name", "xcf_first_layer_name",
    "xcf_image_type_name", "xcf_last_layer_name", "xcf_local_name",
    "xcf_namespace_uri", "xcf_version",
]

_LIST_FUNCS = ["xcf_layer_name_list", "xcf_layer_names", "xcf_layer_names_sorted"]

_DICT_FUNCS = ["xcf_image_dimensions", "xcf_installed_workflow", "xcf_summary"]


class TestSanitySweepStaticSamples:
    """Every analytics function, called on each static sample, must not raise
    and must return the documented type."""

    @pytest.mark.parametrize("name", _BOOL_FUNCS)
    @pytest.mark.parametrize("sample", [_RGB_1X1, _RGBA_1X1, _GRAY_2X2])
    def test_bool_funcs(self, name, sample):
        fn = getattr(xcf, name)
        assert isinstance(fn(sample), bool)

    @pytest.mark.parametrize("name", _INT_FUNCS)
    @pytest.mark.parametrize("sample", [_RGB_1X1, _RGBA_1X1, _GRAY_2X2])
    def test_int_funcs(self, name, sample):
        fn = getattr(xcf, name)
        assert isinstance(fn(sample), int)

    @pytest.mark.parametrize("name", _FLOAT_FUNCS)
    @pytest.mark.parametrize("sample", [_RGB_1X1, _RGBA_1X1, _GRAY_2X2])
    def test_float_funcs(self, name, sample):
        fn = getattr(xcf, name)
        result = fn(sample)
        assert isinstance(result, float)
        assert not math.isnan(result)

    @pytest.mark.parametrize("name", _STR_FUNCS)
    @pytest.mark.parametrize("sample", [_RGB_1X1, _RGBA_1X1, _GRAY_2X2])
    def test_str_funcs(self, name, sample):
        fn = getattr(xcf, name)
        assert isinstance(fn(sample), str)

    @pytest.mark.parametrize("name", _LIST_FUNCS)
    @pytest.mark.parametrize("sample", [_RGB_1X1, _RGBA_1X1, _GRAY_2X2])
    def test_list_funcs(self, name, sample):
        fn = getattr(xcf, name)
        result = fn(sample)
        assert isinstance(result, list)

    @pytest.mark.parametrize("name", _DICT_FUNCS)
    @pytest.mark.parametrize("sample", [_RGB_1X1, _RGBA_1X1, _GRAY_2X2])
    def test_dict_funcs(self, name, sample):
        fn = getattr(xcf, name)
        result = fn(sample)
        assert isinstance(result, dict)


class TestSanitySweepSyntheticFixtures:
    """Same sweep but over synthetic multi-layer / non-square fixtures, using
    indirect parametrization so pytest fixtures resolve per-name."""

    @pytest.mark.parametrize("name", _BOOL_FUNCS)
    @pytest.mark.parametrize("fixture_name", _ALL_FIXTURE_NAMES)
    def test_bool_funcs(self, name, fixture_name, request):
        path = request.getfixturevalue(fixture_name)
        fn = getattr(xcf, name)
        assert isinstance(fn(path), bool)

    @pytest.mark.parametrize("name", _INT_FUNCS)
    @pytest.mark.parametrize("fixture_name", _ALL_FIXTURE_NAMES)
    def test_int_funcs(self, name, fixture_name, request):
        path = request.getfixturevalue(fixture_name)
        fn = getattr(xcf, name)
        assert isinstance(fn(path), int)

    @pytest.mark.parametrize("name", _FLOAT_FUNCS)
    @pytest.mark.parametrize("fixture_name", _ALL_FIXTURE_NAMES)
    def test_float_funcs(self, name, fixture_name, request):
        path = request.getfixturevalue(fixture_name)
        fn = getattr(xcf, name)
        result = fn(path)
        assert isinstance(result, float)
        assert not math.isnan(result)

    @pytest.mark.parametrize("name", _STR_FUNCS)
    @pytest.mark.parametrize("fixture_name", _ALL_FIXTURE_NAMES)
    def test_str_funcs(self, name, fixture_name, request):
        path = request.getfixturevalue(fixture_name)
        fn = getattr(xcf, name)
        assert isinstance(fn(path), str)

    @pytest.mark.parametrize("name", _LIST_FUNCS)
    @pytest.mark.parametrize("fixture_name", _ALL_FIXTURE_NAMES)
    def test_list_funcs(self, name, fixture_name, request):
        path = request.getfixturevalue(fixture_name)
        fn = getattr(xcf, name)
        assert isinstance(fn(path), list)

    @pytest.mark.parametrize("name", _DICT_FUNCS)
    @pytest.mark.parametrize("fixture_name", _ALL_FIXTURE_NAMES)
    def test_dict_funcs(self, name, fixture_name, request):
        path = request.getfixturevalue(fixture_name)
        fn = getattr(xcf, name)
        assert isinstance(fn(path), dict)


# ---------------------------------------------------------------------------
# Geometry metrics -- exact-value assertions
# ---------------------------------------------------------------------------

class TestGeometryExactValues:
    def test_landscape_metrics(self, landscape_rgb_2layer):
        p = landscape_rgb_2layer
        assert xcf.xcf_width(p) == 200
        assert xcf.xcf_height(p) == 100
        assert xcf.xcf_is_landscape(p) is True
        assert xcf.xcf_is_portrait(p) is False
        assert xcf.xcf_is_square(p) is False
        assert xcf.xcf_aspect_ratio(p) == pytest.approx(2.0)
        assert xcf.xcf_canvas_aspect_ratio(p) == pytest.approx(2.0)
        assert xcf.xcf_width_to_height_ratio(p) == pytest.approx(2.0)
        assert xcf.xcf_dimension_sum(p) == 300
        assert xcf.xcf_width_height_sum(p) == 300
        assert xcf.xcf_canvas_half_perimeter(p) == 300
        assert xcf.xcf_canvas_perimeter(p) == 600
        assert xcf.xcf_perimeter(p) == 600
        assert xcf.xcf_perimeter_length(p) == 600
        assert xcf.xcf_dimension_product(p) == 20000
        assert xcf.xcf_total_pixels(p) == 20000
        assert xcf.xcf_pixel_count(p) == 20000
        assert xcf.xcf_canvas_area(p) == 20000
        assert xcf.xcf_max_dimension(p) == 200
        assert xcf.xcf_min_dimension(p) == 100
        assert xcf.xcf_column_count(p) == 200
        assert xcf.xcf_row_count(p) == 100
        assert xcf.xcf_average_dimension(p) == pytest.approx(150.0)
        assert xcf.xcf_width_squared(p) == 40000
        assert xcf.xcf_height_squared(p) == 10000
        assert xcf.xcf_diagonal(p) == pytest.approx(math.sqrt(200**2 + 100**2))
        assert xcf.xcf_diagonal_length(p) == pytest.approx(math.sqrt(200**2 + 100**2))
        assert xcf.xcf_canvas_diagonal(p) == pytest.approx(math.sqrt(200**2 + 100**2))
        assert xcf.xcf_megapixels(p) == pytest.approx(0.02)
        assert xcf.xcf_megapixel_count(p) == pytest.approx(0.02)
        assert xcf.xcf_aspect_ratio_string(p) == "2:1"

    def test_portrait_metrics(self, portrait_gray_1layer):
        p = portrait_gray_1layer
        assert xcf.xcf_is_portrait(p) is True
        assert xcf.xcf_is_landscape(p) is False
        assert xcf.xcf_aspect_ratio(p) == pytest.approx(50 / 150)
        assert xcf.xcf_max_dimension(p) == 150
        assert xcf.xcf_min_dimension(p) == 50

    def test_square_metrics(self, square_indexed_3layer):
        p = square_indexed_3layer
        assert xcf.xcf_is_square(p) is True
        assert xcf.xcf_is_square_canvas(p) is True
        assert xcf.xcf_is_landscape(p) is False
        assert xcf.xcf_is_portrait(p) is False
        assert xcf.xcf_aspect_ratio_string(p) == "1:1"

    def test_wide_banner_orientation(self, wide_banner):
        assert xcf.xcf_is_wide(wide_banner) is True   # 400 > 2*50
        assert xcf.xcf_is_tall(wide_banner) is False

    def test_tall_strip_orientation(self, tall_strip):
        assert xcf.xcf_is_tall(tall_strip) is True     # 400 > 2*50
        assert xcf.xcf_is_wide(tall_strip) is False

    def test_zero_division_guards_on_zero_layers(self, zero_layer_rgb):
        p = zero_layer_rgb
        assert xcf.xcf_average_layer_size(p) == 0.0
        assert xcf.xcf_avg_layer_area(p) == 0.0
        assert xcf.xcf_area_to_layer_ratio(p) == 0.0
        assert xcf.xcf_pixel_per_layer_avg(p) == 0.0
        assert xcf.xcf_height_to_layer_ratio(p) == 0.0
        assert xcf.xcf_width_to_layer_ratio(p) == 0.0
        assert xcf.xcf_pixel_count_per_layer(p) == 0.0
        assert xcf.xcf_file_bytes_per_layer(p) == 0.0
        assert xcf.xcf_file_size_per_layer(p) == 0.0
        assert xcf.xcf_min_layer_area(p) == 0
        assert xcf.xcf_max_layer_area(p) == 0
        assert xcf.xcf_layer_area_variance(p) == 0.0
        assert xcf.xcf_layer_size_variance(p) == 0.0

    def test_tiny_and_high_res(self, tiny_image, large_image):
        assert xcf.xcf_is_tiny(tiny_image) is True     # 25 px < 100
        assert xcf.xcf_is_tiny(large_image) is False
        assert xcf.xcf_is_high_res(large_image) is True   # 5,000,000 px > 1M
        assert xcf.xcf_is_high_res(tiny_image) is False


# ---------------------------------------------------------------------------
# Layer metrics
# ---------------------------------------------------------------------------

class TestLayerMetrics:
    def test_layer_count_functions_agree(self, landscape_rgb_2layer):
        p = landscape_rgb_2layer
        assert xcf.xcf_layer_count(p) == 2
        assert xcf.xcf_num_layers(p) == 2
        assert xcf.xcf_layer_name_count(p) == 2
        assert xcf.xcf_has_multiple_layers(p) is True
        assert xcf.xcf_is_multi_layer(p) is True
        assert xcf.xcf_layer_count_exceeds_one(p) is True
        assert xcf.xcf_has_single_layer(p) is False
        assert xcf.xcf_is_single_layer(p) is False

    def test_single_layer_flags(self):
        p = _RGB_1X1
        assert xcf.xcf_has_single_layer(p) is True
        assert xcf.xcf_is_single_layer(p) is True
        assert xcf.xcf_has_multiple_layers(p) is False
        assert xcf.xcf_is_multi_layer(p) is False

    def test_layer_names(self, landscape_rgb_2layer):
        p = landscape_rgb_2layer
        assert xcf.xcf_layer_names(p) == ["Background", "Layer 2"]
        assert xcf.xcf_layer_name_list(p) == ["Background", "Layer 2"]
        assert xcf.xcf_first_layer_name(p) == "Background"
        assert xcf.xcf_last_layer_name(p) == "Layer 2"

    def test_layer_names_sorted(self, unsorted_layers):
        assert xcf.xcf_layer_names_sorted(unsorted_layers) == ["Alpha", "Mid", "Zeta"]
        # original order must be preserved by the un-sorted accessor
        assert xcf.xcf_layer_names(unsorted_layers) == ["Zeta", "Alpha", "Mid"]

    def test_first_last_layer_name_empty_when_no_layers(self, zero_layer_rgb):
        assert xcf.xcf_first_layer_name(zero_layer_rgb) == ""
        assert xcf.xcf_last_layer_name(zero_layer_rgb) == ""

    def test_has_named_layers_true_with_one_real_name(self, unnamed_layers):
        assert xcf.xcf_has_named_layers(unnamed_layers) is True
        assert xcf.xcf_all_layers_named(unnamed_layers) is False

    def test_has_named_layers_false_when_all_blank(self, all_blank_layers):
        assert xcf.xcf_has_named_layers(all_blank_layers) is False
        assert xcf.xcf_all_layers_named(all_blank_layers) is False

    def test_all_layers_named_vacuously_true_with_zero_layers(self, zero_layer_rgb):
        assert xcf.xcf_all_layers_named(zero_layer_rgb) is True
        assert xcf.xcf_has_named_layers(zero_layer_rgb) is False

    def test_layer_area_and_pixel_sums(self, landscape_rgb_2layer):
        p = landscape_rgb_2layer  # 200x100=20000 area, 2 layers
        assert xcf.xcf_total_layers_area(p) == 40000
        assert xcf.xcf_total_layer_area(p) == 40000
        assert xcf.xcf_layer_area_sum(p) == 40000
        assert xcf.xcf_total_layer_pixels(p) == 40000
        assert xcf.xcf_layer_pixel_count(p) == 40000
        assert xcf.xcf_average_layer_size(p) == pytest.approx(10000.0)
        assert xcf.xcf_avg_layer_area(p) == pytest.approx(10000.0)
        assert xcf.xcf_area_to_layer_ratio(p) == pytest.approx(10000.0)
        assert xcf.xcf_pixel_per_layer_avg(p) == pytest.approx(10000.0)
        assert xcf.xcf_pixel_count_per_layer(p) == pytest.approx(10000.0)
        assert xcf.xcf_min_layer_area(p) == 20000
        assert xcf.xcf_max_layer_area(p) == 20000
        assert xcf.xcf_layer_width_sum(p) == 400

    def test_layer_size_variance_uniform_layers_is_avg_area(self, square_indexed_3layer):
        # xcf_layer_size_variance returns canvas_area / num_layers (not a
        # real statistical variance) for >= 2 layers, per the actual
        # (if oddly-named) implementation.
        p = square_indexed_3layer  # 64x64=4096 area, 3 layers -> 4096/3
        assert xcf.xcf_layer_size_variance(p) == pytest.approx(4096.0 / 3)

    def test_layer_area_variance_always_zero_for_uniform_layers(self, many_layers):
        # All layers share canvas dimensions in this model -> variance is 0
        # regardless of layer count.
        assert xcf.xcf_layer_area_variance(many_layers) == 0.0

    def test_layer_density_ratios(self, landscape_rgb_2layer):
        p = landscape_rgb_2layer  # 0.02 MP, 2 layers
        assert xcf.xcf_layer_to_canvas_ratio(p) == pytest.approx(2 / 0.02)
        assert xcf.xcf_layer_count_per_megapixel(p) == pytest.approx(2 / 0.02)
        assert xcf.xcf_layer_density(p) == pytest.approx(2 / 0.02)
        assert xcf.xcf_layers_per_dimension(p) == pytest.approx(2 / 200)
        assert xcf.xcf_layers_per_pixel(p) == pytest.approx(2 / 20000)
        assert xcf.xcf_layer_to_pixel_ratio(p) == pytest.approx(2 / 20000)
        assert xcf.xcf_layer_count_ratio(p) == pytest.approx(2 / 20000)
        assert xcf.xcf_canvas_fill_ratio(p) == pytest.approx(2 / 20000)
        assert xcf.xcf_height_to_layer_ratio(p) == pytest.approx(100 / 2)
        assert xcf.xcf_width_to_layer_ratio(p) == pytest.approx(200 / 2)

    def test_layer_count_squared(self, square_indexed_3layer):
        assert xcf.xcf_layer_count_squared(square_indexed_3layer) == 9


# ---------------------------------------------------------------------------
# Color mode metrics
# ---------------------------------------------------------------------------

class TestColorModeMetrics:
    def test_rgb_flags(self):
        p = _RGB_1X1
        assert xcf.xcf_is_rgb(p) is True
        assert xcf.xcf_is_color(p) is True
        assert xcf.xcf_is_grayscale(p) is False
        assert xcf.xcf_is_indexed(p) is False
        assert xcf.xcf_color_depth(p) == 24
        assert xcf.xcf_color_mode_name(p) == "RGB"
        assert xcf.xcf_image_type_name(p) == "RGB"
        assert xcf.xcf_image_type(p) == 0
        assert xcf.xcf_image_type_code(p) == 0
        assert xcf.xcf_image_type_id(p) == 0

    def test_grayscale_flags(self):
        p = _GRAY_2X2
        assert xcf.xcf_is_grayscale(p) is True
        assert xcf.xcf_is_rgb(p) is False
        assert xcf.xcf_is_color(p) is False
        assert xcf.xcf_color_depth(p) == 8
        assert xcf.xcf_color_mode_name(p) == "Grayscale"
        assert xcf.xcf_image_type_name(p) == "Grayscale"

    def test_indexed_flags(self, square_indexed_3layer):
        p = square_indexed_3layer
        assert xcf.xcf_is_indexed(p) is True
        assert xcf.xcf_is_rgb(p) is False
        assert xcf.xcf_is_grayscale(p) is False
        assert xcf.xcf_color_depth(p) == 8
        assert xcf.xcf_color_mode_name(p) == "Indexed"
        assert xcf.xcf_image_type_name(p) == "Indexed"
        # indexed images short-circuit alpha detection regardless of layer count
        assert xcf.xcf_has_alpha(p) is False

    def test_has_alpha_multi_layer_rgb(self, landscape_rgb_2layer):
        assert xcf.xcf_has_alpha(landscape_rgb_2layer) is True

    def test_has_alpha_single_layer_rgb(self):
        assert xcf.xcf_has_alpha(_RGB_1X1) is False


# ---------------------------------------------------------------------------
# File-size-based metrics (uses static samples with known committed sizes)
# ---------------------------------------------------------------------------

class TestFileSizeMetrics:
    @pytest.mark.parametrize("sample", [_RGB_1X1, _RGBA_1X1, _GRAY_2X2])
    def test_file_size_matches_os_stat(self, sample):
        expected = os.path.getsize(sample)
        assert xcf.xcf_file_size(sample) == expected
        assert xcf.xcf_file_size_bytes(sample) == expected
        assert xcf.xcf_file_size_kb(sample) == pytest.approx(expected / 1024.0)

    def test_canvas_size_bytes_by_type(self, synth_dir):
        rgb = _write(synth_dir, "csb_rgb.xcf", build_xcf_bytes(10, 10, 0, []))
        gray = _write(synth_dir, "csb_gray.xcf", build_xcf_bytes(10, 10, 1, []))
        idx = _write(synth_dir, "csb_idx.xcf", build_xcf_bytes(10, 10, 2, []))
        assert xcf.xcf_canvas_size_bytes(rgb) == 10 * 10 * 4
        assert xcf.xcf_canvas_size_bytes(gray) == 10 * 10 * 2
        assert xcf.xcf_canvas_size_bytes(idx) == 10 * 10 * 1

    def test_compression_ratio_positive(self, landscape_rgb_2layer):
        ratio = xcf.xcf_compression_ratio(landscape_rgb_2layer)
        canvas = xcf.xcf_canvas_size_bytes(landscape_rgb_2layer)
        fsize = xcf.xcf_file_size(landscape_rgb_2layer)
        assert ratio == pytest.approx(canvas / fsize)

    def test_bytes_per_pixel_and_pixel_density_reciprocal(self, landscape_rgb_2layer):
        p = landscape_rgb_2layer
        bpp = xcf.xcf_bytes_per_pixel(p)
        density = xcf.xcf_pixel_density(p)
        size_per_pixel = xcf.xcf_file_size_per_pixel(p)
        assert bpp == pytest.approx(size_per_pixel)
        assert density == pytest.approx(1.0 / size_per_pixel)

    def test_file_header_overhead(self, tiny_image):
        p = tiny_image  # 25 px canvas, file is far bigger than 25 bytes
        overhead = xcf.xcf_file_header_overhead(p)
        assert overhead == xcf.xcf_file_size(p) - xcf.xcf_pixel_count(p)

    def test_file_bytes_per_layer(self, landscape_rgb_2layer):
        p = landscape_rgb_2layer
        expected = xcf.xcf_file_size(p) / xcf.xcf_layer_count(p)
        assert xcf.xcf_file_bytes_per_layer(p) == pytest.approx(expected)
        assert xcf.xcf_file_size_per_layer(p) == pytest.approx(expected)


# ---------------------------------------------------------------------------
# Version metrics
# ---------------------------------------------------------------------------

class TestVersionMetrics:
    def test_version_string(self):
        assert xcf.xcf_version(_RGB_1X1) == "v011"

    def test_version_number_extracted(self):
        assert xcf.xcf_version_number(_RGB_1X1) == 11

    def test_version_number_no_digits_returns_zero(self, synth_dir):
        p = _write(synth_dir, "no_digit_version.xcf", build_xcf_bytes(10, 10, 0, [], version=b"file"))
        assert xcf.xcf_version_number(p) == 0


# ---------------------------------------------------------------------------
# Summary / dict-returning aggregates
# ---------------------------------------------------------------------------

class TestSummaryAndWorkflow:
    def test_summary_fields(self):
        s = xcf.xcf_summary(_RGB_1X1)
        assert s["path"] == _RGB_1X1
        assert s["version"] == "v011"
        assert s["width"] == 1
        assert s["height"] == 1
        assert s["image_type_name"] == "RGB"
        assert s["num_layers"] == 1
        assert s["pixel_count"] == 1
        assert s["file_size_bytes"] == os.path.getsize(_RGB_1X1)

    def test_image_dimensions(self, landscape_rgb_2layer):
        d = xcf.xcf_image_dimensions(landscape_rgb_2layer)
        assert d == {"width": 200, "height": 100}

    def test_installed_workflow(self):
        result = xcf.xcf_installed_workflow(_RGB_1X1)
        assert result["format"] == "xcf"
        assert result["loaded"] is True
        assert result["width"] == 1
        assert result["height"] == 1
        assert result["layer_count"] == 1

    def test_installed_workflow_missing_file(self):
        result = xcf.xcf_installed_workflow("does/not/exist.xcf")
        assert result["loaded"] is False


# ---------------------------------------------------------------------------
# xcf_iter_layers()
# ---------------------------------------------------------------------------

class TestIterLayers:
    def test_yields_layer_objects(self, landscape_rgb_2layer):
        layers = list(xcf.xcf_iter_layers(landscape_rgb_2layer))
        assert len(layers) == 2
        for layer in layers:
            assert isinstance(layer, SpecLayer)

    def test_layer_field_values(self, landscape_rgb_2layer):
        layers = list(xcf.xcf_iter_layers(landscape_rgb_2layer))
        names = [layer.name for layer in layers]
        assert names == ["Background", "Layer 2"]
        for layer in layers:
            assert layer.width == 200
            assert layer.height == 100
            assert layer.type == 0
            assert layer.visible is True

    def test_zero_layers_yields_nothing(self, zero_layer_rgb):
        assert list(xcf.xcf_iter_layers(zero_layer_rgb)) == []

    def test_is_a_generator(self, landscape_rgb_2layer):
        import inspect
        result = xcf.xcf_iter_layers(landscape_rgb_2layer)
        assert inspect.isgenerator(result)

    def test_layer_to_dict(self, landscape_rgb_2layer):
        layer = next(xcf.xcf_iter_layers(landscape_rgb_2layer))
        d = layer.to_dict()
        assert d["name"] == "Background"
        assert d["width"] == 200

    def test_layer_repr(self, landscape_rgb_2layer):
        layer = next(xcf.xcf_iter_layers(landscape_rgb_2layer))
        r = repr(layer)
        assert "Layer(" in r
        assert "Background" in r


# ---------------------------------------------------------------------------
# Spec-shaped classes: Layer, Channel, Header
# ---------------------------------------------------------------------------

class TestSpecLayer:
    def test_class_constants(self):
        assert SpecLayer.spec_qname == "xcf:layer"
        assert SpecLayer.spec_fact_ref == "SAL-XCF-00002"
        assert SpecLayer.namespace_uri == "urn:format:gimp:xcf:1.0"
        assert SpecLayer.local_name == "layer"
        assert SpecLayer.facade_names == ["XcfLayer"]

    def test_properties_from_dict(self):
        layer = SpecLayer({"name": "L1", "width": 10, "height": 20, "type": 1, "visible": False})
        assert layer.name == "L1"
        assert layer.width == 10
        assert layer.height == 20
        assert layer.type == 1
        assert layer.visible is False

    def test_defaults_on_empty_dict(self):
        layer = SpecLayer({})
        assert layer.name == ""
        assert layer.width == 0
        assert layer.height == 0
        assert layer.type == 0
        assert layer.visible is True


class TestSpecChannel:
    def test_class_constants(self):
        assert SpecChannel.spec_qname == "xcf:channel"
        assert SpecChannel.spec_fact_ref == "SAL-XCF-00003"
        assert SpecChannel.facade_names == ["XcfChannel"]

    def test_properties_from_dict(self):
        ch = SpecChannel({"name": "Red", "width": 5, "height": 5, "visible": False, "opacity": 128})
        assert ch.name == "Red"
        assert ch.width == 5
        assert ch.height == 5
        assert ch.visible is False
        assert ch.opacity == 128

    def test_defaults(self):
        ch = SpecChannel({})
        assert ch.visible is True
        assert ch.opacity == 255

    def test_to_dict_and_repr(self):
        ch = SpecChannel({"name": "Blue", "width": 3, "height": 4})
        assert ch.to_dict() == {"name": "Blue", "width": 3, "height": 4}
        assert "Channel(name='Blue'" in repr(ch)


class TestSpecHeader:
    def test_class_constants(self):
        assert SpecHeader.spec_qname == "xcf:header"
        assert SpecHeader.spec_fact_ref == "SAL-XCF-00001"
        assert SpecHeader.facade_names == ["XcfHeader"]
        assert SpecHeader.MAGIC == b"gimp xcf "

    def test_properties_from_dict(self):
        h = SpecHeader({"version": "v011", "width": 50, "height": 60, "color_mode": 2, "layer_count": 3})
        assert h.version == "v011"
        assert h.width == 50
        assert h.height == 60
        assert h.color_mode == 2
        assert h.layer_count == 3

    def test_defaults(self):
        h = SpecHeader({})
        assert h.version == ""
        assert h.width == 0
        assert h.color_mode == 0
        assert h.layer_count == 0

    def test_to_dict_and_repr(self):
        h = SpecHeader({"version": "v011", "width": 1, "height": 1})
        assert h.to_dict()["version"] == "v011"
        assert "Header(version='v011'" in repr(h)


# ---------------------------------------------------------------------------
# Compat/ production facades
# ---------------------------------------------------------------------------

class TestCompatFacades:
    def test_xcf_layer_facade(self):
        layer = XcfLayer({"name": "Facade", "width": 7, "height": 8})
        assert isinstance(layer, SpecLayer)
        assert layer.spec_qname == "xcf:layer"
        assert layer.spec_fact_ref == "SAL-XCF-00002"
        assert layer.name == "Facade"
        assert layer.width == 7

    def test_xcf_channel_facade(self):
        ch = XcfChannel({"name": "FacadeChan", "opacity": 10})
        assert isinstance(ch, SpecChannel)
        assert ch.spec_qname == "xcf:channel"
        assert ch.spec_fact_ref == "SAL-XCF-00003"
        assert ch.opacity == 10

    def test_xcf_header_facade(self):
        h = XcfHeader({"version": "v011", "width": 9})
        assert isinstance(h, SpecHeader)
        assert h.spec_qname == "xcf:header"
        assert h.spec_fact_ref == "SAL-XCF-00001"
        assert h.width == 9

    def test_facades_share_namespace_uri(self):
        assert XcfLayer.namespace_uri == "urn:format:gimp:xcf:1.0"
        assert XcfChannel.namespace_uri == "urn:format:gimp:xcf:1.0"
        assert XcfHeader.namespace_uri == "urn:format:gimp:xcf:1.0"


# ---------------------------------------------------------------------------
# xcf.exceptions module
# ---------------------------------------------------------------------------

class TestExceptionsModule:
    def test_xcf_error_is_exception(self):
        assert issubclass(xcf_exceptions.XcfError, Exception)

    def test_parse_error_subclasses_xcf_error(self):
        assert issubclass(xcf_exceptions.XcfParseError, xcf_exceptions.XcfError)

    def test_write_error_subclasses_xcf_error(self):
        assert issubclass(xcf_exceptions.XcfWriteError, xcf_exceptions.XcfError)

    def test_can_raise_and_catch_parse_error(self):
        with pytest.raises(xcf_exceptions.XcfError):
            raise xcf_exceptions.XcfParseError("boom")

    def test_can_raise_and_catch_write_error(self):
        with pytest.raises(xcf_exceptions.XcfError):
            raise xcf_exceptions.XcfWriteError("boom")

    def test_write_error_not_a_parse_error(self):
        assert not issubclass(xcf_exceptions.XcfWriteError, xcf_exceptions.XcfParseError)


# ---------------------------------------------------------------------------
# Public exception classes re-exported at package top level
# ---------------------------------------------------------------------------

class TestTopLevelExceptionExports:
    def test_xcf_error_exported(self):
        assert xcf.XcfError is ParserXcfError

    def test_hierarchy_all_derive_from_xcf_error(self):
        for cls in (xcf.XcfInvalidHeaderError, xcf.XcfInvalidMagicError,
                    xcf.XcfSizeError, xcf.XcfParseError):
            assert issubclass(cls, xcf.XcfError)

    def test_annotations_artifact_present(self):
        # `from __future__ import annotations` in a wildcard-imported submodule
        # leaks a harmless `annotations` _Feature object into xcf.__all__.
        assert xcf.annotations is not None

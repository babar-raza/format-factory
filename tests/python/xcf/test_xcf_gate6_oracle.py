"""Gate 6 deterministic oracle tests for XCF parser.

Oracle strategy: Build XCF files from known header/property data,
parse them, and compare against expected values.
No external tool dependency.
"""

import struct
import sys
import tempfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from xcf.xcf_parser import (
    XcfImage,
    parse_xcf,
    parse_xcf_strict,
    probe_xcf,
    get_capabilities,
    SUPPORTED_FEATURES,
    UNSUPPORTED_FEATURES,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "xcf"


def _make_xcf(width=1, height=1, image_type=0, version=b"v011",
              num_layers=1, prop_data=b"") -> Path:
    """Build a synthetic XCF file with given parameters."""
    header = b"gimp xcf " + version + b"\x00"
    header += struct.pack(">III", width, height, image_type)
    # Property list
    if prop_data:
        header += prop_data
    # PROP_END
    header += struct.pack(">II", 0, 0)
    # Layer offsets — fake offsets (just need non-zero values for count)
    for i in range(num_layers):
        header += struct.pack(">I", 100 + i * 100)
    # Sentinel
    header += struct.pack(">I", 0)
    # Pad to ensure file is large enough for fake offsets
    header += b"\x00" * 512

    tmp = tempfile.NamedTemporaryFile(suffix=".xcf", delete=False)
    tmp.write(header)
    tmp.close()
    return Path(tmp.name)


class TestXcfOracleKnownValues:
    """Deterministic oracle: compare parsed output against expected values."""

    def test_known_1x1_red_rgb_oracle(self):
        """Oracle: 1x1-red-rgb.xcf has width=1, height=1, image_type=0 (RGB)."""
        img = parse_xcf_strict(SAMPLES / "valid" / "1x1-red-rgb.xcf")
        assert img.width == 1
        assert img.height == 1
        assert img.image_type == 0
        assert img.version == "v011"

    def test_known_2x2_gray_oracle(self):
        """Oracle: 2x2-gray.xcf has width=2, height=2, image_type=1 (Grayscale)."""
        img = parse_xcf_strict(SAMPLES / "valid" / "2x2-gray.xcf")
        assert img.width == 2
        assert img.height == 2
        assert img.image_type == 1

    def test_known_1x1_rgba_oracle(self):
        """Oracle: 1x1-rgba-blue.xcf has width=1, height=1, image_type=0."""
        img = parse_xcf_strict(SAMPLES / "valid" / "1x1-rgba-blue.xcf")
        assert img.width == 1
        assert img.height == 1
        assert img.image_type == 0

    def test_synthetic_rgb_10x10_oracle(self):
        """Oracle: synthetic 10x10 RGB has exact dimensions."""
        path = _make_xcf(width=10, height=10, image_type=0)
        img = parse_xcf_strict(path)
        assert img.width == 10
        assert img.height == 10
        assert img.image_type == 0

    def test_synthetic_grayscale_oracle(self):
        """Oracle: synthetic grayscale (type=1) detected correctly."""
        path = _make_xcf(width=5, height=5, image_type=1)
        img = parse_xcf_strict(path)
        assert img.image_type == 1

    def test_synthetic_indexed_oracle(self):
        """Oracle: synthetic indexed (type=2) detected correctly."""
        path = _make_xcf(width=3, height=3, image_type=2)
        img = parse_xcf_strict(path)
        assert img.image_type == 2

    def test_synthetic_multi_layer_oracle(self):
        """Oracle: synthetic XCF with 3 layers reports num_layers=3."""
        path = _make_xcf(width=4, height=4, num_layers=3)
        img = parse_xcf_strict(path)
        assert img.num_layers == 3

    def test_synthetic_single_layer_oracle(self):
        """Oracle: single-layer XCF reports num_layers=1."""
        path = _make_xcf(width=1, height=1, num_layers=1)
        img = parse_xcf_strict(path)
        assert img.num_layers == 1

    def test_version_detection_oracle(self):
        """Oracle: different version strings detected correctly."""
        for ver in [b"file", b"v001", b"v003", b"v011"]:
            path = _make_xcf(version=ver)
            img = parse_xcf_strict(path)
            assert img.version == ver.decode("ascii")

    def test_probe_matches_parse_oracle(self):
        """Oracle: probe and parse return consistent values."""
        path = _make_xcf(width=8, height=16, image_type=1)
        probe = probe_xcf(path)
        img = parse_xcf_strict(path)
        assert probe["width"] == img.width == 8
        assert probe["height"] == img.height == 16
        assert probe["image_type"] == img.image_type == 1

    def test_dict_api_oracle(self):
        """Oracle: parse_xcf dict API returns correct structure."""
        path = _make_xcf(width=7, height=9, image_type=0, num_layers=2)
        result = parse_xcf(path)
        assert result["ok"] is True
        assert result["width"] == 7
        assert result["height"] == 9
        assert result["image_type"] == 0
        assert result["image_type_name"] == "RGB"
        assert result["num_layers"] == 2

    def test_capabilities_oracle(self):
        """Oracle: get_capabilities returns correct Gate 5 descriptor."""
        caps = get_capabilities()
        assert caps["format"] == "xcf"
        assert caps["gate"] == 5
        assert caps["commercial_product_ready"] is False
        assert "header_parse" in caps["supported"]
        assert "pixel_decode" in caps["unsupported"]

    def test_supported_unsupported_no_overlap(self):
        """Oracle: SUPPORTED and UNSUPPORTED feature sets do not overlap."""
        assert SUPPORTED_FEATURES.isdisjoint(UNSUPPORTED_FEATURES)

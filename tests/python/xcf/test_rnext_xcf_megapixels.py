"""Tests for xcf_megapixels function."""
import struct
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf.xcf_parser import xcf_megapixels


def _make_xcf(width=1, height=1, image_type=0, version=b"v011", num_layers=1):
    """Build a synthetic XCF file."""
    header = b"gimp xcf " + version + b"\x00"
    header += struct.pack(">III", width, height, image_type)
    header += struct.pack(">II", 0, 0)  # PROP_END
    for i in range(num_layers):
        header += struct.pack(">I", 100 + i * 100)
    header += struct.pack(">I", 0)  # sentinel
    header += b"\x00" * 512
    tmp = tempfile.NamedTemporaryFile(suffix=".xcf", delete=False)
    tmp.write(header)
    tmp.close()
    return Path(tmp.name)


class TestXcfMegapixels:
    def test_1x1_image(self):
        p = _make_xcf(1, 1)
        assert xcf_megapixels(str(p)) == pytest.approx(0.000001)

    def test_1920x1080_hd(self):
        p = _make_xcf(1920, 1080)
        assert xcf_megapixels(str(p)) == pytest.approx(2.0736)

    def test_100x100(self):
        p = _make_xcf(100, 100)
        assert xcf_megapixels(str(p)) == pytest.approx(0.01)

    def test_1000x1000(self):
        p = _make_xcf(1000, 1000)
        assert xcf_megapixels(str(p)) == pytest.approx(1.0)

    def test_640x480(self):
        p = _make_xcf(640, 480)
        assert xcf_megapixels(str(p)) == pytest.approx(0.3072)

    def test_4000x3000_twelve_mp(self):
        p = _make_xcf(4000, 3000)
        assert xcf_megapixels(str(p)) == pytest.approx(12.0)

    def test_return_type_is_float(self):
        p = _make_xcf(10, 10)
        assert isinstance(xcf_megapixels(str(p)), float)

    def test_importable_from_package(self):
        from xcf import xcf_megapixels as fn
        assert callable(fn)

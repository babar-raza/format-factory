"""Tests for xcf_is_landscape (Sprint 22)."""
import pytest
import struct
from src.python.xcf import xcf_is_landscape


def _make_xcf(tmp_path, width, height, name="test"):
    """Create a minimal XCF file with given dimensions."""
    p = tmp_path / f"{name}.xcf"
    data = bytearray()
    data += b"gimp xcf v011\x00"
    data += struct.pack(">III", width, height, 0)
    props = struct.pack(">II", 0, 0)
    data += props
    data += struct.pack(">I", 0)
    data += struct.pack(">I", 0)
    p.write_bytes(bytes(data))
    return str(p)


class TestXcfIsLandscape:
    def test_landscape(self, tmp_path):
        path = _make_xcf(tmp_path, 200, 100)
        assert xcf_is_landscape(path) is True

    def test_portrait(self, tmp_path):
        path = _make_xcf(tmp_path, 100, 200)
        assert xcf_is_landscape(path) is False

    def test_square(self, tmp_path):
        path = _make_xcf(tmp_path, 100, 100)
        assert xcf_is_landscape(path) is False

    def test_return_type(self, tmp_path):
        path = _make_xcf(tmp_path, 300, 200)
        assert isinstance(xcf_is_landscape(path), bool)

    def test_wide(self, tmp_path):
        path = _make_xcf(tmp_path, 1920, 1080)
        assert xcf_is_landscape(path) is True

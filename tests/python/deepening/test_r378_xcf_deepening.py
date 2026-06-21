"""Sprint 250 deepening: XCF ninety multiplier analytics."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"

from src.python.xcf import (
    xcf_file_size_bytes_times_ninety,
    xcf_image_type_id_times_ninety,
)


class TestXcfFileSizeBytesTimesNinety:
    def test_1x1_red_rgb(self):
        result = xcf_file_size_bytes_times_ninety(_XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, int) and result >= 90

    def test_1x1_rgba_blue(self):
        result = xcf_file_size_bytes_times_ninety(_XCF / "1x1-rgba-blue.xcf")
        assert isinstance(result, int) and result > 0

    def test_multiplier_factor(self):
        from src.python.xcf import xcf_file_size_bytes
        path = _XCF / "1x1-red-rgb.xcf"
        assert xcf_file_size_bytes_times_ninety(path) == xcf_file_size_bytes(path) * 90

    def test_returns_multiple_of_90(self):
        assert xcf_file_size_bytes_times_ninety(_XCF / "1x1-red-rgb.xcf") % 90 == 0

    def test_consistent(self):
        path = _XCF / "1x1-rgba-blue.xcf"
        assert xcf_file_size_bytes_times_ninety(path) == xcf_file_size_bytes_times_ninety(path)


class TestXcfImageTypeIdTimesNinety:
    def test_1x1_red_rgb(self):
        result = xcf_image_type_id_times_ninety(_XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, int) and result >= 0

    def test_1x1_rgba_blue(self):
        result = xcf_image_type_id_times_ninety(_XCF / "1x1-rgba-blue.xcf")
        assert isinstance(result, int) and result >= 0

    def test_multiplier_factor(self):
        from src.python.xcf import xcf_image_type_id
        path = _XCF / "1x1-red-rgb.xcf"
        assert xcf_image_type_id_times_ninety(path) == xcf_image_type_id(path) * 90

    def test_returns_multiple_of_90(self):
        assert xcf_image_type_id_times_ninety(_XCF / "1x1-red-rgb.xcf") % 90 == 0

    def test_consistent(self):
        path = _XCF / "1x1-rgba-blue.xcf"
        assert xcf_image_type_id_times_ninety(path) == xcf_image_type_id_times_ninety(path)

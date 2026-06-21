"""Sprint 262 deepening: XCF ninety-seven multiplier analytics."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"

from src.python.xcf import (
    xcf_file_size_bytes_times_ninety_seven,
    xcf_image_type_id_times_ninety_seven,
)


class TestXcfFileSizeBytesTimesNinetySeven:
    def test_red_rgb(self):
        result = xcf_file_size_bytes_times_ninety_seven(_XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, int) and result >= 97

    def test_rgba_blue(self):
        result = xcf_file_size_bytes_times_ninety_seven(_XCF / "1x1-rgba-blue.xcf")
        assert isinstance(result, int) and result >= 97

    def test_multiplier_factor(self):
        from src.python.xcf import xcf_file_size_bytes
        path = _XCF / "1x1-red-rgb.xcf"
        assert xcf_file_size_bytes_times_ninety_seven(path) == xcf_file_size_bytes(path) * 97

    def test_returns_multiple_of_97(self):
        assert xcf_file_size_bytes_times_ninety_seven(_XCF / "1x1-red-rgb.xcf") % 97 == 0

    def test_rgba_multiple_of_97(self):
        assert xcf_file_size_bytes_times_ninety_seven(_XCF / "1x1-rgba-blue.xcf") % 97 == 0


class TestXcfImageTypeIdTimesNinetySeven:
    def test_red_rgb(self):
        result = xcf_image_type_id_times_ninety_seven(_XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, int) and result >= 0

    def test_rgba_blue(self):
        result = xcf_image_type_id_times_ninety_seven(_XCF / "1x1-rgba-blue.xcf")
        assert isinstance(result, int) and result >= 0

    def test_multiplier_factor(self):
        from src.python.xcf import xcf_image_type_id
        path = _XCF / "1x1-red-rgb.xcf"
        assert xcf_image_type_id_times_ninety_seven(path) == xcf_image_type_id(path) * 97

    def test_returns_multiple_of_97(self):
        assert xcf_image_type_id_times_ninety_seven(_XCF / "1x1-red-rgb.xcf") % 97 == 0

    def test_rgba_multiple_of_97(self):
        assert xcf_image_type_id_times_ninety_seven(_XCF / "1x1-rgba-blue.xcf") % 97 == 0

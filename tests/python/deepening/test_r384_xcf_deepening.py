"""Sprint 256 deepening: XCF ninety-three multiplier analytics."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"

from src.python.xcf import (
    xcf_file_size_bytes_times_ninety_three,
    xcf_image_type_id_times_ninety_three,
)


class TestXcfFileSizeBytesTimesNinetyThree:
    def test_red_rgb(self):
        result = xcf_file_size_bytes_times_ninety_three(_XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, int) and result >= 93

    def test_rgba_blue(self):
        result = xcf_file_size_bytes_times_ninety_three(_XCF / "1x1-rgba-blue.xcf")
        assert isinstance(result, int) and result >= 93

    def test_multiplier_factor(self):
        from src.python.xcf import xcf_file_size_bytes
        path = _XCF / "1x1-red-rgb.xcf"
        assert xcf_file_size_bytes_times_ninety_three(path) == xcf_file_size_bytes(path) * 93

    def test_returns_multiple_of_93(self):
        assert xcf_file_size_bytes_times_ninety_three(_XCF / "1x1-red-rgb.xcf") % 93 == 0

    def test_rgba_multiple_of_93(self):
        assert xcf_file_size_bytes_times_ninety_three(_XCF / "1x1-rgba-blue.xcf") % 93 == 0


class TestXcfImageTypeIdTimesNinetyThree:
    def test_red_rgb(self):
        result = xcf_image_type_id_times_ninety_three(_XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, int) and result >= 0

    def test_rgba_blue(self):
        result = xcf_image_type_id_times_ninety_three(_XCF / "1x1-rgba-blue.xcf")
        assert isinstance(result, int) and result >= 0

    def test_multiplier_factor(self):
        from src.python.xcf import xcf_image_type_id
        path = _XCF / "1x1-red-rgb.xcf"
        assert xcf_image_type_id_times_ninety_three(path) == xcf_image_type_id(path) * 93

    def test_returns_multiple_of_93(self):
        assert xcf_image_type_id_times_ninety_three(_XCF / "1x1-red-rgb.xcf") % 93 == 0

    def test_rgba_multiple_of_93(self):
        assert xcf_image_type_id_times_ninety_three(_XCF / "1x1-rgba-blue.xcf") % 93 == 0

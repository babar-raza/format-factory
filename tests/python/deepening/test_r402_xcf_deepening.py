"""Sprint 274 deepening: XCF one-hundred-and-three multiplier analytics."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"

from src.python.xcf import (
    xcf_file_size_bytes_times_one_hundred_and_three,
    xcf_image_type_id_times_one_hundred_and_three,
)


class TestXcfFileSizeBytesTimesOneHundredAndThree:
    def test_red_rgb(self):
        result = xcf_file_size_bytes_times_one_hundred_and_three(_XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, int) and result >= 103

    def test_rgba_blue(self):
        result = xcf_file_size_bytes_times_one_hundred_and_three(_XCF / "1x1-rgba-blue.xcf")
        assert isinstance(result, int) and result >= 103

    def test_multiplier_factor(self):
        from src.python.xcf import xcf_file_size_bytes
        path = _XCF / "1x1-red-rgb.xcf"
        assert xcf_file_size_bytes_times_one_hundred_and_three(path) == xcf_file_size_bytes(path) * 103

    def test_returns_multiple_of_103(self):
        assert xcf_file_size_bytes_times_one_hundred_and_three(_XCF / "1x1-red-rgb.xcf") % 103 == 0

    def test_rgba_multiple_of_103(self):
        assert xcf_file_size_bytes_times_one_hundred_and_three(_XCF / "1x1-rgba-blue.xcf") % 103 == 0


class TestXcfImageTypeIdTimesOneHundredAndThree:
    def test_red_rgb(self):
        result = xcf_image_type_id_times_one_hundred_and_three(_XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, int) and result >= 0

    def test_rgba_blue(self):
        result = xcf_image_type_id_times_one_hundred_and_three(_XCF / "1x1-rgba-blue.xcf")
        assert isinstance(result, int) and result >= 0

    def test_multiplier_factor(self):
        from src.python.xcf import xcf_image_type_id
        path = _XCF / "1x1-red-rgb.xcf"
        assert xcf_image_type_id_times_one_hundred_and_three(path) == xcf_image_type_id(path) * 103

    def test_returns_multiple_of_103(self):
        assert xcf_image_type_id_times_one_hundred_and_three(_XCF / "1x1-red-rgb.xcf") % 103 == 0

    def test_rgba_multiple_of_103(self):
        assert xcf_image_type_id_times_one_hundred_and_three(_XCF / "1x1-rgba-blue.xcf") % 103 == 0

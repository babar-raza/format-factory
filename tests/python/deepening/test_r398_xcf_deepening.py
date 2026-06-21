"""Sprint 270 deepening: XCF one-hundred-and-one multiplier analytics."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"

from src.python.xcf import (
    xcf_file_size_bytes_times_one_hundred_and_one,
    xcf_image_type_id_times_one_hundred_and_one,
)


class TestXcfFileSizeBytesTimesOneHundredAndOne:
    def test_red_rgb(self):
        result = xcf_file_size_bytes_times_one_hundred_and_one(_XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, int) and result >= 101

    def test_rgba_blue(self):
        result = xcf_file_size_bytes_times_one_hundred_and_one(_XCF / "1x1-rgba-blue.xcf")
        assert isinstance(result, int) and result >= 101

    def test_multiplier_factor(self):
        from src.python.xcf import xcf_file_size_bytes
        path = _XCF / "1x1-red-rgb.xcf"
        assert xcf_file_size_bytes_times_one_hundred_and_one(path) == xcf_file_size_bytes(path) * 101

    def test_returns_multiple_of_101(self):
        assert xcf_file_size_bytes_times_one_hundred_and_one(_XCF / "1x1-red-rgb.xcf") % 101 == 0

    def test_rgba_multiple_of_101(self):
        assert xcf_file_size_bytes_times_one_hundred_and_one(_XCF / "1x1-rgba-blue.xcf") % 101 == 0


class TestXcfImageTypeIdTimesOneHundredAndOne:
    def test_red_rgb(self):
        result = xcf_image_type_id_times_one_hundred_and_one(_XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, int) and result >= 0

    def test_rgba_blue(self):
        result = xcf_image_type_id_times_one_hundred_and_one(_XCF / "1x1-rgba-blue.xcf")
        assert isinstance(result, int) and result >= 0

    def test_multiplier_factor(self):
        from src.python.xcf import xcf_image_type_id
        path = _XCF / "1x1-red-rgb.xcf"
        assert xcf_image_type_id_times_one_hundred_and_one(path) == xcf_image_type_id(path) * 101

    def test_returns_multiple_of_101(self):
        assert xcf_image_type_id_times_one_hundred_and_one(_XCF / "1x1-red-rgb.xcf") % 101 == 0

    def test_rgba_multiple_of_101(self):
        assert xcf_image_type_id_times_one_hundred_and_one(_XCF / "1x1-rgba-blue.xcf") % 101 == 0

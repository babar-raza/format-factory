"""Sprint 248 deepening: XCF eighty-nine multiplier analytics."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"

from src.python.xcf import (
    xcf_file_size_bytes_times_eighty_nine,
    xcf_image_type_id_times_eighty_nine,
)


class TestXcfFileSizeBytesTimesEightyNine:
    def test_1x1_red_rgb(self):
        result = xcf_file_size_bytes_times_eighty_nine(_XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, int)
        assert result > 0

    def test_1x1_rgba_blue(self):
        result = xcf_file_size_bytes_times_eighty_nine(_XCF / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
        assert result > 0

    def test_multiplier_factor(self):
        from src.python.xcf import xcf_file_size_bytes
        path = _XCF / "1x1-red-rgb.xcf"
        base = xcf_file_size_bytes(path)
        assert xcf_file_size_bytes_times_eighty_nine(path) == base * 89

    def test_returns_multiple_of_89(self):
        result = xcf_file_size_bytes_times_eighty_nine(_XCF / "1x1-red-rgb.xcf")
        assert result % 89 == 0

    def test_positive_value(self):
        result = xcf_file_size_bytes_times_eighty_nine(_XCF / "1x1-rgba-blue.xcf")
        assert result >= 89  # at least 1 byte * 89


class TestXcfImageTypeIdTimesEightyNine:
    def test_1x1_red_rgb(self):
        result = xcf_image_type_id_times_eighty_nine(_XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, int)
        assert result >= 0

    def test_1x1_rgba_blue(self):
        result = xcf_image_type_id_times_eighty_nine(_XCF / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
        assert result >= 0

    def test_multiplier_factor(self):
        from src.python.xcf import xcf_image_type_id
        path = _XCF / "1x1-red-rgb.xcf"
        base = xcf_image_type_id(path)
        assert xcf_image_type_id_times_eighty_nine(path) == base * 89

    def test_returns_multiple_of_89(self):
        result = xcf_image_type_id_times_eighty_nine(_XCF / "1x1-red-rgb.xcf")
        assert result % 89 == 0

    def test_consistent_across_calls(self):
        path = _XCF / "1x1-rgba-blue.xcf"
        assert xcf_image_type_id_times_eighty_nine(path) == xcf_image_type_id_times_eighty_nine(path)

"""Sprint R492 — XCF/ZST/TOML/FODG/Gnumeric _times_eleven composite analytics tests."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_eleven, xcf_image_type_id_times_eleven
from src.python.zst.zst_codec import zst_file_size_bytes_times_eleven, zst_decompressed_size_times_eleven
from src.python.toml.toml_codec import toml_file_size_bytes_times_eleven, toml_string_value_count_times_eleven
from src.python.fodg.fodg_codec import fodg_page_count_times_eleven, fodg_total_shape_count_times_eleven
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_eleven, gnumeric_total_row_count_times_eleven

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")


class TestXcfFileSizeBytesTimesEleven:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_eleven(_XCF), int)

    def test_non_negative(self):
        assert xcf_file_size_bytes_times_eleven(_XCF) >= 0

    def test_divisible(self):
        assert xcf_file_size_bytes_times_eleven(_XCF) % 11 == 0


class TestXcfImageTypeIdTimesEleven:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_eleven(_XCF), int)

    def test_non_negative(self):
        assert xcf_image_type_id_times_eleven(_XCF) >= 0

    def test_divisible(self):
        assert xcf_image_type_id_times_eleven(_XCF) % 11 == 0


class TestZstFileSizeBytesTimesEleven:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_eleven(_ZST), int)

    def test_non_negative(self):
        assert zst_file_size_bytes_times_eleven(_ZST) >= 0

    def test_divisible(self):
        assert zst_file_size_bytes_times_eleven(_ZST) % 11 == 0


class TestZstDecompressedSizeTimesEleven:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_eleven(_ZST), int)

    def test_non_negative(self):
        assert zst_decompressed_size_times_eleven(_ZST) >= 0

    def test_divisible(self):
        assert zst_decompressed_size_times_eleven(_ZST) % 11 == 0


class TestTomlFileSizeBytesTimesEleven:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_eleven(_TOML), int)

    def test_non_negative(self):
        assert toml_file_size_bytes_times_eleven(_TOML) >= 0

    def test_divisible(self):
        assert toml_file_size_bytes_times_eleven(_TOML) % 11 == 0


class TestTomlStringValueCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_eleven(_TOML), int)

    def test_non_negative(self):
        assert toml_string_value_count_times_eleven(_TOML) >= 0

    def test_divisible(self):
        assert toml_string_value_count_times_eleven(_TOML) % 11 == 0


class TestFodgPageCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_eleven(_FODG), int)

    def test_non_negative(self):
        assert fodg_page_count_times_eleven(_FODG) >= 0

    def test_divisible(self):
        assert fodg_page_count_times_eleven(_FODG) % 11 == 0


class TestFodgTotalShapeCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_eleven(_FODG), int)

    def test_non_negative(self):
        assert fodg_total_shape_count_times_eleven(_FODG) >= 0

    def test_divisible(self):
        assert fodg_total_shape_count_times_eleven(_FODG) % 11 == 0


class TestGnumericFileSizeBytesTimesEleven:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_eleven(_GNUMERIC), int)

    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_eleven(_GNUMERIC) >= 0

    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_eleven(_GNUMERIC) % 11 == 0


class TestGnumericTotalRowCountTimesEleven:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_eleven(_GNUMERIC), int)

    def test_non_negative(self):
        assert gnumeric_total_row_count_times_eleven(_GNUMERIC) >= 0

    def test_divisible(self):
        assert gnumeric_total_row_count_times_eleven(_GNUMERIC) % 11 == 0

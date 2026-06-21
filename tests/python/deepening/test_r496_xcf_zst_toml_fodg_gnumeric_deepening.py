"""Sprint R496 — XCF/ZST/TOML/FODG/Gnumeric _times_twelve composite analytics tests."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_twelve, xcf_image_type_id_times_twelve
from src.python.zst.zst_codec import zst_file_size_bytes_times_twelve, zst_decompressed_size_times_twelve
from src.python.toml.toml_codec import toml_file_size_bytes_times_twelve, toml_string_value_count_times_twelve
from src.python.fodg.fodg_codec import fodg_page_count_times_twelve, fodg_total_shape_count_times_twelve
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_twelve, gnumeric_total_row_count_times_twelve

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")


class TestXcfFileSizeBytesTimesTwelve:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_twelve(_XCF), int)

    def test_non_negative(self):
        assert xcf_file_size_bytes_times_twelve(_XCF) >= 0

    def test_divisible(self):
        assert xcf_file_size_bytes_times_twelve(_XCF) % 12 == 0


class TestXcfImageTypeIdTimesTwelve:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_twelve(_XCF), int)

    def test_non_negative(self):
        assert xcf_image_type_id_times_twelve(_XCF) >= 0

    def test_divisible(self):
        assert xcf_image_type_id_times_twelve(_XCF) % 12 == 0


class TestZstFileSizeBytesTimesTwelve:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_twelve(_ZST), int)

    def test_non_negative(self):
        assert zst_file_size_bytes_times_twelve(_ZST) >= 0

    def test_divisible(self):
        assert zst_file_size_bytes_times_twelve(_ZST) % 12 == 0


class TestZstDecompressedSizeTimesTwelve:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_twelve(_ZST), int)

    def test_non_negative(self):
        assert zst_decompressed_size_times_twelve(_ZST) >= 0

    def test_divisible(self):
        assert zst_decompressed_size_times_twelve(_ZST) % 12 == 0


class TestTomlFileSizeBytesTimesTwelve:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_twelve(_TOML), int)

    def test_non_negative(self):
        assert toml_file_size_bytes_times_twelve(_TOML) >= 0

    def test_divisible(self):
        assert toml_file_size_bytes_times_twelve(_TOML) % 12 == 0


class TestTomlStringValueCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_twelve(_TOML), int)

    def test_non_negative(self):
        assert toml_string_value_count_times_twelve(_TOML) >= 0

    def test_divisible(self):
        assert toml_string_value_count_times_twelve(_TOML) % 12 == 0


class TestFodgPageCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_twelve(_FODG), int)

    def test_non_negative(self):
        assert fodg_page_count_times_twelve(_FODG) >= 0

    def test_divisible(self):
        assert fodg_page_count_times_twelve(_FODG) % 12 == 0


class TestFodgTotalShapeCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_twelve(_FODG), int)

    def test_non_negative(self):
        assert fodg_total_shape_count_times_twelve(_FODG) >= 0

    def test_divisible(self):
        assert fodg_total_shape_count_times_twelve(_FODG) % 12 == 0


class TestGnumericFileSizeBytesTimesTwelve:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_twelve(_GNUMERIC), int)

    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_twelve(_GNUMERIC) >= 0

    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_twelve(_GNUMERIC) % 12 == 0


class TestGnumericTotalRowCountTimesTwelve:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_twelve(_GNUMERIC), int)

    def test_non_negative(self):
        assert gnumeric_total_row_count_times_twelve(_GNUMERIC) >= 0

    def test_divisible(self):
        assert gnumeric_total_row_count_times_twelve(_GNUMERIC) % 12 == 0

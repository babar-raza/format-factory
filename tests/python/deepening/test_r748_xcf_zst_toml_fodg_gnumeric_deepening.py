"""Sprint R748 — XCF/ZST/TOML/FODG/Gnumeric _times_seventy_five composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_seventy_five, xcf_image_type_id_times_seventy_five
from src.python.zst.zst_codec import zst_file_size_bytes_times_seventy_five, zst_decompressed_size_times_seventy_five
from src.python.toml.toml_codec import toml_file_size_bytes_times_seventy_five, toml_string_value_count_times_seventy_five
from src.python.fodg.fodg_codec import fodg_page_count_times_seventy_five, fodg_total_shape_count_times_seventy_five
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_seventy_five, gnumeric_total_row_count_times_seventy_five
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_seventy_five(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_seventy_five(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_seventy_five(_XCF) % 75 == 0
class TestXcfImageTypeIdTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_seventy_five(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_seventy_five(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_seventy_five(_XCF) % 75 == 0
class TestZstFileSizeBytesTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_seventy_five(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_seventy_five(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_seventy_five(_ZST) % 75 == 0
class TestZstDecompressedSizeTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_seventy_five(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_seventy_five(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_seventy_five(_ZST) % 75 == 0
class TestTomlFileSizeBytesTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_seventy_five(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_seventy_five(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_seventy_five(_TOML) % 75 == 0
class TestTomlStringValueCountTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_seventy_five(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_seventy_five(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_seventy_five(_TOML) % 75 == 0
class TestFodgPageCountTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_seventy_five(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_seventy_five(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_seventy_five(_FODG) % 75 == 0
class TestFodgTotalShapeCountTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_seventy_five(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_seventy_five(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_seventy_five(_FODG) % 75 == 0
class TestGnumericFileSizeBytesTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_seventy_five(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_seventy_five(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_seventy_five(_GNUMERIC) % 75 == 0
class TestGnumericTotalRowCountTimesSeventyFive:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_seventy_five(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_seventy_five(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_seventy_five(_GNUMERIC) % 75 == 0

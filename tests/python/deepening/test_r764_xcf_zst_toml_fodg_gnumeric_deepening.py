"""Sprint R764 — XCF/ZST/TOML/FODG/Gnumeric _times_seventy_nine composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_seventy_nine, xcf_image_type_id_times_seventy_nine
from src.python.zst.zst_codec import zst_file_size_bytes_times_seventy_nine, zst_decompressed_size_times_seventy_nine
from src.python.toml.toml_codec import toml_file_size_bytes_times_seventy_nine, toml_string_value_count_times_seventy_nine
from src.python.fodg.fodg_codec import fodg_page_count_times_seventy_nine, fodg_total_shape_count_times_seventy_nine
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_seventy_nine, gnumeric_total_row_count_times_seventy_nine
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesSeventyNine:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_seventy_nine(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_seventy_nine(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_seventy_nine(_XCF) % 79 == 0
class TestXcfImageTypeIdTimesSeventyNine:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_seventy_nine(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_seventy_nine(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_seventy_nine(_XCF) % 79 == 0
class TestZstFileSizeBytesTimesSeventyNine:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_seventy_nine(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_seventy_nine(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_seventy_nine(_ZST) % 79 == 0
class TestZstDecompressedSizeTimesSeventyNine:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_seventy_nine(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_seventy_nine(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_seventy_nine(_ZST) % 79 == 0
class TestTomlFileSizeBytesTimesSeventyNine:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_seventy_nine(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_seventy_nine(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_seventy_nine(_TOML) % 79 == 0
class TestTomlStringValueCountTimesSeventyNine:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_seventy_nine(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_seventy_nine(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_seventy_nine(_TOML) % 79 == 0
class TestFodgPageCountTimesSeventyNine:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_seventy_nine(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_seventy_nine(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_seventy_nine(_FODG) % 79 == 0
class TestFodgTotalShapeCountTimesSeventyNine:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_seventy_nine(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_seventy_nine(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_seventy_nine(_FODG) % 79 == 0
class TestGnumericFileSizeBytesTimesSeventyNine:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_seventy_nine(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_seventy_nine(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_seventy_nine(_GNUMERIC) % 79 == 0
class TestGnumericTotalRowCountTimesSeventyNine:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_seventy_nine(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_seventy_nine(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_seventy_nine(_GNUMERIC) % 79 == 0

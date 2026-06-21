"""Sprint R756 — XCF/ZST/TOML/FODG/Gnumeric _times_seventy_seven composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_seventy_seven, xcf_image_type_id_times_seventy_seven
from src.python.zst.zst_codec import zst_file_size_bytes_times_seventy_seven, zst_decompressed_size_times_seventy_seven
from src.python.toml.toml_codec import toml_file_size_bytes_times_seventy_seven, toml_string_value_count_times_seventy_seven
from src.python.fodg.fodg_codec import fodg_page_count_times_seventy_seven, fodg_total_shape_count_times_seventy_seven
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_seventy_seven, gnumeric_total_row_count_times_seventy_seven
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_seventy_seven(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_seventy_seven(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_seventy_seven(_XCF) % 77 == 0
class TestXcfImageTypeIdTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_seventy_seven(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_seventy_seven(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_seventy_seven(_XCF) % 77 == 0
class TestZstFileSizeBytesTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_seventy_seven(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_seventy_seven(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_seventy_seven(_ZST) % 77 == 0
class TestZstDecompressedSizeTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_seventy_seven(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_seventy_seven(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_seventy_seven(_ZST) % 77 == 0
class TestTomlFileSizeBytesTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_seventy_seven(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_seventy_seven(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_seventy_seven(_TOML) % 77 == 0
class TestTomlStringValueCountTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_seventy_seven(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_seventy_seven(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_seventy_seven(_TOML) % 77 == 0
class TestFodgPageCountTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_seventy_seven(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_seventy_seven(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_seventy_seven(_FODG) % 77 == 0
class TestFodgTotalShapeCountTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_seventy_seven(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_seventy_seven(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_seventy_seven(_FODG) % 77 == 0
class TestGnumericFileSizeBytesTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_seventy_seven(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_seventy_seven(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_seventy_seven(_GNUMERIC) % 77 == 0
class TestGnumericTotalRowCountTimesSeventySeven:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_seventy_seven(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_seventy_seven(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_seventy_seven(_GNUMERIC) % 77 == 0

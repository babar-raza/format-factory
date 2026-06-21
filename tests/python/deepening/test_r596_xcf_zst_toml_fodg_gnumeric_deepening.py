"""Sprint R596 — XCF/ZST/TOML/FODG/Gnumeric _times_thirty_seven composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_thirty_seven, xcf_image_type_id_times_thirty_seven
from src.python.zst.zst_codec import zst_file_size_bytes_times_thirty_seven, zst_decompressed_size_times_thirty_seven
from src.python.toml.toml_codec import toml_file_size_bytes_times_thirty_seven, toml_string_value_count_times_thirty_seven
from src.python.fodg.fodg_codec import fodg_page_count_times_thirty_seven, fodg_total_shape_count_times_thirty_seven
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_thirty_seven, gnumeric_total_row_count_times_thirty_seven
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_thirty_seven(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_thirty_seven(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_thirty_seven(_XCF) % 37 == 0
class TestXcfImageTypeIdTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_thirty_seven(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_thirty_seven(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_thirty_seven(_XCF) % 37 == 0
class TestZstFileSizeBytesTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_thirty_seven(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_thirty_seven(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_thirty_seven(_ZST) % 37 == 0
class TestZstDecompressedSizeTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_thirty_seven(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_thirty_seven(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_thirty_seven(_ZST) % 37 == 0
class TestTomlFileSizeBytesTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_thirty_seven(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_thirty_seven(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_thirty_seven(_TOML) % 37 == 0
class TestTomlStringValueCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_thirty_seven(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_thirty_seven(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_thirty_seven(_TOML) % 37 == 0
class TestFodgPageCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_thirty_seven(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_thirty_seven(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_thirty_seven(_FODG) % 37 == 0
class TestFodgTotalShapeCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_thirty_seven(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_thirty_seven(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_thirty_seven(_FODG) % 37 == 0
class TestGnumericFileSizeBytesTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_thirty_seven(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_thirty_seven(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_thirty_seven(_GNUMERIC) % 37 == 0
class TestGnumericTotalRowCountTimesThirtySeven:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_thirty_seven(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_thirty_seven(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_thirty_seven(_GNUMERIC) % 37 == 0

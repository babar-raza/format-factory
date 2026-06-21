"""Sprint R584 — XCF/ZST/TOML/FODG/Gnumeric _times_thirty_four composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_thirty_four, xcf_image_type_id_times_thirty_four
from src.python.zst.zst_codec import zst_file_size_bytes_times_thirty_four, zst_decompressed_size_times_thirty_four
from src.python.toml.toml_codec import toml_file_size_bytes_times_thirty_four, toml_string_value_count_times_thirty_four
from src.python.fodg.fodg_codec import fodg_page_count_times_thirty_four, fodg_total_shape_count_times_thirty_four
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_thirty_four, gnumeric_total_row_count_times_thirty_four
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesThirtyFour:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_thirty_four(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_thirty_four(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_thirty_four(_XCF) % 34 == 0
class TestXcfImageTypeIdTimesThirtyFour:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_thirty_four(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_thirty_four(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_thirty_four(_XCF) % 34 == 0
class TestZstFileSizeBytesTimesThirtyFour:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_thirty_four(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_thirty_four(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_thirty_four(_ZST) % 34 == 0
class TestZstDecompressedSizeTimesThirtyFour:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_thirty_four(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_thirty_four(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_thirty_four(_ZST) % 34 == 0
class TestTomlFileSizeBytesTimesThirtyFour:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_thirty_four(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_thirty_four(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_thirty_four(_TOML) % 34 == 0
class TestTomlStringValueCountTimesThirtyFour:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_thirty_four(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_thirty_four(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_thirty_four(_TOML) % 34 == 0
class TestFodgPageCountTimesThirtyFour:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_thirty_four(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_thirty_four(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_thirty_four(_FODG) % 34 == 0
class TestFodgTotalShapeCountTimesThirtyFour:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_thirty_four(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_thirty_four(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_thirty_four(_FODG) % 34 == 0
class TestGnumericFileSizeBytesTimesThirtyFour:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_thirty_four(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_thirty_four(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_thirty_four(_GNUMERIC) % 34 == 0
class TestGnumericTotalRowCountTimesThirtyFour:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_thirty_four(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_thirty_four(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_thirty_four(_GNUMERIC) % 34 == 0

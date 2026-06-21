"""Sprint R636 — XCF/ZST/TOML/FODG/Gnumeric _times_forty_seven composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_forty_seven, xcf_image_type_id_times_forty_seven
from src.python.zst.zst_codec import zst_file_size_bytes_times_forty_seven, zst_decompressed_size_times_forty_seven
from src.python.toml.toml_codec import toml_file_size_bytes_times_forty_seven, toml_string_value_count_times_forty_seven
from src.python.fodg.fodg_codec import fodg_page_count_times_forty_seven, fodg_total_shape_count_times_forty_seven
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_forty_seven, gnumeric_total_row_count_times_forty_seven
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_forty_seven(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_forty_seven(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_forty_seven(_XCF) % 47 == 0
class TestXcfImageTypeIdTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_forty_seven(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_forty_seven(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_forty_seven(_XCF) % 47 == 0
class TestZstFileSizeBytesTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_forty_seven(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_forty_seven(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_forty_seven(_ZST) % 47 == 0
class TestZstDecompressedSizeTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_forty_seven(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_forty_seven(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_forty_seven(_ZST) % 47 == 0
class TestTomlFileSizeBytesTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_forty_seven(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_forty_seven(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_forty_seven(_TOML) % 47 == 0
class TestTomlStringValueCountTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_forty_seven(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_forty_seven(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_forty_seven(_TOML) % 47 == 0
class TestFodgPageCountTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_forty_seven(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_forty_seven(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_forty_seven(_FODG) % 47 == 0
class TestFodgTotalShapeCountTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_forty_seven(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_forty_seven(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_forty_seven(_FODG) % 47 == 0
class TestGnumericFileSizeBytesTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_forty_seven(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_forty_seven(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_forty_seven(_GNUMERIC) % 47 == 0
class TestGnumericTotalRowCountTimesForty_Seven:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_forty_seven(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_forty_seven(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_forty_seven(_GNUMERIC) % 47 == 0

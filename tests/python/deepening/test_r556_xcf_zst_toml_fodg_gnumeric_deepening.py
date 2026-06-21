"""Sprint R556 — XCF/ZST/TOML/FODG/Gnumeric _times_twenty_seven composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_twenty_seven, xcf_image_type_id_times_twenty_seven
from src.python.zst.zst_codec import zst_file_size_bytes_times_twenty_seven, zst_decompressed_size_times_twenty_seven
from src.python.toml.toml_codec import toml_file_size_bytes_times_twenty_seven, toml_string_value_count_times_twenty_seven
from src.python.fodg.fodg_codec import fodg_page_count_times_twenty_seven, fodg_total_shape_count_times_twenty_seven
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_twenty_seven, gnumeric_total_row_count_times_twenty_seven
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesTwentySeven:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_twenty_seven(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_twenty_seven(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_twenty_seven(_XCF) % 27 == 0
class TestXcfImageTypeIdTimesTwentySeven:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_twenty_seven(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_twenty_seven(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_twenty_seven(_XCF) % 27 == 0
class TestZstFileSizeBytesTimesTwentySeven:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_twenty_seven(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_twenty_seven(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_twenty_seven(_ZST) % 27 == 0
class TestZstDecompressedSizeTimesTwentySeven:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_twenty_seven(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_twenty_seven(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_twenty_seven(_ZST) % 27 == 0
class TestTomlFileSizeBytesTimesTwentySeven:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_twenty_seven(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_twenty_seven(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_twenty_seven(_TOML) % 27 == 0
class TestTomlStringValueCountTimesTwentySeven:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_twenty_seven(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_twenty_seven(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_twenty_seven(_TOML) % 27 == 0
class TestFodgPageCountTimesTwentySeven:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_twenty_seven(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_twenty_seven(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_twenty_seven(_FODG) % 27 == 0
class TestFodgTotalShapeCountTimesTwentySeven:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_twenty_seven(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_twenty_seven(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_twenty_seven(_FODG) % 27 == 0
class TestGnumericFileSizeBytesTimesTwentySeven:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_twenty_seven(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_twenty_seven(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_twenty_seven(_GNUMERIC) % 27 == 0
class TestGnumericTotalRowCountTimesTwentySeven:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_twenty_seven(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_twenty_seven(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_twenty_seven(_GNUMERIC) % 27 == 0

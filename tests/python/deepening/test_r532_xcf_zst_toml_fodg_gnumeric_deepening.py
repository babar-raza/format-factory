"""Sprint R532 — XCF/ZST/TOML/FODG/Gnumeric _times_twenty_one composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_twenty_one, xcf_image_type_id_times_twenty_one
from src.python.zst.zst_codec import zst_file_size_bytes_times_twenty_one, zst_decompressed_size_times_twenty_one
from src.python.toml.toml_codec import toml_file_size_bytes_times_twenty_one, toml_string_value_count_times_twenty_one
from src.python.fodg.fodg_codec import fodg_page_count_times_twenty_one, fodg_total_shape_count_times_twenty_one
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_twenty_one, gnumeric_total_row_count_times_twenty_one
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_twenty_one(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_twenty_one(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_twenty_one(_XCF) % 21 == 0
class TestXcfImageTypeIdTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_twenty_one(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_twenty_one(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_twenty_one(_XCF) % 21 == 0
class TestZstFileSizeBytesTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_twenty_one(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_twenty_one(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_twenty_one(_ZST) % 21 == 0
class TestZstDecompressedSizeTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_twenty_one(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_twenty_one(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_twenty_one(_ZST) % 21 == 0
class TestTomlFileSizeBytesTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_twenty_one(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_twenty_one(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_twenty_one(_TOML) % 21 == 0
class TestTomlStringValueCountTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_twenty_one(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_twenty_one(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_twenty_one(_TOML) % 21 == 0
class TestFodgPageCountTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_twenty_one(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_twenty_one(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_twenty_one(_FODG) % 21 == 0
class TestFodgTotalShapeCountTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_twenty_one(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_twenty_one(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_twenty_one(_FODG) % 21 == 0
class TestGnumericFileSizeBytesTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_twenty_one(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_twenty_one(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_twenty_one(_GNUMERIC) % 21 == 0
class TestGnumericTotalRowCountTimesTwentyOne:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_twenty_one(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_twenty_one(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_twenty_one(_GNUMERIC) % 21 == 0

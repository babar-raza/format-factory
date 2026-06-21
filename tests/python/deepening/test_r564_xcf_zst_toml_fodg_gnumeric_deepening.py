"""Sprint R564 — XCF/ZST/TOML/FODG/Gnumeric _times_twenty_nine composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_twenty_nine, xcf_image_type_id_times_twenty_nine
from src.python.zst.zst_codec import zst_file_size_bytes_times_twenty_nine, zst_decompressed_size_times_twenty_nine
from src.python.toml.toml_codec import toml_file_size_bytes_times_twenty_nine, toml_string_value_count_times_twenty_nine
from src.python.fodg.fodg_codec import fodg_page_count_times_twenty_nine, fodg_total_shape_count_times_twenty_nine
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_twenty_nine, gnumeric_total_row_count_times_twenty_nine
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesTwentyNine:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_twenty_nine(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_twenty_nine(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_twenty_nine(_XCF) % 29 == 0
class TestXcfImageTypeIdTimesTwentyNine:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_twenty_nine(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_twenty_nine(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_twenty_nine(_XCF) % 29 == 0
class TestZstFileSizeBytesTimesTwentyNine:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_twenty_nine(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_twenty_nine(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_twenty_nine(_ZST) % 29 == 0
class TestZstDecompressedSizeTimesTwentyNine:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_twenty_nine(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_twenty_nine(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_twenty_nine(_ZST) % 29 == 0
class TestTomlFileSizeBytesTimesTwentyNine:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_twenty_nine(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_twenty_nine(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_twenty_nine(_TOML) % 29 == 0
class TestTomlStringValueCountTimesTwentyNine:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_twenty_nine(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_twenty_nine(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_twenty_nine(_TOML) % 29 == 0
class TestFodgPageCountTimesTwentyNine:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_twenty_nine(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_twenty_nine(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_twenty_nine(_FODG) % 29 == 0
class TestFodgTotalShapeCountTimesTwentyNine:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_twenty_nine(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_twenty_nine(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_twenty_nine(_FODG) % 29 == 0
class TestGnumericFileSizeBytesTimesTwentyNine:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_twenty_nine(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_twenty_nine(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_twenty_nine(_GNUMERIC) % 29 == 0
class TestGnumericTotalRowCountTimesTwentyNine:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_twenty_nine(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_twenty_nine(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_twenty_nine(_GNUMERIC) % 29 == 0

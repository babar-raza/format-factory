"""Sprint R768 — XCF/ZST/TOML/FODG/Gnumeric _times_eighty composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_eighty, xcf_image_type_id_times_eighty
from src.python.zst.zst_codec import zst_file_size_bytes_times_eighty, zst_decompressed_size_times_eighty
from src.python.toml.toml_codec import toml_file_size_bytes_times_eighty, toml_string_value_count_times_eighty
from src.python.fodg.fodg_codec import fodg_page_count_times_eighty, fodg_total_shape_count_times_eighty
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_eighty, gnumeric_total_row_count_times_eighty
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesEighty:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_eighty(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_eighty(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_eighty(_XCF) % 80 == 0
class TestXcfImageTypeIdTimesEighty:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_eighty(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_eighty(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_eighty(_XCF) % 80 == 0
class TestZstFileSizeBytesTimesEighty:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_eighty(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_eighty(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_eighty(_ZST) % 80 == 0
class TestZstDecompressedSizeTimesEighty:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_eighty(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_eighty(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_eighty(_ZST) % 80 == 0
class TestTomlFileSizeBytesTimesEighty:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_eighty(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_eighty(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_eighty(_TOML) % 80 == 0
class TestTomlStringValueCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_eighty(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_eighty(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_eighty(_TOML) % 80 == 0
class TestFodgPageCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_eighty(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_eighty(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_eighty(_FODG) % 80 == 0
class TestFodgTotalShapeCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_eighty(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_eighty(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_eighty(_FODG) % 80 == 0
class TestGnumericFileSizeBytesTimesEighty:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_eighty(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_eighty(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_eighty(_GNUMERIC) % 80 == 0
class TestGnumericTotalRowCountTimesEighty:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_eighty(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_eighty(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_eighty(_GNUMERIC) % 80 == 0

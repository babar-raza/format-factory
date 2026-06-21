"""Sprint R728 — XCF/ZST/TOML/FODG/Gnumeric _times_seventy composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_seventy, xcf_image_type_id_times_seventy
from src.python.zst.zst_codec import zst_file_size_bytes_times_seventy, zst_decompressed_size_times_seventy
from src.python.toml.toml_codec import toml_file_size_bytes_times_seventy, toml_string_value_count_times_seventy
from src.python.fodg.fodg_codec import fodg_page_count_times_seventy, fodg_total_shape_count_times_seventy
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_seventy, gnumeric_total_row_count_times_seventy
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesSeventy:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_seventy(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_seventy(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_seventy(_XCF) % 70 == 0
class TestXcfImageTypeIdTimesSeventy:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_seventy(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_seventy(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_seventy(_XCF) % 70 == 0
class TestZstFileSizeBytesTimesSeventy:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_seventy(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_seventy(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_seventy(_ZST) % 70 == 0
class TestZstDecompressedSizeTimesSeventy:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_seventy(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_seventy(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_seventy(_ZST) % 70 == 0
class TestTomlFileSizeBytesTimesSeventy:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_seventy(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_seventy(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_seventy(_TOML) % 70 == 0
class TestTomlStringValueCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_seventy(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_seventy(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_seventy(_TOML) % 70 == 0
class TestFodgPageCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_seventy(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_seventy(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_seventy(_FODG) % 70 == 0
class TestFodgTotalShapeCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_seventy(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_seventy(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_seventy(_FODG) % 70 == 0
class TestGnumericFileSizeBytesTimesSeventy:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_seventy(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_seventy(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_seventy(_GNUMERIC) % 70 == 0
class TestGnumericTotalRowCountTimesSeventy:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_seventy(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_seventy(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_seventy(_GNUMERIC) % 70 == 0

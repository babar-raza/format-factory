"""Sprint R608 — XCF/ZST/TOML/FODG/Gnumeric _times_forty composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_forty, xcf_image_type_id_times_forty
from src.python.zst.zst_codec import zst_file_size_bytes_times_forty, zst_decompressed_size_times_forty
from src.python.toml.toml_codec import toml_file_size_bytes_times_forty, toml_string_value_count_times_forty
from src.python.fodg.fodg_codec import fodg_page_count_times_forty, fodg_total_shape_count_times_forty
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_forty, gnumeric_total_row_count_times_forty
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesForty:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_forty(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_forty(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_forty(_XCF) % 40 == 0
class TestXcfImageTypeIdTimesForty:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_forty(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_forty(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_forty(_XCF) % 40 == 0
class TestZstFileSizeBytesTimesForty:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_forty(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_forty(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_forty(_ZST) % 40 == 0
class TestZstDecompressedSizeTimesForty:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_forty(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_forty(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_forty(_ZST) % 40 == 0
class TestTomlFileSizeBytesTimesForty:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_forty(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_forty(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_forty(_TOML) % 40 == 0
class TestTomlStringValueCountTimesForty:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_forty(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_forty(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_forty(_TOML) % 40 == 0
class TestFodgPageCountTimesForty:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_forty(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_forty(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_forty(_FODG) % 40 == 0
class TestFodgTotalShapeCountTimesForty:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_forty(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_forty(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_forty(_FODG) % 40 == 0
class TestGnumericFileSizeBytesTimesForty:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_forty(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_forty(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_forty(_GNUMERIC) % 40 == 0
class TestGnumericTotalRowCountTimesForty:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_forty(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_forty(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_forty(_GNUMERIC) % 40 == 0

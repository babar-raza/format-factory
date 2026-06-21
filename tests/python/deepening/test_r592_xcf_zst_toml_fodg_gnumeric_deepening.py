"""Sprint R592 — XCF/ZST/TOML/FODG/Gnumeric _times_thirty_six composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_thirty_six, xcf_image_type_id_times_thirty_six
from src.python.zst.zst_codec import zst_file_size_bytes_times_thirty_six, zst_decompressed_size_times_thirty_six
from src.python.toml.toml_codec import toml_file_size_bytes_times_thirty_six, toml_string_value_count_times_thirty_six
from src.python.fodg.fodg_codec import fodg_page_count_times_thirty_six, fodg_total_shape_count_times_thirty_six
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_thirty_six, gnumeric_total_row_count_times_thirty_six
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesThirtySix:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_thirty_six(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_thirty_six(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_thirty_six(_XCF) % 36 == 0
class TestXcfImageTypeIdTimesThirtySix:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_thirty_six(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_thirty_six(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_thirty_six(_XCF) % 36 == 0
class TestZstFileSizeBytesTimesThirtySix:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_thirty_six(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_thirty_six(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_thirty_six(_ZST) % 36 == 0
class TestZstDecompressedSizeTimesThirtySix:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_thirty_six(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_thirty_six(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_thirty_six(_ZST) % 36 == 0
class TestTomlFileSizeBytesTimesThirtySix:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_thirty_six(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_thirty_six(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_thirty_six(_TOML) % 36 == 0
class TestTomlStringValueCountTimesThirtySix:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_thirty_six(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_thirty_six(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_thirty_six(_TOML) % 36 == 0
class TestFodgPageCountTimesThirtySix:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_thirty_six(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_thirty_six(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_thirty_six(_FODG) % 36 == 0
class TestFodgTotalShapeCountTimesThirtySix:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_thirty_six(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_thirty_six(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_thirty_six(_FODG) % 36 == 0
class TestGnumericFileSizeBytesTimesThirtySix:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_thirty_six(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_thirty_six(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_thirty_six(_GNUMERIC) % 36 == 0
class TestGnumericTotalRowCountTimesThirtySix:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_thirty_six(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_thirty_six(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_thirty_six(_GNUMERIC) % 36 == 0

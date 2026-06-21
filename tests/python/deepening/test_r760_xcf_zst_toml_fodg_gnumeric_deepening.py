"""Sprint R760 — XCF/ZST/TOML/FODG/Gnumeric _times_seventy_eight composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_seventy_eight, xcf_image_type_id_times_seventy_eight
from src.python.zst.zst_codec import zst_file_size_bytes_times_seventy_eight, zst_decompressed_size_times_seventy_eight
from src.python.toml.toml_codec import toml_file_size_bytes_times_seventy_eight, toml_string_value_count_times_seventy_eight
from src.python.fodg.fodg_codec import fodg_page_count_times_seventy_eight, fodg_total_shape_count_times_seventy_eight
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_seventy_eight, gnumeric_total_row_count_times_seventy_eight
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesSeventyEight:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_seventy_eight(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_seventy_eight(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_seventy_eight(_XCF) % 78 == 0
class TestXcfImageTypeIdTimesSeventyEight:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_seventy_eight(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_seventy_eight(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_seventy_eight(_XCF) % 78 == 0
class TestZstFileSizeBytesTimesSeventyEight:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_seventy_eight(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_seventy_eight(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_seventy_eight(_ZST) % 78 == 0
class TestZstDecompressedSizeTimesSeventyEight:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_seventy_eight(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_seventy_eight(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_seventy_eight(_ZST) % 78 == 0
class TestTomlFileSizeBytesTimesSeventyEight:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_seventy_eight(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_seventy_eight(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_seventy_eight(_TOML) % 78 == 0
class TestTomlStringValueCountTimesSeventyEight:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_seventy_eight(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_seventy_eight(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_seventy_eight(_TOML) % 78 == 0
class TestFodgPageCountTimesSeventyEight:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_seventy_eight(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_seventy_eight(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_seventy_eight(_FODG) % 78 == 0
class TestFodgTotalShapeCountTimesSeventyEight:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_seventy_eight(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_seventy_eight(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_seventy_eight(_FODG) % 78 == 0
class TestGnumericFileSizeBytesTimesSeventyEight:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_seventy_eight(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_seventy_eight(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_seventy_eight(_GNUMERIC) % 78 == 0
class TestGnumericTotalRowCountTimesSeventyEight:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_seventy_eight(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_seventy_eight(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_seventy_eight(_GNUMERIC) % 78 == 0

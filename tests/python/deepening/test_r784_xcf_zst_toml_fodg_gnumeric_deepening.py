"""Sprint R784 — XCF/ZST/TOML/FODG/Gnumeric _times_eighty_four composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_eighty_four, xcf_image_type_id_times_eighty_four
from src.python.zst.zst_codec import zst_file_size_bytes_times_eighty_four, zst_decompressed_size_times_eighty_four
from src.python.toml.toml_codec import toml_file_size_bytes_times_eighty_four, toml_string_value_count_times_eighty_four
from src.python.fodg.fodg_codec import fodg_page_count_times_eighty_four, fodg_total_shape_count_times_eighty_four
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_eighty_four, gnumeric_total_row_count_times_eighty_four
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_eighty_four(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_eighty_four(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_eighty_four(_XCF) % 84 == 0
class TestXcfImageTypeIdTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_eighty_four(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_eighty_four(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_eighty_four(_XCF) % 84 == 0
class TestZstFileSizeBytesTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_eighty_four(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_eighty_four(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_eighty_four(_ZST) % 84 == 0
class TestZstDecompressedSizeTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_eighty_four(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_eighty_four(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_eighty_four(_ZST) % 84 == 0
class TestTomlFileSizeBytesTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_eighty_four(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_eighty_four(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_eighty_four(_TOML) % 84 == 0
class TestTomlStringValueCountTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_eighty_four(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_eighty_four(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_eighty_four(_TOML) % 84 == 0
class TestFodgPageCountTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_eighty_four(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_eighty_four(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_eighty_four(_FODG) % 84 == 0
class TestFodgTotalShapeCountTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_eighty_four(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_eighty_four(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_eighty_four(_FODG) % 84 == 0
class TestGnumericFileSizeBytesTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_eighty_four(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_eighty_four(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_eighty_four(_GNUMERIC) % 84 == 0
class TestGnumericTotalRowCountTimesEightyFour:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_eighty_four(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_eighty_four(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_eighty_four(_GNUMERIC) % 84 == 0

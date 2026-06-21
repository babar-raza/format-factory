"""Sprint R660 — XCF/ZST/TOML/FODG/Gnumeric _times_fifty_three composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_fifty_three, xcf_image_type_id_times_fifty_three
from src.python.zst.zst_codec import zst_file_size_bytes_times_fifty_three, zst_decompressed_size_times_fifty_three
from src.python.toml.toml_codec import toml_file_size_bytes_times_fifty_three, toml_string_value_count_times_fifty_three
from src.python.fodg.fodg_codec import fodg_page_count_times_fifty_three, fodg_total_shape_count_times_fifty_three
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_fifty_three, gnumeric_total_row_count_times_fifty_three
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_fifty_three(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_fifty_three(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_fifty_three(_XCF) % 53 == 0
class TestXcfImageTypeIdTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_fifty_three(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_fifty_three(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_fifty_three(_XCF) % 53 == 0
class TestZstFileSizeBytesTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_fifty_three(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_fifty_three(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_fifty_three(_ZST) % 53 == 0
class TestZstDecompressedSizeTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_fifty_three(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_fifty_three(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_fifty_three(_ZST) % 53 == 0
class TestTomlFileSizeBytesTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_fifty_three(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_fifty_three(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_fifty_three(_TOML) % 53 == 0
class TestTomlStringValueCountTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_fifty_three(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_fifty_three(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_fifty_three(_TOML) % 53 == 0
class TestFodgPageCountTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_fifty_three(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_fifty_three(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_fifty_three(_FODG) % 53 == 0
class TestFodgTotalShapeCountTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_fifty_three(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_fifty_three(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_fifty_three(_FODG) % 53 == 0
class TestGnumericFileSizeBytesTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_fifty_three(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_fifty_three(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_fifty_three(_GNUMERIC) % 53 == 0
class TestGnumericTotalRowCountTimesFiftyThree:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_fifty_three(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_fifty_three(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_fifty_three(_GNUMERIC) % 53 == 0

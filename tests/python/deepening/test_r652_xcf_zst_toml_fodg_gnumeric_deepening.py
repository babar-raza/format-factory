"""Sprint R652 — XCF/ZST/TOML/FODG/Gnumeric _times_fifty_one composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_fifty_one, xcf_image_type_id_times_fifty_one
from src.python.zst.zst_codec import zst_file_size_bytes_times_fifty_one, zst_decompressed_size_times_fifty_one
from src.python.toml.toml_codec import toml_file_size_bytes_times_fifty_one, toml_string_value_count_times_fifty_one
from src.python.fodg.fodg_codec import fodg_page_count_times_fifty_one, fodg_total_shape_count_times_fifty_one
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_fifty_one, gnumeric_total_row_count_times_fifty_one
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesFiftyOne:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_fifty_one(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_fifty_one(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_fifty_one(_XCF) % 51 == 0
class TestXcfImageTypeIdTimesFiftyOne:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_fifty_one(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_fifty_one(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_fifty_one(_XCF) % 51 == 0
class TestZstFileSizeBytesTimesFiftyOne:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_fifty_one(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_fifty_one(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_fifty_one(_ZST) % 51 == 0
class TestZstDecompressedSizeTimesFiftyOne:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_fifty_one(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_fifty_one(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_fifty_one(_ZST) % 51 == 0
class TestTomlFileSizeBytesTimesFiftyOne:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_fifty_one(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_fifty_one(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_fifty_one(_TOML) % 51 == 0
class TestTomlStringValueCountTimesFiftyOne:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_fifty_one(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_fifty_one(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_fifty_one(_TOML) % 51 == 0
class TestFodgPageCountTimesFiftyOne:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_fifty_one(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_fifty_one(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_fifty_one(_FODG) % 51 == 0
class TestFodgTotalShapeCountTimesFiftyOne:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_fifty_one(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_fifty_one(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_fifty_one(_FODG) % 51 == 0
class TestGnumericFileSizeBytesTimesFiftyOne:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_fifty_one(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_fifty_one(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_fifty_one(_GNUMERIC) % 51 == 0
class TestGnumericTotalRowCountTimesFiftyOne:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_fifty_one(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_fifty_one(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_fifty_one(_GNUMERIC) % 51 == 0

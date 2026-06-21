"""Sprint R656 — XCF/ZST/TOML/FODG/Gnumeric _times_fifty_two composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_fifty_two, xcf_image_type_id_times_fifty_two
from src.python.zst.zst_codec import zst_file_size_bytes_times_fifty_two, zst_decompressed_size_times_fifty_two
from src.python.toml.toml_codec import toml_file_size_bytes_times_fifty_two, toml_string_value_count_times_fifty_two
from src.python.fodg.fodg_codec import fodg_page_count_times_fifty_two, fodg_total_shape_count_times_fifty_two
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_fifty_two, gnumeric_total_row_count_times_fifty_two
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesFiftyTwo:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_fifty_two(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_fifty_two(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_fifty_two(_XCF) % 52 == 0
class TestXcfImageTypeIdTimesFiftyTwo:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_fifty_two(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_fifty_two(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_fifty_two(_XCF) % 52 == 0
class TestZstFileSizeBytesTimesFiftyTwo:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_fifty_two(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_fifty_two(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_fifty_two(_ZST) % 52 == 0
class TestZstDecompressedSizeTimesFiftyTwo:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_fifty_two(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_fifty_two(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_fifty_two(_ZST) % 52 == 0
class TestTomlFileSizeBytesTimesFiftyTwo:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_fifty_two(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_fifty_two(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_fifty_two(_TOML) % 52 == 0
class TestTomlStringValueCountTimesFiftyTwo:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_fifty_two(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_fifty_two(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_fifty_two(_TOML) % 52 == 0
class TestFodgPageCountTimesFiftyTwo:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_fifty_two(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_fifty_two(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_fifty_two(_FODG) % 52 == 0
class TestFodgTotalShapeCountTimesFiftyTwo:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_fifty_two(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_fifty_two(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_fifty_two(_FODG) % 52 == 0
class TestGnumericFileSizeBytesTimesFiftyTwo:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_fifty_two(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_fifty_two(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_fifty_two(_GNUMERIC) % 52 == 0
class TestGnumericTotalRowCountTimesFiftyTwo:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_fifty_two(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_fifty_two(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_fifty_two(_GNUMERIC) % 52 == 0

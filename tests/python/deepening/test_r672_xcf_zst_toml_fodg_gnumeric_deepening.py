"""Sprint R672 — XCF/ZST/TOML/FODG/Gnumeric _times_fifty_six composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_fifty_six, xcf_image_type_id_times_fifty_six
from src.python.zst.zst_codec import zst_file_size_bytes_times_fifty_six, zst_decompressed_size_times_fifty_six
from src.python.toml.toml_codec import toml_file_size_bytes_times_fifty_six, toml_string_value_count_times_fifty_six
from src.python.fodg.fodg_codec import fodg_page_count_times_fifty_six, fodg_total_shape_count_times_fifty_six
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_fifty_six, gnumeric_total_row_count_times_fifty_six
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesFiftySix:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_fifty_six(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_fifty_six(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_fifty_six(_XCF) % 56 == 0
class TestXcfImageTypeIdTimesFiftySix:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_fifty_six(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_fifty_six(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_fifty_six(_XCF) % 56 == 0
class TestZstFileSizeBytesTimesFiftySix:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_fifty_six(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_fifty_six(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_fifty_six(_ZST) % 56 == 0
class TestZstDecompressedSizeTimesFiftySix:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_fifty_six(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_fifty_six(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_fifty_six(_ZST) % 56 == 0
class TestTomlFileSizeBytesTimesFiftySix:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_fifty_six(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_fifty_six(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_fifty_six(_TOML) % 56 == 0
class TestTomlStringValueCountTimesFiftySix:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_fifty_six(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_fifty_six(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_fifty_six(_TOML) % 56 == 0
class TestFodgPageCountTimesFiftySix:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_fifty_six(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_fifty_six(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_fifty_six(_FODG) % 56 == 0
class TestFodgTotalShapeCountTimesFiftySix:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_fifty_six(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_fifty_six(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_fifty_six(_FODG) % 56 == 0
class TestGnumericFileSizeBytesTimesFiftySix:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_fifty_six(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_fifty_six(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_fifty_six(_GNUMERIC) % 56 == 0
class TestGnumericTotalRowCountTimesFiftySix:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_fifty_six(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_fifty_six(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_fifty_six(_GNUMERIC) % 56 == 0

"""Sprint R688 — XCF/ZST/TOML/FODG/Gnumeric _times_sixty composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_sixty, xcf_image_type_id_times_sixty
from src.python.zst.zst_codec import zst_file_size_bytes_times_sixty, zst_decompressed_size_times_sixty
from src.python.toml.toml_codec import toml_file_size_bytes_times_sixty, toml_string_value_count_times_sixty
from src.python.fodg.fodg_codec import fodg_page_count_times_sixty, fodg_total_shape_count_times_sixty
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_sixty, gnumeric_total_row_count_times_sixty
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesSixty:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_sixty(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_sixty(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_sixty(_XCF) % 60 == 0
class TestXcfImageTypeIdTimesSixty:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_sixty(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_sixty(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_sixty(_XCF) % 60 == 0
class TestZstFileSizeBytesTimesSixty:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_sixty(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_sixty(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_sixty(_ZST) % 60 == 0
class TestZstDecompressedSizeTimesSixty:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_sixty(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_sixty(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_sixty(_ZST) % 60 == 0
class TestTomlFileSizeBytesTimesSixty:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_sixty(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_sixty(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_sixty(_TOML) % 60 == 0
class TestTomlStringValueCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_sixty(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_sixty(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_sixty(_TOML) % 60 == 0
class TestFodgPageCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_sixty(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_sixty(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_sixty(_FODG) % 60 == 0
class TestFodgTotalShapeCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_sixty(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_sixty(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_sixty(_FODG) % 60 == 0
class TestGnumericFileSizeBytesTimesSixty:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_sixty(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_sixty(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_sixty(_GNUMERIC) % 60 == 0
class TestGnumericTotalRowCountTimesSixty:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_sixty(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_sixty(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_sixty(_GNUMERIC) % 60 == 0

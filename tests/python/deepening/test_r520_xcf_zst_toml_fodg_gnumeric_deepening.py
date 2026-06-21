"""Sprint R520 — XCF/ZST/TOML/FODG/Gnumeric _times_eighteen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_eighteen, xcf_image_type_id_times_eighteen
from src.python.zst.zst_codec import zst_file_size_bytes_times_eighteen, zst_decompressed_size_times_eighteen
from src.python.toml.toml_codec import toml_file_size_bytes_times_eighteen, toml_string_value_count_times_eighteen
from src.python.fodg.fodg_codec import fodg_page_count_times_eighteen, fodg_total_shape_count_times_eighteen
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_eighteen, gnumeric_total_row_count_times_eighteen
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesEighteen:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_eighteen(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_eighteen(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_eighteen(_XCF) % 18 == 0
class TestXcfImageTypeIdTimesEighteen:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_eighteen(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_eighteen(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_eighteen(_XCF) % 18 == 0
class TestZstFileSizeBytesTimesEighteen:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_eighteen(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_eighteen(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_eighteen(_ZST) % 18 == 0
class TestZstDecompressedSizeTimesEighteen:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_eighteen(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_eighteen(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_eighteen(_ZST) % 18 == 0
class TestTomlFileSizeBytesTimesEighteen:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_eighteen(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_eighteen(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_eighteen(_TOML) % 18 == 0
class TestTomlStringValueCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_eighteen(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_eighteen(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_eighteen(_TOML) % 18 == 0
class TestFodgPageCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_eighteen(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_eighteen(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_eighteen(_FODG) % 18 == 0
class TestFodgTotalShapeCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_eighteen(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_eighteen(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_eighteen(_FODG) % 18 == 0
class TestGnumericFileSizeBytesTimesEighteen:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_eighteen(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_eighteen(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_eighteen(_GNUMERIC) % 18 == 0
class TestGnumericTotalRowCountTimesEighteen:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_eighteen(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_eighteen(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_eighteen(_GNUMERIC) % 18 == 0

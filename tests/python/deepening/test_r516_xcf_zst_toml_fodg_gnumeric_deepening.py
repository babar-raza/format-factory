"""Sprint R516 — XCF/ZST/TOML/FODG/Gnumeric _times_seventeen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_seventeen, xcf_image_type_id_times_seventeen
from src.python.zst.zst_codec import zst_file_size_bytes_times_seventeen, zst_decompressed_size_times_seventeen
from src.python.toml.toml_codec import toml_file_size_bytes_times_seventeen, toml_string_value_count_times_seventeen
from src.python.fodg.fodg_codec import fodg_page_count_times_seventeen, fodg_total_shape_count_times_seventeen
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_seventeen, gnumeric_total_row_count_times_seventeen
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_seventeen(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_seventeen(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_seventeen(_XCF) % 17 == 0
class TestXcfImageTypeIdTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_seventeen(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_seventeen(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_seventeen(_XCF) % 17 == 0
class TestZstFileSizeBytesTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_seventeen(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_seventeen(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_seventeen(_ZST) % 17 == 0
class TestZstDecompressedSizeTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_seventeen(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_seventeen(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_seventeen(_ZST) % 17 == 0
class TestTomlFileSizeBytesTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_seventeen(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_seventeen(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_seventeen(_TOML) % 17 == 0
class TestTomlStringValueCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_seventeen(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_seventeen(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_seventeen(_TOML) % 17 == 0
class TestFodgPageCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_seventeen(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_seventeen(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_seventeen(_FODG) % 17 == 0
class TestFodgTotalShapeCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_seventeen(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_seventeen(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_seventeen(_FODG) % 17 == 0
class TestGnumericFileSizeBytesTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_seventeen(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_seventeen(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_seventeen(_GNUMERIC) % 17 == 0
class TestGnumericTotalRowCountTimesSeventeen:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_seventeen(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_seventeen(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_seventeen(_GNUMERIC) % 17 == 0

"""Sprint R524 — XCF/ZST/TOML/FODG/Gnumeric _times_nineteen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_nineteen, xcf_image_type_id_times_nineteen
from src.python.zst.zst_codec import zst_file_size_bytes_times_nineteen, zst_decompressed_size_times_nineteen
from src.python.toml.toml_codec import toml_file_size_bytes_times_nineteen, toml_string_value_count_times_nineteen
from src.python.fodg.fodg_codec import fodg_page_count_times_nineteen, fodg_total_shape_count_times_nineteen
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_nineteen, gnumeric_total_row_count_times_nineteen
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesNineteen:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_nineteen(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_nineteen(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_nineteen(_XCF) % 19 == 0
class TestXcfImageTypeIdTimesNineteen:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_nineteen(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_nineteen(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_nineteen(_XCF) % 19 == 0
class TestZstFileSizeBytesTimesNineteen:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_nineteen(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_nineteen(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_nineteen(_ZST) % 19 == 0
class TestZstDecompressedSizeTimesNineteen:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_nineteen(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_nineteen(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_nineteen(_ZST) % 19 == 0
class TestTomlFileSizeBytesTimesNineteen:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_nineteen(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_nineteen(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_nineteen(_TOML) % 19 == 0
class TestTomlStringValueCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_nineteen(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_nineteen(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_nineteen(_TOML) % 19 == 0
class TestFodgPageCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_nineteen(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_nineteen(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_nineteen(_FODG) % 19 == 0
class TestFodgTotalShapeCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_nineteen(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_nineteen(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_nineteen(_FODG) % 19 == 0
class TestGnumericFileSizeBytesTimesNineteen:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_nineteen(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_nineteen(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_nineteen(_GNUMERIC) % 19 == 0
class TestGnumericTotalRowCountTimesNineteen:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_nineteen(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_nineteen(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_nineteen(_GNUMERIC) % 19 == 0

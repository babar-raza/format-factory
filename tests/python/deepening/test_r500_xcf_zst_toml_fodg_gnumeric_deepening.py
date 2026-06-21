"""Sprint R500 — XCF/ZST/TOML/FODG/Gnumeric _times_thirteen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_thirteen, xcf_image_type_id_times_thirteen
from src.python.zst.zst_codec import zst_file_size_bytes_times_thirteen, zst_decompressed_size_times_thirteen
from src.python.toml.toml_codec import toml_file_size_bytes_times_thirteen, toml_string_value_count_times_thirteen
from src.python.fodg.fodg_codec import fodg_page_count_times_thirteen, fodg_total_shape_count_times_thirteen
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_thirteen, gnumeric_total_row_count_times_thirteen
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesThirteen:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_thirteen(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_thirteen(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_thirteen(_XCF) % 13 == 0

class TestXcfImageTypeIdTimesThirteen:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_thirteen(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_thirteen(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_thirteen(_XCF) % 13 == 0

class TestZstFileSizeBytesTimesThirteen:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_thirteen(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_thirteen(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_thirteen(_ZST) % 13 == 0

class TestZstDecompressedSizeTimesThirteen:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_thirteen(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_thirteen(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_thirteen(_ZST) % 13 == 0

class TestTomlFileSizeBytesTimesThirteen:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_thirteen(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_thirteen(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_thirteen(_TOML) % 13 == 0

class TestTomlStringValueCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_thirteen(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_thirteen(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_thirteen(_TOML) % 13 == 0

class TestFodgPageCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_thirteen(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_thirteen(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_thirteen(_FODG) % 13 == 0

class TestFodgTotalShapeCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_thirteen(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_thirteen(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_thirteen(_FODG) % 13 == 0

class TestGnumericFileSizeBytesTimesThirteen:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_thirteen(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_thirteen(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_thirteen(_GNUMERIC) % 13 == 0

class TestGnumericTotalRowCountTimesThirteen:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_thirteen(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_thirteen(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_thirteen(_GNUMERIC) % 13 == 0

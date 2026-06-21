"""Sprint R508 — XCF/ZST/TOML/FODG/Gnumeric _times_fifteen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_fifteen, xcf_image_type_id_times_fifteen
from src.python.zst.zst_codec import zst_file_size_bytes_times_fifteen, zst_decompressed_size_times_fifteen
from src.python.toml.toml_codec import toml_file_size_bytes_times_fifteen, toml_string_value_count_times_fifteen
from src.python.fodg.fodg_codec import fodg_page_count_times_fifteen, fodg_total_shape_count_times_fifteen
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_fifteen, gnumeric_total_row_count_times_fifteen
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesFifteen:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_fifteen(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_fifteen(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_fifteen(_XCF) % 15 == 0

class TestXcfImageTypeIdTimesFifteen:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_fifteen(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_fifteen(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_fifteen(_XCF) % 15 == 0

class TestZstFileSizeBytesTimesFifteen:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_fifteen(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_fifteen(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_fifteen(_ZST) % 15 == 0

class TestZstDecompressedSizeTimesFifteen:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_fifteen(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_fifteen(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_fifteen(_ZST) % 15 == 0

class TestTomlFileSizeBytesTimesFifteen:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_fifteen(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_fifteen(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_fifteen(_TOML) % 15 == 0

class TestTomlStringValueCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_fifteen(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_fifteen(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_fifteen(_TOML) % 15 == 0

class TestFodgPageCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_fifteen(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_fifteen(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_fifteen(_FODG) % 15 == 0

class TestFodgTotalShapeCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_fifteen(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_fifteen(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_fifteen(_FODG) % 15 == 0

class TestGnumericFileSizeBytesTimesFifteen:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_fifteen(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_fifteen(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_fifteen(_GNUMERIC) % 15 == 0

class TestGnumericTotalRowCountTimesFifteen:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_fifteen(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_fifteen(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_fifteen(_GNUMERIC) % 15 == 0

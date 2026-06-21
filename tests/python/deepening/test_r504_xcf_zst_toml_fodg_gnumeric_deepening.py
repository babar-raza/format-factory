"""Sprint R504 — XCF/ZST/TOML/FODG/Gnumeric _times_fourteen composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_fourteen, xcf_image_type_id_times_fourteen
from src.python.zst.zst_codec import zst_file_size_bytes_times_fourteen, zst_decompressed_size_times_fourteen
from src.python.toml.toml_codec import toml_file_size_bytes_times_fourteen, toml_string_value_count_times_fourteen
from src.python.fodg.fodg_codec import fodg_page_count_times_fourteen, fodg_total_shape_count_times_fourteen
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_fourteen, gnumeric_total_row_count_times_fourteen
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesFourteen:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_fourteen(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_fourteen(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_fourteen(_XCF) % 14 == 0

class TestXcfImageTypeIdTimesFourteen:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_fourteen(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_fourteen(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_fourteen(_XCF) % 14 == 0

class TestZstFileSizeBytesTimesFourteen:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_fourteen(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_fourteen(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_fourteen(_ZST) % 14 == 0

class TestZstDecompressedSizeTimesFourteen:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_fourteen(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_fourteen(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_fourteen(_ZST) % 14 == 0

class TestTomlFileSizeBytesTimesFourteen:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_fourteen(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_fourteen(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_fourteen(_TOML) % 14 == 0

class TestTomlStringValueCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_fourteen(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_fourteen(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_fourteen(_TOML) % 14 == 0

class TestFodgPageCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_fourteen(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_fourteen(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_fourteen(_FODG) % 14 == 0

class TestFodgTotalShapeCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_fourteen(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_fourteen(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_fourteen(_FODG) % 14 == 0

class TestGnumericFileSizeBytesTimesFourteen:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_fourteen(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_fourteen(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_fourteen(_GNUMERIC) % 14 == 0

class TestGnumericTotalRowCountTimesFourteen:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_fourteen(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_fourteen(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_fourteen(_GNUMERIC) % 14 == 0

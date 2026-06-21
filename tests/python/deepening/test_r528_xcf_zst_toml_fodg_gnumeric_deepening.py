"""Sprint R528 — XCF/ZST/TOML/FODG/Gnumeric _times_twenty composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_twenty, xcf_image_type_id_times_twenty
from src.python.zst.zst_codec import zst_file_size_bytes_times_twenty, zst_decompressed_size_times_twenty
from src.python.toml.toml_codec import toml_file_size_bytes_times_twenty, toml_string_value_count_times_twenty
from src.python.fodg.fodg_codec import fodg_page_count_times_twenty, fodg_total_shape_count_times_twenty
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_twenty, gnumeric_total_row_count_times_twenty
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesTwenty:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_twenty(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_twenty(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_twenty(_XCF) % 20 == 0
class TestXcfImageTypeIdTimesTwenty:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_twenty(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_twenty(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_twenty(_XCF) % 20 == 0
class TestZstFileSizeBytesTimesTwenty:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_twenty(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_twenty(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_twenty(_ZST) % 20 == 0
class TestZstDecompressedSizeTimesTwenty:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_twenty(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_twenty(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_twenty(_ZST) % 20 == 0
class TestTomlFileSizeBytesTimesTwenty:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_twenty(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_twenty(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_twenty(_TOML) % 20 == 0
class TestTomlStringValueCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_twenty(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_twenty(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_twenty(_TOML) % 20 == 0
class TestFodgPageCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_twenty(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_twenty(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_twenty(_FODG) % 20 == 0
class TestFodgTotalShapeCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_twenty(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_twenty(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_twenty(_FODG) % 20 == 0
class TestGnumericFileSizeBytesTimesTwenty:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_twenty(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_twenty(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_twenty(_GNUMERIC) % 20 == 0
class TestGnumericTotalRowCountTimesTwenty:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_twenty(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_twenty(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_twenty(_GNUMERIC) % 20 == 0

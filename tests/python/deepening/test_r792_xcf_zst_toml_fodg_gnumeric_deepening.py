"""Sprint R792 — XCF/ZST/TOML/FODG/Gnumeric _times_eighty_six composite analytics tests."""
import sys, pathlib
_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_eighty_six, xcf_image_type_id_times_eighty_six
from src.python.zst.zst_codec import zst_file_size_bytes_times_eighty_six, zst_decompressed_size_times_eighty_six
from src.python.toml.toml_codec import toml_file_size_bytes_times_eighty_six, toml_string_value_count_times_eighty_six
from src.python.fodg.fodg_codec import fodg_page_count_times_eighty_six, fodg_total_shape_count_times_eighty_six
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_eighty_six, gnumeric_total_row_count_times_eighty_six
SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_ZST = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
_TOML = str(SAMPLES / "toml" / "minimal.toml")
_FODG = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
_GNUMERIC = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")

class TestXcfFileSizeBytesTimesEightySix:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_eighty_six(_XCF), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_eighty_six(_XCF) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_eighty_six(_XCF) % 86 == 0
class TestXcfImageTypeIdTimesEightySix:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_eighty_six(_XCF), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_eighty_six(_XCF) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_eighty_six(_XCF) % 86 == 0
class TestZstFileSizeBytesTimesEightySix:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_eighty_six(_ZST), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_eighty_six(_ZST) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_eighty_six(_ZST) % 86 == 0
class TestZstDecompressedSizeTimesEightySix:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_eighty_six(_ZST), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_eighty_six(_ZST) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_eighty_six(_ZST) % 86 == 0
class TestTomlFileSizeBytesTimesEightySix:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_eighty_six(_TOML), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_eighty_six(_TOML) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_eighty_six(_TOML) % 86 == 0
class TestTomlStringValueCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_eighty_six(_TOML), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_eighty_six(_TOML) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_eighty_six(_TOML) % 86 == 0
class TestFodgPageCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_eighty_six(_FODG), int)
    def test_non_negative(self):
        assert fodg_page_count_times_eighty_six(_FODG) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_eighty_six(_FODG) % 86 == 0
class TestFodgTotalShapeCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_eighty_six(_FODG), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_eighty_six(_FODG) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_eighty_six(_FODG) % 86 == 0
class TestGnumericFileSizeBytesTimesEightySix:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_eighty_six(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_eighty_six(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_eighty_six(_GNUMERIC) % 86 == 0
class TestGnumericTotalRowCountTimesEightySix:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_eighty_six(_GNUMERIC), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_eighty_six(_GNUMERIC) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_eighty_six(_GNUMERIC) % 86 == 0

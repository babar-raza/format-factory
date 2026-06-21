"""Sprint R476 — XCF/ZST/TOML/FODG/Gnumeric _times_seven composite analytics tests."""
import pathlib, sys

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.xcf.xcf_parser import xcf_file_size_times_seven, xcf_image_type_id_times_seven
from src.python.zst.zst_codec import zst_file_size_times_seven, zst_decompressed_size_times_seven
from src.python.toml.toml_codec import toml_file_size_times_seven, toml_string_value_count_times_seven
from src.python.fodg.fodg_codec import fodg_page_count_times_seven, fodg_total_shape_count_times_seven
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_times_seven, gnumeric_total_row_count_times_seven

class TestXcfFileSizeTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(xcf_file_size_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_file_size_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_file_size_times_seven(p) % 7 == 0

class TestXcfImageTypeIdTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(xcf_image_type_id_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_image_type_id_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_image_type_id_times_seven(p) % 7 == 0

class TestZstFileSizeTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(zst_file_size_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_file_size_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_file_size_times_seven(p) % 7 == 0

class TestZstDecompressedSizeTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(zst_decompressed_size_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_decompressed_size_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_decompressed_size_times_seven(p) % 7 == 0

class TestTomlFileSizeTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert isinstance(toml_file_size_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_file_size_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_file_size_times_seven(p) % 7 == 0

class TestTomlStringValueCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert isinstance(toml_string_value_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_string_value_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_string_value_count_times_seven(p) % 7 == 0

class TestFodgPageCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert isinstance(fodg_page_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_page_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_page_count_times_seven(p) % 7 == 0

class TestFodgTotalShapeCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert isinstance(fodg_total_shape_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_total_shape_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_total_shape_count_times_seven(p) % 7 == 0

class TestGnumericFileSizeTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert isinstance(gnumeric_file_size_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_file_size_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_file_size_times_seven(p) % 7 == 0

class TestGnumericTotalRowCountTimesSeven:
    def test_returns_int(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert isinstance(gnumeric_total_row_count_times_seven(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_total_row_count_times_seven(p) >= 0
    def test_divisible_by_seven(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_total_row_count_times_seven(p) % 7 == 0

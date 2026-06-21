"""Sprint R484 — XCF/ZST/TOML/FODG/Gnumeric _times_nine composite analytics tests."""
import sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_file_size_times_nine, xcf_image_type_id_times_nine
from src.python.zst.zst_codec import zst_file_size_times_nine, zst_decompressed_size_times_nine
from src.python.toml.toml_codec import toml_file_size_times_nine, toml_string_value_count_times_nine
from src.python.fodg.fodg_codec import fodg_page_count_times_nine, fodg_total_shape_count_times_nine
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_times_nine, gnumeric_total_row_count_times_nine

SAMPLES = _REPO / "samples" / "by-format"

class TestXcfFileSizeTimesNine:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_times_nine(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")), int)
    def test_non_negative(self):
        assert xcf_file_size_times_nine(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")) >= 0
    def test_divisible(self):
        assert xcf_file_size_times_nine(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")) % 9 == 0

class TestXcfImageTypeIdTimesNine:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_nine(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_nine(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_nine(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")) % 9 == 0

class TestZstFileSizeTimesNine:
    def test_returns_int(self):
        assert isinstance(zst_file_size_times_nine(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")), int)
    def test_non_negative(self):
        assert zst_file_size_times_nine(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")) >= 0
    def test_divisible(self):
        assert zst_file_size_times_nine(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")) % 9 == 0

class TestZstDecompressedSizeTimesNine:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_nine(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_nine(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_nine(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")) % 9 == 0

class TestTomlFileSizeTimesNine:
    def test_returns_int(self):
        assert isinstance(toml_file_size_times_nine(str(SAMPLES / "toml" / "minimal.toml")), int)
    def test_non_negative(self):
        assert toml_file_size_times_nine(str(SAMPLES / "toml" / "minimal.toml")) >= 0
    def test_divisible(self):
        assert toml_file_size_times_nine(str(SAMPLES / "toml" / "minimal.toml")) % 9 == 0

class TestTomlStringValueCountTimesNine:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_nine(str(SAMPLES / "toml" / "minimal.toml")), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_nine(str(SAMPLES / "toml" / "minimal.toml")) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_nine(str(SAMPLES / "toml" / "minimal.toml")) % 9 == 0

class TestFodgPageCountTimesNine:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_nine(str(SAMPLES / "fodg" / "minimal-drawing.fodg")), int)
    def test_non_negative(self):
        assert fodg_page_count_times_nine(str(SAMPLES / "fodg" / "minimal-drawing.fodg")) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_nine(str(SAMPLES / "fodg" / "minimal-drawing.fodg")) % 9 == 0

class TestFodgTotalShapeCountTimesNine:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_nine(str(SAMPLES / "fodg" / "minimal-drawing.fodg")), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_nine(str(SAMPLES / "fodg" / "minimal-drawing.fodg")) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_nine(str(SAMPLES / "fodg" / "minimal-drawing.fodg")) % 9 == 0

class TestGnumericFileSizeTimesNine:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_times_nine(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")), int)
    def test_non_negative(self):
        assert gnumeric_file_size_times_nine(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_times_nine(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")) % 9 == 0

class TestGnumericTotalRowCountTimesNine:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_nine(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_nine(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_nine(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")) % 9 == 0

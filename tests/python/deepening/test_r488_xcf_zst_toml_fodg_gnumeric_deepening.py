"""Sprint R488 — XCF/ZST/TOML/FODG/Gnumeric _times_ten composite analytics tests."""
import sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_file_size_bytes_times_ten, xcf_image_type_id_times_ten
from src.python.zst.zst_codec import zst_file_size_bytes_times_ten, zst_decompressed_size_times_ten
from src.python.toml.toml_codec import toml_file_size_bytes_times_ten, toml_string_value_count_times_ten
from src.python.fodg.fodg_codec import fodg_page_count_times_ten, fodg_total_shape_count_times_ten
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_bytes_times_ten, gnumeric_total_row_count_times_ten

SAMPLES = _REPO / "samples" / "by-format"

class TestXcfFileSizeBytesTimesTen:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_bytes_times_ten(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")), int)
    def test_non_negative(self):
        assert xcf_file_size_bytes_times_ten(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")) >= 0
    def test_divisible(self):
        assert xcf_file_size_bytes_times_ten(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")) % 10 == 0

class TestXcfImageTypeIdTimesTen:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_ten(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_ten(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_ten(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")) % 10 == 0

class TestZstFileSizeBytesTimesTen:
    def test_returns_int(self):
        assert isinstance(zst_file_size_bytes_times_ten(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")), int)
    def test_non_negative(self):
        assert zst_file_size_bytes_times_ten(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")) >= 0
    def test_divisible(self):
        assert zst_file_size_bytes_times_ten(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")) % 10 == 0

class TestZstDecompressedSizeTimesTen:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_ten(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_ten(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_ten(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")) % 10 == 0

class TestTomlFileSizeBytesTimesTen:
    def test_returns_int(self):
        assert isinstance(toml_file_size_bytes_times_ten(str(SAMPLES / "toml" / "minimal.toml")), int)
    def test_non_negative(self):
        assert toml_file_size_bytes_times_ten(str(SAMPLES / "toml" / "minimal.toml")) >= 0
    def test_divisible(self):
        assert toml_file_size_bytes_times_ten(str(SAMPLES / "toml" / "minimal.toml")) % 10 == 0

class TestTomlStringValueCountTimesTen:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_ten(str(SAMPLES / "toml" / "minimal.toml")), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_ten(str(SAMPLES / "toml" / "minimal.toml")) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_ten(str(SAMPLES / "toml" / "minimal.toml")) % 10 == 0

class TestFodgPageCountTimesTen:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_ten(str(SAMPLES / "fodg" / "minimal-drawing.fodg")), int)
    def test_non_negative(self):
        assert fodg_page_count_times_ten(str(SAMPLES / "fodg" / "minimal-drawing.fodg")) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_ten(str(SAMPLES / "fodg" / "minimal-drawing.fodg")) % 10 == 0

class TestFodgTotalShapeCountTimesTen:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_ten(str(SAMPLES / "fodg" / "minimal-drawing.fodg")), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_ten(str(SAMPLES / "fodg" / "minimal-drawing.fodg")) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_ten(str(SAMPLES / "fodg" / "minimal-drawing.fodg")) % 10 == 0

class TestGnumericFileSizeBytesTimesTen:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_bytes_times_ten(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")), int)
    def test_non_negative(self):
        assert gnumeric_file_size_bytes_times_ten(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_bytes_times_ten(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")) % 10 == 0

class TestGnumericTotalRowCountTimesTen:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_ten(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_ten(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_ten(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")) % 10 == 0

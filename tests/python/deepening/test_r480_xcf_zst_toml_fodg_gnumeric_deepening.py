"""Sprint R480 — XCF/ZST/TOML/FODG/Gnumeric _times_eight composite analytics tests."""
import sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_file_size_times_eight, xcf_image_type_id_times_eight
from src.python.zst.zst_codec import zst_file_size_times_eight, zst_decompressed_size_times_eight
from src.python.toml.toml_codec import toml_file_size_times_eight, toml_string_value_count_times_eight
from src.python.fodg.fodg_codec import fodg_page_count_times_eight, fodg_total_shape_count_times_eight
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_times_eight, gnumeric_total_row_count_times_eight

SAMPLES = _REPO / "samples" / "by-format"

# --- XCF ---
class TestXcfFileSizeTimesEight:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_times_eight(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")), int)
    def test_non_negative(self):
        assert xcf_file_size_times_eight(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")) >= 0
    def test_divisible(self):
        assert xcf_file_size_times_eight(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")) % 8 == 0

class TestXcfImageTypeIdTimesEight:
    def test_returns_int(self):
        assert isinstance(xcf_image_type_id_times_eight(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")), int)
    def test_non_negative(self):
        assert xcf_image_type_id_times_eight(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")) >= 0
    def test_divisible(self):
        assert xcf_image_type_id_times_eight(str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")) % 8 == 0

# --- ZST ---
class TestZstFileSizeTimesEight:
    def test_returns_int(self):
        assert isinstance(zst_file_size_times_eight(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")), int)
    def test_non_negative(self):
        assert zst_file_size_times_eight(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")) >= 0
    def test_divisible(self):
        assert zst_file_size_times_eight(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")) % 8 == 0

class TestZstDecompressedSizeTimesEight:
    def test_returns_int(self):
        assert isinstance(zst_decompressed_size_times_eight(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")), int)
    def test_non_negative(self):
        assert zst_decompressed_size_times_eight(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")) >= 0
    def test_divisible(self):
        assert zst_decompressed_size_times_eight(str(SAMPLES / "zst" / "valid" / "text-compressed.zst")) % 8 == 0

# --- TOML ---
class TestTomlFileSizeTimesEight:
    def test_returns_int(self):
        assert isinstance(toml_file_size_times_eight(str(SAMPLES / "toml" / "minimal.toml")), int)
    def test_non_negative(self):
        assert toml_file_size_times_eight(str(SAMPLES / "toml" / "minimal.toml")) >= 0
    def test_divisible(self):
        assert toml_file_size_times_eight(str(SAMPLES / "toml" / "minimal.toml")) % 8 == 0

class TestTomlStringValueCountTimesEight:
    def test_returns_int(self):
        assert isinstance(toml_string_value_count_times_eight(str(SAMPLES / "toml" / "minimal.toml")), int)
    def test_non_negative(self):
        assert toml_string_value_count_times_eight(str(SAMPLES / "toml" / "minimal.toml")) >= 0
    def test_divisible(self):
        assert toml_string_value_count_times_eight(str(SAMPLES / "toml" / "minimal.toml")) % 8 == 0

# --- FODG ---
class TestFodgPageCountTimesEight:
    def test_returns_int(self):
        assert isinstance(fodg_page_count_times_eight(str(SAMPLES / "fodg" / "minimal-drawing.fodg")), int)
    def test_non_negative(self):
        assert fodg_page_count_times_eight(str(SAMPLES / "fodg" / "minimal-drawing.fodg")) >= 0
    def test_divisible(self):
        assert fodg_page_count_times_eight(str(SAMPLES / "fodg" / "minimal-drawing.fodg")) % 8 == 0

class TestFodgTotalShapeCountTimesEight:
    def test_returns_int(self):
        assert isinstance(fodg_total_shape_count_times_eight(str(SAMPLES / "fodg" / "minimal-drawing.fodg")), int)
    def test_non_negative(self):
        assert fodg_total_shape_count_times_eight(str(SAMPLES / "fodg" / "minimal-drawing.fodg")) >= 0
    def test_divisible(self):
        assert fodg_total_shape_count_times_eight(str(SAMPLES / "fodg" / "minimal-drawing.fodg")) % 8 == 0

# --- Gnumeric ---
class TestGnumericFileSizeTimesEight:
    def test_returns_int(self):
        assert isinstance(gnumeric_file_size_times_eight(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")), int)
    def test_non_negative(self):
        assert gnumeric_file_size_times_eight(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")) >= 0
    def test_divisible(self):
        assert gnumeric_file_size_times_eight(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")) % 8 == 0

class TestGnumericTotalRowCountTimesEight:
    def test_returns_int(self):
        assert isinstance(gnumeric_total_row_count_times_eight(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")), int)
    def test_non_negative(self):
        assert gnumeric_total_row_count_times_eight(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")) >= 0
    def test_divisible(self):
        assert gnumeric_total_row_count_times_eight(str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")) % 8 == 0

"""Sprint R472 — XCF/ZST/TOML/FODG/Gnumeric _times_six composite analytics tests."""
import pathlib, sys

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.xcf.xcf_parser import xcf_file_size_times_six, xcf_image_type_id_times_six
from src.python.zst.zst_codec import zst_file_size_times_six, zst_decompressed_size_times_six
from src.python.toml.toml_codec import toml_file_size_times_six, toml_string_value_count_times_six
from src.python.fodg.fodg_codec import fodg_page_count_times_six, fodg_total_shape_count_times_six
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_times_six, gnumeric_total_row_count_times_six

# --- XCF ---
class TestXcfFileSizeTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(xcf_file_size_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_file_size_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_file_size_times_six(p) % 6 == 0

class TestXcfImageTypeIdTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(xcf_image_type_id_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_image_type_id_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_image_type_id_times_six(p) % 6 == 0

# --- ZST ---
class TestZstFileSizeTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(zst_file_size_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_file_size_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_file_size_times_six(p) % 6 == 0

class TestZstDecompressedSizeTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(zst_decompressed_size_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_decompressed_size_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_decompressed_size_times_six(p) % 6 == 0

# --- TOML ---
class TestTomlFileSizeTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert isinstance(toml_file_size_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_file_size_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_file_size_times_six(p) % 6 == 0

class TestTomlStringValueCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert isinstance(toml_string_value_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_string_value_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_string_value_count_times_six(p) % 6 == 0

# --- FODG ---
class TestFodgPageCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert isinstance(fodg_page_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_page_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_page_count_times_six(p) % 6 == 0

class TestFodgTotalShapeCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert isinstance(fodg_total_shape_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_total_shape_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_total_shape_count_times_six(p) % 6 == 0

# --- Gnumeric ---
class TestGnumericFileSizeTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert isinstance(gnumeric_file_size_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_file_size_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_file_size_times_six(p) % 6 == 0

class TestGnumericTotalRowCountTimesSix:
    def test_returns_int(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert isinstance(gnumeric_total_row_count_times_six(p), int)
    def test_non_negative(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_total_row_count_times_six(p) >= 0
    def test_divisible_by_six(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_total_row_count_times_six(p) % 6 == 0

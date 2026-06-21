"""Sprint R468 — XCF/ZST/TOML/FODG/Gnumeric round 13 deepening (_times_five)."""
import os, sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.xcf.xcf_parser import xcf_file_size_times_five, xcf_image_type_id_times_five
from src.python.zst.zst_codec import zst_file_size_times_five, zst_decompressed_size_times_five
from src.python.toml.toml_codec import toml_file_size_times_five, toml_string_value_count_times_five
from src.python.fodg.fodg_codec import fodg_page_count_times_five, fodg_total_shape_count_times_five
from src.python.gnumeric.gnumeric_codec import gnumeric_file_size_times_five, gnumeric_total_row_count_times_five


# --- XCF ---
class TestXcfFileSizeTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(xcf_file_size_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_file_size_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_file_size_times_five(p) % 5 == 0


class TestXcfImageTypeIdTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(xcf_image_type_id_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_image_type_id_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_image_type_id_times_five(p) % 5 == 0


# --- ZST ---
class TestZstFileSizeTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(zst_file_size_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_file_size_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_file_size_times_five(p) % 5 == 0


class TestZstDecompressedSizeTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(zst_decompressed_size_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_decompressed_size_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_decompressed_size_times_five(p) % 5 == 0


# --- TOML ---
class TestTomlFileSizeTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert isinstance(toml_file_size_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_file_size_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_file_size_times_five(p) % 5 == 0


class TestTomlStringValueCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert isinstance(toml_string_value_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_string_value_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_string_value_count_times_five(p) % 5 == 0


# --- FODG ---
class TestFodgPageCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert isinstance(fodg_page_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_page_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_page_count_times_five(p) % 5 == 0


class TestFodgTotalShapeCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert isinstance(fodg_total_shape_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_total_shape_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_total_shape_count_times_five(p) % 5 == 0


# --- Gnumeric ---
class TestGnumericFileSizeTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert isinstance(gnumeric_file_size_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_file_size_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_file_size_times_five(p) % 5 == 0


class TestGnumericTotalRowCountTimesFive:
    def test_returns_int(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert isinstance(gnumeric_total_row_count_times_five(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_total_row_count_times_five(p) >= 0

    def test_divisible_by_five(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_total_row_count_times_five(p) % 5 == 0

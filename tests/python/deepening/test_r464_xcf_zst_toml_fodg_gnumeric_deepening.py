"""Sprint R464 — XCF/ZST/TOML/FODG/Gnumeric round 12 deepening (_times_four continued)."""
import os, sys, pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

SAMPLES = _REPO / "samples" / "by-format"

from src.python.xcf import xcf_file_size_times_four, xcf_image_type_id_times_four
from src.python.zst import zst_file_size_times_four, zst_decompressed_size_times_four
from src.python.toml import toml_file_size_times_four, toml_string_value_count_times_four
from src.python.fodg import fodg_page_count_times_four, fodg_total_shape_count_times_four
from src.python.gnumeric import gnumeric_file_size_times_four, gnumeric_total_row_count_times_four


# --- XCF ---
class TestXcfFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(xcf_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_file_size_times_four(p) > 0


class TestXcfImageTypeIdTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(xcf_image_type_id_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_image_type_id_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert xcf_image_type_id_times_four(p) % 4 == 0


# --- ZST ---
class TestZstFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(zst_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_file_size_times_four(p) > 0


class TestZstDecompressedSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert isinstance(zst_decompressed_size_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_decompressed_size_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "zst" / "valid" / "text-compressed.zst")
        assert zst_decompressed_size_times_four(p) % 4 == 0


# --- TOML ---
class TestTomlFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert isinstance(toml_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_file_size_times_four(p) > 0


class TestTomlStringValueCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert isinstance(toml_string_value_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_string_value_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "toml" / "minimal.toml")
        assert toml_string_value_count_times_four(p) % 4 == 0


# --- FODG ---
class TestFodgPageCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert isinstance(fodg_page_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_page_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_page_count_times_four(p) % 4 == 0


class TestFodgTotalShapeCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert isinstance(fodg_total_shape_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_total_shape_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "fodg" / "minimal-drawing.fodg")
        assert fodg_total_shape_count_times_four(p) % 4 == 0


# --- Gnumeric ---
class TestGnumericFileSizeTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert isinstance(gnumeric_file_size_times_four(p), int)

    def test_equals_four_times_size(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_file_size_times_four(p) == os.path.getsize(p) * 4

    def test_positive(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_file_size_times_four(p) > 0


class TestGnumericTotalRowCountTimesFour:
    def test_returns_int(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert isinstance(gnumeric_total_row_count_times_four(p), int)

    def test_non_negative(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_total_row_count_times_four(p) >= 0

    def test_divisible_by_four(self):
        p = str(SAMPLES / "gnumeric" / "minimal-spreadsheet.gnumeric")
        assert gnumeric_total_row_count_times_four(p) % 4 == 0
